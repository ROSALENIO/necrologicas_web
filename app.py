from flask import Flask, render_template, request
import sqlite3
import unicodedata
import os

app = Flask(__name__)

# Cargar configuración desde .env
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = int(os.getenv("PORT", "5000"))

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8").lower()

@app.route("/", methods=["GET", "POST"])
def buscar():
    resultados = []
    if request.method == "POST":
        termino = request.form.get("termino", "").strip()
        termino_norm = normalizar(termino)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, edad, fecha, calle, localidad, texto
            FROM avisos
            WHERE LOWER(nombre) LIKE ?
            ORDER BY fecha DESC
        """, (f"%{termino_norm}%",))
        resultados = cursor.fetchall()
        conn.close()

    return render_template("search.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=DEBUG, port=PORT)
