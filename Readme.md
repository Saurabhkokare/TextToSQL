# Natural Language to SQL Generator

This project is a Gradio-based application that converts natural language questions into SQL queries using a language model. It also executes the generated SQL queries on a specified database and displays the results.

## Features

- Converts natural language questions into SQL queries.
- Supports multiple database types: SQLite, PostgreSQL, and MySQL (MySQL support is commented out but can be enabled).
- Executes the generated SQL queries and displays the results in JSON format.
- User-friendly interface built with Gradio.

## Requirements

- Python 3.8 or higher
- Required Python libraries (listed in `requirements.txt`):
  - `gradio`
  - `langchain`
  - `langchain_community`
  - `psycopg2`
  - `sqlite3` (built-in with Python)
  - `python-dotenv`

## Installation

1. Clone the repository:
   ```bash
   