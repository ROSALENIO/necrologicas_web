from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    if request.method == 'POST':
        nombre = request.form['nombre']
        conn = get_db_connection()
        query = "SELECT * FROM obituaries WHERE nombre LIKE ? ORDER BY fecha DESC"
        resultados = conn.execute(query, ('%' + nombre + '%',)).fetchall()
        conn.close()
    return render_template('search.html', resultados=resultados)

@app.route('/')
def home():
    return render_template('search.html', resultados=[])
