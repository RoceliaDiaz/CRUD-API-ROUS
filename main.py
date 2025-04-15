from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Buckingham Boutique POS API",
    description="API para gestionar la venta de guayaberas en la boutique Buckingham.",
    version="1.0.0"
)
@app.get("/")
def inicio():
    return{"mensaje:" "Bienvenido a la API Pos de Buckingham Boutique"}
# --------------------------
# MODELOS DE DATOS
# --------------------------

class Producto(BaseModel):
    id: int
    nombre: str
    descripcion: str
    talla: str
    color: str
    precio: float
    stock: int

class Cliente(BaseModel):
    id: int
    nombre: str
    correo: str
    telefono: str

class Venta(BaseModel):
    id: int
    cliente_id: int
    producto_id: int
    cantidad: int
    total: Optional[float] = None

# --------------------------
# BASE DE DATOS EN MEMORIA
# --------------------------

productos_db = [
    Producto(id=1, nombre="Guayabera Clásica", descripcion="Guayabera blanca bordada", talla="M", color="Blanco", precio=850.00, stock=15),
    Producto(id=2, nombre="Guayabera Premium", descripcion="Lino de alta calidad", talla="L", color="Beige", precio=1299.00, stock=5),
    Producto(id=3, nombre="Guayabera Casual", descripcion="Diseño moderno para uso diario", talla="S", color="Azul", precio=699.00, stock=10)
]

clientes_db = [
    Cliente(id=1, nombre="Juan Pérez", correo="juanperez@email.com", telefono="9611234567"),
    Cliente(id=2, nombre="Carlos Mendoza", correo="carlosm@email.com", telefono="9619876543")
]

ventas_db = []

# --------------------------
# ENDPOINTS PRODUCTOS
# --------------------------

@app.get("/productos/", response_model=List[Producto], tags=["Productos"])
def listar_productos():
    return productos_db

@app.post("/productos/", response_model=Producto, tags=["Productos"])
def agregar_producto(producto: Producto):
    productos_db.append(producto)
    return producto

@app.get("/productos/{producto_id}", response_model=Producto, tags=["Productos"])
def obtener_producto(producto_id: int):
    for producto in productos_db:
        if producto.id == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(producto_id: int):
    global productos_db
    productos_db = [p for p in productos_db if p.id != producto_id]
    return {"mensaje": "Producto eliminado exitosamente"}

# --------------------------
# ENDPOINTS CLIENTES
# --------------------------

@app.get("/clientes/", response_model=List[Cliente], tags=["Clientes"])
def listar_clientes():
    return clientes_db

@app.post("/clientes/", response_model=Cliente, tags=["Clientes"])
def agregar_cliente(cliente: Cliente):
    clientes_db.append(cliente)
    return cliente

# --------------------------
# ENDPOINTS VENTAS
# --------------------------

@app.get("/ventas/", response_model=List[Venta], tags=["Ventas"])
def listar_ventas():
    return ventas_db

@app.post("/ventas/", response_model=Venta, tags=["Ventas"])
def registrar_venta(venta: Venta):
    producto = next((p for p in productos_db if p.id == venta.producto_id), None)
    cliente = next((c for c in clientes_db if c.id == venta.cliente_id), None)

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if producto.stock < venta.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    producto.stock -= venta.cantidad
    venta.total = round(producto.precio * venta.cantidad, 2)
    ventas_db.append(venta)
    return venta