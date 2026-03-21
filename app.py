from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            texto TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        texto = request.form.get("texto")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO reviews (texto) VALUES (%s)", (texto,))
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT texto FROM reviews")
    reviews = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", reviews=reviews)

if __name__ == "__main__":
    app.run()