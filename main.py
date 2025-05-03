import gradio as gr
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_groq import ChatGroq
import sqlite3
import psycopg2
import mysql
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Function to handle DB connection separately
def execute_query(db_url, user_question, db_type):
    try:
        # Load database
        db = SQLDatabase.from_uri(db_url)

        # Load LLM
        llm = ChatGroq(
            model_name="llama3-8b-8192",
            temperature=0.0
        )

        # Create chain
        chain = create_sql_query_chain(llm, db)
        response = chain.invoke({"question": user_question})

        # Extract SQL Query using regex
        match = re.search(r'SQLQuery:\s*(SELECT .*?)$', response, re.DOTALL | re.IGNORECASE)
        if not match:
            return "No valid SQL query found.", None, None

        sql_query = match.group(1).strip()

        # Connect to database and run query
        if db_type.lower() == "sqlite":
            raw_path = db_url.split("sqlite:///")[-1]
            conn = sqlite3.connect(raw_path)
        elif db_type.lower() == "postgresql":
            parts = db_url.split("//")[1].split("@")
            user_pass, host_db = parts
            user, password = user_pass.split(":")
            host, dbname = host_db.split("/")
            host, port = host.split(":") if ":" in host else (host, 5432)
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        elif db_type.lower() == "mysql":
            parts = db_url.split("//")[1].split("@")
            user_pass, host_db = parts
            user, password = user_pass.split(":")
            host, dbname = host_db.split("/")
            host, port = host.split(":") if ":" in host else (host, 3306)
            conn = mysql.connector.connect(
                database=dbname,
                user=user,
                password=password,
                host=host,
                port=int(port)
            )
        else:
            return f"Unsupported database type: {db_type}", None, None

        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        # Prepare results for display
        results = [dict(zip(column_names, row)) for row in rows] if rows else []
        return response, sql_query, results if results else "No results found."

    except Exception as e:
        return f"Error: {str(e)}", None, None

# Gradio UI
def main(db_url, db_type, user_question):
    response, sql_query, results = execute_query(db_url, user_question, db_type)
    return response, sql_query, results

with gr.Blocks() as app:
    gr.Markdown("# Natural Language to SQL Generator")
    gr.Markdown("Enter your Database URL and ask your question!")

    with gr.Row():
        db_url = gr.Textbox(label="Database URL", placeholder="sqlite:///path_to_db.sqlite")
        db_type = gr.Dropdown(["sqlite", "postgresql", "mysql"], value="sqlite", label="Database Type")

    user_question = gr.Textbox(label="Your Question", placeholder="e.g., Show all users who signed up in 2023")

    btn = gr.Button("Generate and Execute SQL")

    with gr.Row():
        response_output = gr.Code(label="LLM Generated SQL Query", language="sql")
        sql_query_output = gr.Textbox(label="Extracted SQL Query")
    
    results_output = gr.JSON(label="Query Results")

    btn.click(fn=main, inputs=[db_url, db_type, user_question], outputs=[response_output, sql_query_output, results_output])

app.launch()
