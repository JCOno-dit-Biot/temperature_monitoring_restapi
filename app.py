import os
from flask import Flask
import psycopg2
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    host = "localhost",
    database= os.getenv("POSTGRES_DB_NAME"),
    user= os.getenv("POSTGRES_USER_NAME"),
    password= os.getenv("POSTGRES_PWD"),
    port = os.getenv("PORT")
)

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello, world!"

