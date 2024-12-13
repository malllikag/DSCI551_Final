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
