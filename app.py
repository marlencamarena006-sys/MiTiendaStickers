from flask import Flask, render_template, request, redirect, url_for, flash, session
from tienda_db import BaseDatosTienda

app = Flask(__name__)
app.secret_key = "clave_secreta_sticker_shop" # Clave para que funcionen las sesiones
db = BaseDatosTienda()
db.semilla_productos()

@app.route("/")
def index():
    # Inicializar el carrito en la sesión si no existe
    if 'carrito' not in session:
        session['carrito'] = []
    
    productos = db.listar_productos()
    return render_template("index.html", productos=productos)

# --- RUTAS DE USUARIO (Apartado 1) ---

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
            session["rol"] = usuario["rol"]
            
            if usuario["rol"] == "admin":
                return redirect(url_for("admin_agregar"))
            return redirect(url_for("index"))
            
        flash("Usuario o contraseña incorrectos.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- LÓGICA DEL CARRITO (Apartado 1) ---

@app.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    producto_id = request.form.get("producto_id")
    carrito = session.get('carrito', [])
    carrito.append(producto_id)
    session['carrito'] = carrito
    session.modified = True 
    
    flash("Producto añadido al carrito.")
    return redirect(url_for("index"))

@app.route("/carrito")
def ver_carrito():
    ids_en_carrito = session.get('carrito', [])
    productos_en_carrito = []
    total = 0
    
    # Obtenemos info real de la BD
    todos = db.listar_productos()
    for p_id in ids_en_carrito:
        for p in todos:
            # Forzamos la comparación de IDs como strings
            if str(p['id']) == str(p_id):
                productos_en_carrito.append(p)
                total += p['precio']
    
    return render_template("carrito.html", items=productos_en_carrito, total=total)

@app.route("/carrito/quitar", methods=["POST"])
def carrito_quitar():
    producto_id = request.form.get("producto_id")
    carrito = session.get('carrito', [])
    
    if str(producto_id) in [str(i) for i in carrito]:
        # Quitamos solo uno de la lista
        for item in carrito:
            if str(item) == str(producto_id):
                carrito.remove(item)
                break
        session['carrito'] = carrito
        session.modified = True
        flash("Producto eliminado del carrito.")
        
    return redirect(url_for("ver_carrito"))

@app.route("/carrito/finalizar", methods=["POST"])
def finalizar_compra():
    if "user_id" not in session:
        flash("Debes iniciar sesión para comprar.")
        return redirect(url_for("login"))
    
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for("index"))

    # Cálculo del total real
    total_compra = 0
    todos = db.listar_productos()
    for p_id in carrito:
        for p in todos:
            if str(p['id']) == str(p_id):
                total_compra += p['precio']
    
    # Baja de stock y creación de pedido (Automatización)
    pedido_id = db.crear_pedido(session["user_id"], total_compra)
    
    for p_id in carrito:
        db.descontar_stock(p_id, 1)
    
    session['carrito'] = []
    session.modified = True
    
    return render_template("checkout_ok.html", pedido_id=pedido_id)

# --- RUTAS DE ADMIN (Apartado 2) ---

@app.route("/admin/agregar", methods=["GET", "POST"])
def admin_agregar():
    if session.get("rol") != "admin":
        flash("Acceso denegado.")
        return redirect(url_for("login"))
        
    if request.method == "POST":
        nombre = request.form.get("nombre")
        desc = request.form.get("descripcion")
        precio = float(request.form.get("precio"))
        stock = int(request.form.get("stock"))
        db.crear_producto(nombre, desc, precio, stock)
        flash("¡Producto guardado exitosamente!")
        return redirect(url_for("index"))
    return render_template("admin_form.html")

if __name__ == "__main__":
    app.run(debug=True)