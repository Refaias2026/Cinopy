from flask import Flask, render_template, request, redirect
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

        print("TEXTO RECEBIDO:", texto)

        if texto:
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

    return render_template("index.html", reviews=reviews)


@app.route("/admin")
def admin():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT texto FROM reviews ORDER BY id DESC")
            reviews = cur.fetchall()
            cur.close()
            conn.close()

            return "<br>".join([r[0] for r in reviews]) or "SEM RESENHAS"
        except Exception as e:
            print("ERRO NO ADMIN:", e)

    return "ERRO AO CARREGAR"


if __name__ == "__main__":
    app.run()
