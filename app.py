from flask import Flask, render_template, request, redirect, url_for, flash
from tienda_db import BaseDatosTienda

app = Flask(__name__)
app.secret_key = "clave_secreta_sticker_shop"
db = BaseDatosTienda()
db.semilla_productos()

@app.route("/")
def index():
    productos = db.listar_productos()
    return render_template("index.html", productos=productos)

@app.route("/admin/agregar", methods=["GET", "POST"])
def admin_agregar():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        desc = request.form.get("descripcion")
        precio = request.form.get("precio")
        stock = request.form.get("stock")
        db.crear_producto(nombre, desc, precio, stock)
        flash("¡Producto guardado exitosamente!")
        return redirect(url_for("index"))
    return render_template("admin_form.html")

@app.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    flash("Agregado al carrito correctamente")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)