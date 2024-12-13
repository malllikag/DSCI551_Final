# Developer Guide

## Architecture Overview
- **Frontend**: `index.html` provides a UI using Bootstrap.
- **Backend**: `app.py` (Flask) connects to Neo4j, offers endpoints:
  - `/explore_database`: Shows schema and samples.
  - `/execute_query`: Runs user queries (keyword or NL-based).
  - `/generate_sample_queries/<node_label>`: Returns pattern-based sample queries.
  - `/run_query`: Runs a given query from the sample queries.
  - `/list_databases`, `/set_database`: Manage active database.
  
Neo4j is queried via `execute_cypher_query()` function.

## Data Cleaning Notebook
`data_cleaning.ipynb`:
- Loads raw Chicago Crime dataset
- Cleans and filters invalid records
- Outputs `cleaned_data.csv` for Neo4j import
- Markdown cells inside the notebook explain each step

  ### Neo4j Installation and Configuration

1. **Install Neo4j Desktop**:
   - Download and install Neo4j Desktop from the [official Neo4j website](https://neo4j.com/download/).

2. **Set Up the Database**:
   - Open Neo4j Desktop and create a new database named `chicagocrimedb`.
   - Use the default credentials or set a custom username/password.

3. **Dataset Import**:
   - Place the `chicago_crime_data_cleaned.csv` file into the `import` directory of the Neo4j database.
   - Open the Neo4j browser and execute the following Cypher query to load the dataset:
     ```
     LOAD CSV WITH HEADERS FROM 'file:///chicago_crime_data_cleaned.csv' AS row
     CREATE (c:Crime {
         id: row.id,
         date_of_occurrence: row.date_of_occurrence,
         primary_description: row.primary_description,
         secondary_description: row.secondary_description,
         ward: row.ward,
         arrest: row.arrest,
         domestic: row.domestic,
         latitude: row.latitude,
         longitude: row.longitude
     });
     ```

4. **Verify Database Schema**:
   - Run the following query to ensure the schema is set up:
     ```
     CALL db.schema.visualization();
     ```

5. **Error Handling**:
   - Ensure all files are placed in the correct directory.
   - If the `LOAD CSV` command fails, verify that the `import` directory has proper read/write permissions.

6. **Integration with Flask**:
   - Update the `.env` file in the project to reflect your Neo4j connection details:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your_password
     NEO4J_DATABASE=chicagocrimedb
     ```
   - Restart the Flask server after making changes.

7. **Troubleshooting**:
   - For database-related issues, consult the Neo4j logs located in the `logs` folder of your Neo4j database directory.
   - If the connection fails, verify the Bolt URL and credentials.

## Adding New Patterns
To add a new query pattern (e.g., another aggregation):
- Edit `query_patterns` in `app.py`.
- Include templates with placeholders (e.g., `{A}`, `{B}`, `{X}`).
- Add logic in `/generate_sample_queries` route to substitute placeholders.

## Dependencies
All dependencies listed in `REQUIREMENTS.txt`.
- Flask, Neo4j driver, python-dotenv, nltk, etc.

## Testing and Debugging
- Run `app.py`, open `http://localhost:5001`.
- Try queries and sample queries.
- Check terminal logs for errors.

## Future Extensions
- Add more NL patterns in `match_nl_pattern`.
- Integrate additional constructs or data sources.
