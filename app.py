from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # tabela de resenhas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                texto TEXT
            )
        """)

        # tabela de visitas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
    except:
        pass

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    # CONTADOR DE VISITAS (com proteção)
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO visits DEFAULT VALUES")
        conn.commit()
        cur.close()
        conn.close()
    except:
        pass

    if request.method == "POST":
        texto = request.form.get("texto")

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO reviews (texto) VALUES (%s)", (texto,))
            conn.commit()
            cur.close()
            conn.close()
        except:
            pass

        return redirect("/")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT texto FROM reviews")
        reviews = cur.fetchall()
        cur.close()
        conn.close()
    except:
        reviews = []

    return render_template("index.html", reviews=reviews)


@app.route("/admin")
def admin():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM visits")
        visitas = cur.fetchone()[0]

        cur.execute("SELECT texto FROM reviews")
        reviews = cur.fetchall()

        cur.close()
        conn.close()
    except:
        visitas = 0
        reviews = []

    return render_template("admin.html", visitas=visitas, reviews=reviews)

@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

@app.route("/termos")
def termos():
    return render_template("termos.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")
if __name__ == "__main__":
    app.run()
