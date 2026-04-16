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
        # Tabla de productos (ya la tenías) [cite: 16]
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS productos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL
            );

            -- TABLA DE USUARIOS (Requisito: Perfil de usuario) 
            CREATE TABLE IF NOT EXISTS usuarios(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'cliente'
            );

            -- TABLA DE PEDIDOS (Requisito: Guardar pedido con ID) 
            CREATE TABLE IF NOT EXISTS pedidos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total REAL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            );
        """)
        self.con.commit()

    # --- FUNCIONES PARA TU PARTE (USUARIO) ---

    def registrar_usuario(self, nombre, usuario, password, rol='cliente'):
        try:
            self.cursor.execute("INSERT INTO usuarios(nombre, usuario, password, rol) VALUES(?,?,?,?)",
                               (nombre, usuario, password, rol))
            self.con.commit()
            return True
        except:
            return False

    def validar_usuario(self, usuario, password):
        # Busca si el usuario y contraseña coinciden 
        self.cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
        return self.cursor.fetchone()

    def descontar_stock(self, producto_id, cantidad):
        # BAJA AUTOMÁTICA DE STOCK (Requisito Apartado 1) 
        self.cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto_id))
        self.con.commit()

    def crear_pedido(self, usuario_id, total):
        # GUARDA EL PEDIDO (Requisito Apartado 1) 
        self.cursor.execute("INSERT INTO pedidos(usuario_id, total) VALUES(?,?)", (usuario_id, total))
        self.con.commit()
        return self.cursor.lastrowid

    # --- FUNCIONES DE PRODUCTOS (Ya las tenías) ---
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
        # Asegura los 10 productos por defecto (Requisito Apartado 1) 
        self.cursor.execute("SELECT count(*) as total FROM productos")
        if self.cursor.fetchone()['total'] < 10:
            for i in range(1, 11):
                self.crear_producto(f"Sticker Pack {i}", "Descripción del pack", 50.0, 100)