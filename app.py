from flask import Flask, render_template, request, redirect, make_response
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

print("BANCO USADO:", DATABASE_URL)


def get_connection():
    try:
        return psycopg2.connect(
            DATABASE_URL,
            sslmode="require",
            connect_timeout=5
        )
    except Exception as e:
        print("ERRO AO CONECTAR NO BANCO:", e)
        return None


def init_db():
    conn = get_connection()
    if conn is None:
        return

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                texto TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY
            )
        """)

        conn.commit()
        cur.close()
       
