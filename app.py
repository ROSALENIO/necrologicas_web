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
