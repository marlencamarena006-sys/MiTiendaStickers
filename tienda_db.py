import os
import sqlite3

class BaseDatosTienda:
    def __init__(self, ruta="./", bd="tienda.sqlite3"):
        self.bd_path = os.path.join(ruta, bd)
        self.con = sqlite3.connect(self.bd_path, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.cursor = self.con.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS productos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL
            );
        """)
        self.con.commit()

    def crear_producto(self, nombre, descripcion, precio, stock):
        try:
            self.cursor.execute("INSERT INTO productos(nombre, descripcion, precio, stock) VALUES(?,?,?,?)",
                                (nombre, descripcion, float(precio), int(stock)))
            self.con.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error: {e}")
            return None

    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos ORDER BY id DESC")
        return self.cursor.fetchall()

    def semilla_productos(self):
        if len(self.listar_productos()) == 0:
            self.crear_producto("Sticker Pack", "Paquete de 10 stickers", 59.0, 47)