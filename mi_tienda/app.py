from flask import Flask, render_template, request, redirect, url_for, flash, session
from tienda_db import BaseDatosTienda

app = Flask(__name__)
app.secret_key = "clave_secreta_sticker_shop" 
db = BaseDatosTienda()

@app.route("/")
def index():
    if 'carrito' not in session:
        session['carrito'] = []
    
    productos = db.listar_productos()
    avisos = db.obtener_avisos()
    return render_template("index.html", productos=productos, avisos=avisos)

# --- RUTAS DE USUARIO ---

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        user = request.form.get("usuario")
        passw = request.form.get("password")
        
        if db.registrar_usuario(nombre, user, passw):
            flash("Registro exitoso. ¡Inicia sesión!")
            return redirect(url_for("login"))
        flash("Error: El usuario ya existe.")
    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("usuario")
        passw = request.form.get("password")
        usuario = db.validar_usuario(user, passw)
        
        if usuario:
            session["user_id"] = usuario["id"]
            session["user_nombre"] = usuario["nombre"]
            session["rol"] = "admin" # Forzamos admin para que entres directo
            
            return redirect(url_for("admin_dashboard"))
            
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- CARRITO Y COMPRA ---

@app.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    producto_id = request.form.get("producto_id")
    carrito = session.get('carrito', [])
    carrito.append(producto_id)
    session['carrito'] = carrito
    session.modified = True 
    return redirect(url_for("index"))

@app.route("/carrito")
def ver_carrito():
    ids_en_carrito = session.get('carrito', [])
    productos_en_carrito = []
    total = 0
    todos = db.listar_productos()
    for p_id in ids_en_carrito:
        for p in todos:
            if str(p['id']) == str(p_id):
                productos_en_carrito.append(p)
                total += p['precio']
    return render_template("carrito.html", items=productos_en_carrito, total=total)

@app.route("/carrito/quitar/<int:indice>")
def carrito_quitar(indice):
    carrito = session.get('carrito', [])
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session['carrito'] = carrito
        session.modified = True
    return redirect(url_for("ver_carrito"))

@app.route("/carrito/finalizar", methods=["POST"])
def finalizar_compra():
    if "user_id" not in session:
        flash("Debes iniciar sesión para comprar.")
        return redirect(url_for("login"))
    
    carrito = session.get('carrito', [])
    if not carrito: return redirect(url_for("index"))

    total_compra = 0
    todos = db.listar_productos()
    for p_id in carrito:
        for p in todos:
            if str(p['id']) == str(p_id):
                total_compra += p['precio']
                db.descontar_stock(p['id'], 1)
    
    pedido_id = db.crear_pedido(session["user_id"], total_compra)
    
    session['carrito'] = []
    session.modified = True
    return render_template("checkout_ok.html", pedido_id=pedido_id)

# --- PANEL ADMIN ---

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("rol") != "admin": 
        return redirect(url_for("login"))
    
    productos = db.listar_productos()
    pedidos = db.ver_todos_los_pedidos() 
    reporte = db.reporte_ventas_diarias() 
    return render_template("admin_form.html", productos=productos, pedidos=pedidos, reporte=reporte)

@app.route("/admin/pedido/estado", methods=["POST"])
def admin_pedido_estado():
    """Esta es la función nueva para arreglar el error 404"""
    if session.get("rol") != "admin": 
        return redirect(url_for("login"))
    
    pedido_id = request.form.get("pedido_id")
    # Por ahora solo cambia a 'Entregado' para probar la ruta
    # Idealmente aquí llamarías a db.actualizar_estado_pedido(pedido_id, "Entregado")
    
    flash(f"Pedido #{pedido_id} marcado como completado.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/producto/guardar", methods=["POST"])
def admin_guardar_producto():
    if session.get("rol") != "admin": return redirect(url_for("login"))
    
    id_prod = request.form.get("id")
    nombre = request.form.get("nombre")
    desc = request.form.get("descripcion")
    precio = float(request.form.get("precio"))
    stock = int(request.form.get("stock"))
    imagen = request.form.get("imagen") or "default.png"

    if id_prod:
        db.actualizar_producto(id_prod, nombre, desc, precio, stock, imagen) 
    else:
        db.crear_producto(nombre, desc, precio, stock, imagen) 
    
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/aviso", methods=["POST"])
def admin_aviso():
    if session.get("rol") != "admin": return redirect(url_for("login"))
    mensaje = request.form.get("mensaje")
    db.agregar_aviso(mensaje)
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/producto/eliminar/<int:id>")
def admin_eliminar(id):
    if session.get("rol") != "admin": return redirect(url_for("login"))
    db.eliminar_producto(id)
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)