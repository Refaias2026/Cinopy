from flask import Flask, render_template, request, redirect, make_response
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# 🔥 MOSTRA QUAL BANCO ESTÁ SENDO USADO
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
    if not conn:
        return

    try:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                texto TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("ERRO AO CRIAR TABELAS:", e)


init_db()


@app.route("/", methods=["GET", "POST"])
def home():

    # CONTADOR DE VISITAS
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO visits DEFAULT VALUES")
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("ERRO AO CONTAR VISITAS:", e)

    # NOVA RESENHA
    if request.method == "POST":
        texto = request.form.get("texto")

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO reviews (texto) VALUES (%s)", (texto,))
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print("ERRO AO SALVAR REVIEW:", e)

        return redirect("/")

    # BUSCAR RESENHAS
    reviews = []
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT texto FROM reviews ORDER BY id DESC")
            reviews = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print("ERRO AO BUSCAR REVIEWS:", e)

    response = make_response(render_template("index.html", reviews=reviews))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/admin")
def admin():
    visitas = 0
    reviews = []

    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM visits")
            visitas = cur.fetchone()[0]

            cur.execute("SELECT texto FROM reviews ORDER BY id DESC")
            reviews = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            print("ERRO NO ADMIN:", e)

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


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run()
