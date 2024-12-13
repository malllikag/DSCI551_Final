import os
import logging
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from neo4j import GraphDatabase
from dotenv import load_dotenv
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import re
import random

load_dotenv()

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Brzfks1229812")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "chicagocrimedb")

query_patterns = [
    {
        "description": "Find total <A> by <B>",
        "template": """
            MATCH (n:Crime)
            WITH n.{B} AS category, {A}(*) AS total
            RETURN category AS {B}, total
            ORDER BY total DESC
            LIMIT 10
        """,
        "A_choices": ["COUNT"],
        "B_choices": ["ward", "primary_description"]
    },
    {
        "description": "Show the top N crimes",
        "template": """
            MATCH (n:Crime)
            RETURN toString(n.date_of_occurrence) AS date_of_occurrence,
                   n.primary_description AS primary_description,
                   n.secondary_description AS secondary_description,
                   n.ward AS ward,
                   n.arrest AS arrest,
                   n.domestic AS domestic
            LIMIT {N}
        """,
        "N_choices": [5, 10, 20]
    },
    {
        "description": "Show M most recent crimes",
        "template": """
            MATCH (n:Crime)
            RETURN toString(n.date_of_occurrence) AS date_of_occurrence,
                   n.primary_description AS primary_description,
                   n.secondary_description AS secondary_description,
                   n.ward AS ward,
                   n.arrest AS arrest,
                   n.domestic AS domestic
            ORDER BY n.date_of_occurrence DESC
            LIMIT {M}
        """,
        "M_choices": [5, 10]
    },
    {
        "description": "Find total <A> by <B> having total > X",
        "template": """
            MATCH (n:Crime)
            WITH n.{B} AS category, {A}(*) AS total
            WHERE total > {X}
            RETURN category AS {B}, total
            ORDER BY total DESC
            LIMIT 10
        """,
        "A_choices": ["COUNT"],
        "B_choices": ["ward", "primary_description"],
        "X_choices": [10, 20, 50]
    },
    {
        "description": "Find sum of <A> by <B>",
        "template": """
            MATCH (n:Crime)
            // Assuming n.some_numeric_field is numeric
            WITH n.{B} AS category, SUM(n.some_numeric_field) AS total
            RETURN category AS {B}, total
            ORDER BY total DESC
            LIMIT 10
        """,
        #This pattern uses SUM directly; no choices for A.
        "B_choices": ["ward", "primary_description"]
    }
]

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session(database=NEO4J_DATABASE) as session:
        session.run("RETURN 1")
    logger.info(f"Connected to Neo4j database '{NEO4J_DATABASE}'.")
except Exception as e:
    logger.error(f"Error connecting to Neo4j: {str(e)}")
    driver = None

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " ").lower())
    return list(synonyms)

def expand_keywords(keywords):
    expanded = set(keywords)
    for keyword in keywords:
        expanded.update(get_synonyms(keyword))
    return list(expanded)

def extract_keywords(user_input):
    tokens = word_tokenize(user_input.lower())
    tagged = pos_tag(tokens)
    # Extract nouns, verbs, and adjectives
    keywords = [w for w, t in tagged if t.startswith(("NN", "VB", "JJ"))]
    return expand_keywords(keywords)

def match_nl_pattern(user_input):
    pattern = r"total\s+(\w+)\s+by\s+(\w+)"
    match = re.search(pattern, user_input.lower())
    if match:
        A = match.group(1)
        B = match.group(2)
        query = f"""
            MATCH (c:Crime)
            WITH c.{B} AS category, COUNT(c) AS total
            RETURN category AS {B}, total
            ORDER BY total DESC
            LIMIT 10
        """
        return query
    return None

def execute_cypher_query(query, parameters=None):
    if not driver:
        raise Exception("Neo4j driver is not initialized.")
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(query, parameters or {})
        data = []
        for record in result:
            row_data = {}
            for key in record.keys():
                val = record[key]
                # Since we're converting date_of_occurrence to string in Cypher, it should be a string now.
                if val is None:
                    val = "N/A"
                if key in ["arrest", "domestic"] and isinstance(val, bool):
                    val = "Yes" if val else "No"
                row_data[key] = val
            data.append(row_data)
        return data

@app.route("/explore_database", methods=["GET"])
def explore_database():
    try:
        nodes = [{
            "label": "Crime",
            "properties": [
                'date_of_occurrence', 'primary_description', 'secondary_description', 'arrest',
                'domestic', 'beat', 'ward', 'x_coordinate', 'y_coordinate', 'latitude', 'longitude'
            ]
        }]

        # Convert date_of_occurrence to string in Cypher to avoid Date type issues.
        sample_query = """
            MATCH (c:Crime)
            RETURN toString(c.date_of_occurrence) AS date_of_occurrence,
                   c.primary_description AS primary_description,
                   c.secondary_description AS secondary_description,
                   c.arrest AS arrest,
                   c.domestic AS domestic,
                   c.beat AS beat,
                   c.ward AS ward,
                   c.x_coordinate AS x_coordinate,
                   c.y_coordinate AS y_coordinate,
                   c.latitude AS latitude,
                   c.longitude AS longitude
            LIMIT 5
        """
        samples = execute_cypher_query(sample_query)
        return jsonify({"nodes": nodes, "samples": samples, "message": "Database schema and samples retrieved successfully."})
    except Exception as e:
        logger.error(f"Error in /explore_database: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/execute_query", methods=["POST"])
