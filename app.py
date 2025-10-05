from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def query_db(query, params=()):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

@app.route("/")
def index():
    avisos = query_db("SELECT nombre, fecha, texto FROM avisos ORDER BY fecha DESC LIMIT 50")
    return render_template("index.html", avisos=avisos)

@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    resultados = []
    if request.method == "POST":
        nombre = request.form.get("nombre")
        resultados = query_db("SELECT nombre, fecha, texto FROM avisos WHERE nombre LIKE ?", [f"%{nombre}%"])
    return render_template("search.html", resultados=resultados)

if __name__ == "__main__":
    app.run(debug=True)
