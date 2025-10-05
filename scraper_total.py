import requests
from bs4 import BeautifulSoup
import sqlite3

DB_PATH = "database.db"
BASE_URL = "https://elrosalenio.com.ar/necrologicas.php?_pagi_pg={}"

def crear_tabla():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        edad INTEGER,
        fecha TEXT,
        calle TEXT,
        localidad TEXT,
        texto TEXT,
        UNIQUE(nombre, fecha, localidad)
    )
    """)
    conn.commit()
    conn.close()

def guardar_aviso(nombre, edad, fecha, calle, localidad, texto):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO avisos (nombre, edad, fecha, calle, localidad, texto)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, edad, fecha, calle, localidad, texto))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def extraer_avisos():
    nuevos = 0
    for pagina in range(1, 330):
        url = BASE_URL.format(pagina)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        tabla = soup.find("table")
        if not tabla:
            continue
        filas = tabla.find_all("tr")[1:]

        for fila in filas:
            celdas = fila.find_all("td")
            if len(celdas) < 4:
                continue

            fecha = celdas[0].get_text(strip=True)
            edad = celdas[1].get_text(strip=True)
            nombre = celdas[2].get_text(strip=True)
            domicilio = celdas[3].get_text(strip=True)

            edad = int(edad) if edad.isdigit() else None

            if "," in domicilio:
                partes = domicilio.split(",", 1)
                calle = partes[0].strip()
                localidad = partes[1].strip()
            else:
                calle = domicilio
                localidad = ""

            texto = f"Falleció el {fecha} a los {edad} años. Domicilio: {domicilio}"

            if guardar_aviso(nombre, edad, fecha, calle, localidad, texto):
                nuevos += 1

        print(f"Página {pagina} procesada.")

    print(f"Total de avisos nuevos insertados: {nuevos}")

def main():
    crear_tabla()
    extraer_avisos()

if __name__ == "__main__":
    main()