def execute_query_route():
    try:
        user_input = request.json.get("query", "").strip()
        if not user_input:
            return jsonify({"error": "No query provided."}), 400

        keywords = extract_keywords(user_input)
        if keywords:
            # Build conditions
            params = {}
            conditions = []
            for i, kw in enumerate(keywords):
                conditions.append(f"(toLower(c.primary_description) CONTAINS $kw{i} OR toLower(c.secondary_description) CONTAINS $kw{i})")
                params[f"kw{i}"] = kw
            condition_str = " OR ".join(conditions)
            query = f"""
                MATCH (c:Crime)
                WHERE {condition_str}
                RETURN toString(c.date_of_occurrence) AS date_of_occurrence,
                       c.primary_description AS primary_description,
                       c.secondary_description AS secondary_description,
                       c.ward AS ward,
                       c.arrest AS arrest,
                       c.domestic AS domestic
                LIMIT 20
            """
            results = execute_cypher_query(query, params)
            if not results:
                # fallback if no results
                fallback_query = """
                    MATCH (c:Crime)
                    RETURN toString(c.date_of_occurrence) AS date_of_occurrence,
                           c.primary_description AS primary_description,
                           c.secondary_description AS secondary_description,
                           c.ward AS ward,
                           c.arrest AS arrest,
                           c.domestic AS domestic
                    LIMIT 20
                """
                results = execute_cypher_query(fallback_query)
        else:
            # No keywords, just show top 20 crimes
            fallback_query = """
                MATCH (c:Crime)
                RETURN toString(c.date_of_occurrence) AS date_of_occurrence,
                       c.primary_description AS primary_description,
                       c.secondary_description AS secondary_description,
                       c.ward AS ward,
                       c.arrest AS arrest,
                       c.domestic AS domestic
                LIMIT 20
            """
            results = execute_cypher_query(fallback_query)

        return jsonify({"message": "Query executed successfully.", "results": results})
    except Exception as e:
        logger.error(f"Error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate_sample_queries/<node_label>", methods=["GET"])
def generate_sample_queries(node_label):
    try:
        construct = request.args.get("construct", None)

        # Filter patterns if construct specified
        filtered_patterns = query_patterns
        if construct == "group_by":
            filtered_patterns = [p for p in query_patterns if "WITH n.{B}" in p["template"]]

        if not filtered_patterns:
            filtered_patterns = query_patterns

        selected_patterns = random.sample(filtered_patterns, min(3, len(filtered_patterns)))
        queries = []
        for p in selected_patterns:
            q = p["template"]
            nl_desc = p["description"]

            if "A_choices" in p and "{A}" in q:
                A = random.choice(p["A_choices"])
                q = q.replace("{A}", A)
                nl_desc = nl_desc.replace("<A>", "count") # or "A"
            if "B_choices" in p and "{B}" in q:
                B = random.choice(p["B_choices"])
                q = q.replace("{B}", B)
                nl_desc = nl_desc.replace("<B>", B)

            if "N_choices" in p and "{N}" in q:
                N = random.choice(p["N_choices"])
                q = q.replace("{N}", str(N))
                nl_desc = nl_desc.replace("N", str(N))

            if "M_choices" in p and "{M}" in q:
                M = random.choice(p["M_choices"])
                q = q.replace("{M}", str(M))
                nl_desc = nl_desc.replace("M", str(M))

            q = q.strip()

            queries.append({
                "natural_language": nl_desc,
                "query": q
            })

        return jsonify({"message": "Sample queries generated successfully.", "queries": queries})
    except Exception as e:
        logger.error(f"Error generating queries: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/list_databases", methods=["GET"])
def list_databases():
    # Returns a list of available databases
    dbs = ["chicagocrimedb", "neo4j", "system"]
    return jsonify({"databases": dbs})

@app.route("/set_database", methods=["POST"])
def set_database():
    global CURRENT_DATABASE
    db_name = request.json.get("database", "").strip()
    if not db_name:
        return jsonify({"error": "No database name provided."}), 400
    try:
        with driver.session(database=db_name) as session:
            session.run("RETURN 1")
        CURRENT_DATABASE = db_name
        logger.info(f"Switched to database '{db_name}'.")
        return jsonify({"message": f"Switched to database '{db_name}' successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/run_query", methods=["POST"])
def run_query():
    try:
        q = request.json.get("query", "").strip()
        if not q:
            return jsonify({"error": "No query provided."}), 400
        results = execute_cypher_query(q)
        return jsonify({"message": "Query executed successfully.", "results": results})
    except Exception as e:
        logger.error(f"Error running query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
