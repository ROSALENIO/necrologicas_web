from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM obituaries ORDER BY fecha DESC').fetchall()
    conn.close()
    return render_template('index.html', rows=rows)

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
