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
            CREATE TABLE IF NOT EXISTS productos(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, descripcion TEXT, precio REAL, stock INTEGER, imagen TEXT DEFAULT 'default.png');
            CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, usuario TEXT UNIQUE, password TEXT, rol TEXT DEFAULT 'cliente');
            CREATE TABLE IF NOT EXISTS pedidos(id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total REAL, estado TEXT DEFAULT 'Pendiente');
            CREATE TABLE IF NOT EXISTS avisos(id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        """)
        self.con.commit()

    # --- USUARIOS ---
    def registrar_usuario(self, nombre, usuario, password, rol='cliente'):
        try:
            self.cursor.execute("INSERT INTO usuarios(nombre, usuario, password, rol) VALUES(?,?,?,?)", (nombre, usuario, password, rol))
            self.con.commit()
            return True
        except:
            return False

    def validar_usuario(self, usuario, password):
        self.cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
        return self.cursor.fetchone()

    # --- PRODUCTOS ---
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos ORDER BY id DESC")
        return self.cursor.fetchall()

    def crear_producto(self, nombre, descripcion, precio, stock, imagen):
        self.cursor.execute("INSERT INTO productos (nombre, descripcion, precio, stock, imagen) VALUES (?, ?, ?, ?, ?)", 
                           (nombre, descripcion, precio, stock, imagen))
        self.con.commit()

    def actualizar_producto(self, id, nombre, descripcion, precio, stock, imagen):
        self.cursor.execute("UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=?, imagen=? WHERE id=?", 
                           (nombre, descripcion, precio, stock, imagen, id))
        self.con.commit()

    def eliminar_producto(self, id):
        self.cursor.execute("DELETE FROM productos WHERE id=?", (id,))
        self.con.commit()

    def descontar_stock(self, producto_id, cantidad):
        self.cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto_id))
        self.con.commit()

    # --- PEDIDOS Y REPORTES ---
    def crear_pedido(self, usuario_id, total):
        self.cursor.execute("INSERT INTO pedidos(usuario_id, total) VALUES(?,?)", (usuario_id, total))
        self.con.commit()
        return self.cursor.lastrowid

    def ver_todos_los_pedidos(self):
        self.cursor.execute("""
            SELECT p.id, u.nombre as cliente, p.fecha, p.total, p.estado 
            FROM pedidos p 
            JOIN usuarios u ON p.usuario_id = u.id 
            ORDER BY p.fecha DESC
        """)
        return self.cursor.fetchall()

    def actualizar_estado_pedido(self, pedido_id, nuevo_estado):
        self.cursor.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (nuevo_estado, pedido_id))
        self.con.commit()

    def reporte_ventas_diarias(self):
        self.cursor.execute("SELECT date(fecha) as dia, SUM(total) as total_dia FROM pedidos GROUP BY dia ORDER BY dia DESC")
        return self.cursor.fetchall()

    # --- AVISOS ---
    def obtener_avisos(self):
        self.cursor.execute("SELECT * FROM avisos ORDER BY fecha DESC LIMIT 3")
        return self.cursor.fetchall()

    def agregar_aviso(self, mensaje):
        self.cursor.execute("INSERT INTO avisos (mensaje) VALUES (?)", (mensaje,))
        self.con.commit()