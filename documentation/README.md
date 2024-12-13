# DSCI551_Final
ChatDB: A Neo4j-backed web app for learning database querying. Explore database schemas, generate sample queries, and run natural language queries.

# ChatDB - Learning to Query Database Systems

ChatDB is an interactive application that helps users learn to query a Neo4j database through a chat-like interface. Users can explore the database schema, generate pattern-based sample queries (with constructs like GROUP BY and HAVING), and ask natural language questions to retrieve data.

## Key Features
- Explore database schemas and view sample data
- Generate sample queries using patterns (total <A> by <B>, group_by, having)
- Support natural language queries (e.g., "find total crimes by ward")
- Execute queries directly and display results

## Quick Start
1. Ensure you have Python 3.8+ installed.
2. Ensure Neo4j is installed, running, and the dataset is loaded.
3. Install dependencies: `pip install -r REQUIREMENTS.txt`
4. Start the Flask app: `python app.py`
5. Open `http://localhost:5001` in your browser.

## Further Documentation
- [USER_GUIDE.md](USER_GUIDE.md): Detailed usage instructions.
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md): Code structure, architecture, and extension details.

## Data Setup
The Chicago Crime dataset was cleaned using `data_cleaning.ipynb`. After cleaning, `cleaned_data.csv` was imported into Neo4j. The notebook contains all steps and can be reviewed for data preparation details.