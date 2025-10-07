import requests
from bs4 import BeautifulSoup
import sqlite3
import unicodedata
import time
from datetime import datetime, timedelta

URL = "https://www.rosalenio.com.ar/necrologicas"
HORARIOS = ["00:00", "06:00", "12:00", "18:00"]

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8").lower()

def obtener_html():
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log_ejecucion(f"⚠️ Error al obtener HTML: {e}")
        return ""

def parsear_avisos(html):
    soup = BeautifulSoup(html, "html.parser")
    avisos = []

    bloques = soup.find_all("div", class_="necrologica")  # Ajustar según HTML real

    for b in bloques:
        nombre = b.find("h3").get_text(strip=True) if b.find("h3") else ""
        texto = b.find("p").get_text(strip=True) if b.find("p") else ""
        fecha = b.find("span", class_="fecha").get_text(strip=True) if b.find("span", class_="fecha") else ""

        avisos.append({
            "nombre": nombre,
            "edad": "",
            "fecha": fecha,
            "calle": "",
            "localidad": "",
            "texto": texto
        })

    return avisos

def guardar_en_db(avisos):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            edad TEXT,
            fecha TEXT,
            calle TEXT,
            localidad TEXT,
            texto TEXT
        )
    """)

    nuevos = 0
    for a in avisos:
        nombre_norm = normalizar(a["nombre"])
        cursor.execute("SELECT COUNT(*) FROM avisos WHERE LOWER(nombre) = ?", (nombre_norm,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO avisos (nombre, edad, fecha, calle, localidad, texto)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (a["nombre"], a["edad"], a["fecha"], a["calle"], a["localidad"], a["texto"]))
            nuevos += 1

    conn.commit()
    conn.close()
    log_ejecucion(f"✅ {nuevos} avisos nuevos guardados.")

def esperar_hasta_proximo_horario():
    ahora = datetime.now()
    proximos = []

    for h in HORARIOS:
        hora, minuto = map(int, h.split(":"))
        objetivo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if objetivo <= ahora:
            objetivo += timedelta(days=1)
        proximos.append(objetivo)

    siguiente = min(proximos)
    espera = (siguiente - ahora).total_seconds()
    log_ejecucion(f"🕒 Próximo scraping a las {siguiente.strftime('%H:%M')}. Esperando {int(espera // 60)} minutos...")
    time.sleep(espera)

def log_ejecucion(mensaje):
    with open("scraper.log", "a", encoding="utf-8") as f:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ahora}] {mensaje}\n")

if __name__ == "__main__":
    while True:
        esperar_hasta_proximo_horario()
        html = obtener_html()
        if html:
            avisos = parsear_avisos(html)
            guardar_en_db(avisos)
        log_ejecucion("🔁 Esperando al próximo horario...")
