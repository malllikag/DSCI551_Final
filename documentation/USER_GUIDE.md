# User Guide

## Introduction
ChatDB allows you to interact with a Neo4j database to learn and practice querying. You can explore schemas, run natural language queries, and generate sample queries from predefined patterns.

## System Requirements
- A modern web browser (Chrome, Firefox)
- Neo4j database running and populated with the Crime dataset
- Python environment with required packages (`REQUIREMENTS.txt`)

## Installation and Setup
1. `pip install -r REQUIREMENTS.txt`
2. Start the server: `python app.py`
3. In your browser, go to `http://localhost:5001`.

## Selecting a Database
At the top of the interface, select `chicagocrimedb` from the dropdown and click "Set Database".

## Explore the Database
Click "Explore Database" to view the schema and sample data.
![image](https://github.com/user-attachments/assets/20ff5579-e985-4916-9b9c-b25c8607239e)



## Running Queries
Type a query or NL question (e.g., "total crimes by ward") into the input box and press "Send".
![image](https://github.com/user-attachments/assets/a0ec2a0b-19c7-4e0c-b42b-9ac28ab9ddd1)


Examples:
- Natural Language: "find total crimes by ward"
- Keyword-based: "theft"

Results appear below the query box in a table.

## Generating Sample Queries
Choose a construct (e.g. `group_by`, `having`) and click "Generate Sample Queries".
![image](https://github.com/user-attachments/assets/f86aadd2-e25e-4bd2-9a37-b01de5f71550)



Each query displayed includes a "Run This Query" button. Click to execute and view results.
![image](https://github.com/user-attachments/assets/914d2946-2591-40ef-8b53-9a414575cd42)


## Troubleshooting
- If no results appear, ensure the correct database is selected and data is loaded.
- Check the server terminal for error messages.
- Verify Neo4j is running and accessible.