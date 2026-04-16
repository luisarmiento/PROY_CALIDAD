from fastapi import FastAPI, Depends, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select 
from .database import engine, crear_tablas, obtener_sesion
from .models import Empleado
from pydantic import BaseModel

app = FastAPI(title="Orquestador de Onboarding con BDD")

# Permitir que el index.html se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/empleado/{dni}")
def obtener_empleado_por_dni(dni: str, db: Session = Depends(obtener_sesion)):
    statement = select(Empleado).where(Empleado.dni == dni)
    empleado = db.exec(statement).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

class LoginData(BaseModel):
    usuario: str
    password: str # Por ahora se usa como DNI para trabajadores

@app.post("/login")
async def login(data: LoginData, db: Session = Depends(obtener_sesion)):
    print(f"DEBUG: Intento de login para usuario: {data.usuario}")
    # 1. CASO ADMIN (RRHH)
    if data.usuario == "admin" and data.password == "admin123":
        return {"rol": "ADMIN", "redirect": "index.html"}

    # 2. CASO TRABAJADOR (El usuario sería su nombre y password su DNI)
    statement = select(Empleado).where(Empleado.dni == data.password)
    empleado = db.exec(statement).first()
    
    if empleado:
        return {
            "rol": "TRABAJADOR", 
            "dni": empleado.dni, 
            "redirect": "portal_trabajador.html"
        }
    
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# Al iniciar, creamos las tablas en PostgreSQL si no existen
@app.on_event("startup")
def on_startup():
    crear_tablas()


# Modelo de entrada (lo que viene de la web)
class DatosRRHH(BaseModel):
    nombre: str
    apellido: str
    dni: str
    puesto: str

@app.post("/iniciar-onboarding")
def iniciar_onboarding(datos: DatosRRHH, db: Session = Depends(obtener_sesion)):
    
    # PRIMERA DEFENSA: Buscar si el DNI ya existe
    statement = select(Empleado).where(Empleado.dni == datos.dni)
    empleado_existente = db.exec(statement).first()

    if empleado_existente:
        # Si existe, lanzamos un error 400 (Bad Request)
        raise HTTPException(status_code=400, detail="El DNI ya se encuentra registrado en el sistema.")

    # SEGUNDA DEFENSA: Validar longitud del DNI (Mínimo 8)
    if len(datos.dni) < 8:
        raise HTTPException(status_code=422, detail="El DNI debe tener al menos 8 dígitos.")
    
    correo_generado = f"{datos.nombre.lower()}.{datos.apellido.lower()}@empresa.com"
    nombre_contrato = f"Contrato_Firmar_{datos.dni}.pdf"
    
    accesos = ["Slack", "Portal del Empleado"]
    if "venta" in datos.puesto.lower():
        accesos.append("CRM de Ventas")

    # 2. CREAR EL OBJETO PARA LA BASE DE DATOS
    nuevo_empleado = Empleado(
        nombre=datos.nombre,
        apellido=datos.apellido,
        dni=datos.dni,
        puesto=datos.puesto,
        correo=correo_generado,
        contrato_pdf=nombre_contrato
    )

    # 3. GUARDAR EN POSTGRESQL
    db.add(nuevo_empleado)
    db.commit() # Guardado permanente
    db.refresh(nuevo_empleado) # Obtenemos el ID generado

    return {
        "estado": "Completado",
        "mensaje": f"Empleado {nuevo_empleado.id} guardado con éxito.",
        "resultados": {
            "correo": correo_generado,
            "documento": nombre_contrato,
            "herramientas": accesos
        }
    }

@app.get("/empleados")
def listar_empleados(db: Session = Depends(obtener_sesion)):
    # Traemos todos los registros de PostgreSQL
    return db.exec(select(Empleado)).all()

@app.post("/login")
def login(username: str, dni: str = None):
    # Lógica simple por ahora:
    if username == "admin":
        return {"role": "RRHH", "redirect": "dashboard.html"}
    
    # Si no es admin, buscamos al trabajador por DNI
    # (Esto sirve para que el trabajador entre a ver su contrato)
    return {"role": "TRABAJADOR", "dni": dni, "redirect": "portal_trabajador.html"}



