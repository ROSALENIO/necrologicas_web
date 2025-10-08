import httpx
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

URL = "https://elrosalenio.com.ar/necrologicas.php?_pagi_pg=1"
DB_PATH = "database.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

def scrape_and_save():
    try:
        response = httpx.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        avisos = soup.select(".necrologica")
        if not avisos:
            print("⚠️ No se encontraron avisos.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avisos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                fecha TEXT,
                hora TEXT,
                lugar TEXT,
                timestamp TEXT
            )
        """)

        nuevos = 0
        for aviso in avisos:
            nombre = aviso.select_one(".nombre").get_text(strip=True) if aviso.select_one(".nombre") else ""
            fecha = aviso.select_one(".fecha").get_text(strip=True) if aviso.select_one(".fecha") else ""
            hora = aviso.select_one(".hora").get_text(strip=True) if aviso.select_one(".hora") else ""
            lugar = aviso.select_one(".lugar").get_text(strip=True) if aviso.select_one(".lugar") else ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT COUNT(*) FROM avisos
                WHERE nombre = ? AND fecha = ? AND hora = ? AND lugar = ?
            """, (nombre, fecha, hora, lugar))
            existe = cursor.fetchone()[0]

            if not existe:
                cursor.execute("""
                    INSERT INTO avisos (nombre, fecha, hora, lugar, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, fecha, hora, lugar, timestamp))
                nuevos += 1

        conn.commit()
        conn.close()

        print(f"✅ {nuevos} avisos nuevos guardados.")
    except Exception as e:
        print(f"❌ Error en el scraper: {e}")

if __name__ == "__main__":
    scrape_and_save()
    print("🔁 Scraper ejecutado correctamente. Fin del proceso.")
