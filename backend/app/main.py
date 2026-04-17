from fastapi import FastAPI, Depends, HTTPException 
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select 
from .database import engine, crear_tablas, obtener_sesion
from .models import Empleado
from pydantic import BaseModel

app = FastAPI(title="MyOnBoard API - Sistema de Onboarding")

# --- CONFIGURACIÓN CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE ENTRADA (PYDANTIC) ---
class LoginData(BaseModel):
    usuario: str
    password: str

class DatosRRHH(BaseModel):
    nombre: str
    apellido: str
    dni: str
    puesto: str
    password: str

# --- EVENTOS DE SISTEMA ---
@app.on_event("startup")
def on_startup():
    crear_tablas()
    # Semilla de Administrador 
    with Session(engine) as session:
        admin_exists = session.exec(select(Empleado).where(Empleado.correo == "admin@empresa.com")).first()
        if not admin_exists:
            admin_root = Empleado(
                nombre="Daniel",
                apellido="Admin",
                dni="00000000",
                puesto="Jefe de RRHH",
                correo="admin@empresa.com",
                password="admin123",
                role="ADMIN",
                status="ACTIVO",
                contrato_pdf="n/a"
            )
            session.add(admin_root)
            session.commit()
            print("✅ Usuario Administrador inicial creado")

# --- ENDPOINTS DE ACCESO (LOGIN) ---
@app.post("/login")
async def login(data: LoginData, db: Session = Depends(obtener_sesion)):
    statement = select(Empleado).where(Empleado.correo == data.usuario)
    user = db.exec(statement).first()

    if not user:
        raise HTTPException(status_code=401, detail="Correo electrónico no encontrado")

    if user.password != data.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Redirección dinámica basada en rol
    pagina = "index.html" if user.role == "ADMIN" else "portal_trabajador.html"

    return {
        "rol": user.role,
        "dni": user.dni,
        "nombre": user.nombre,
        "apellido": user.apellido, # Agregado para el display del portal
        "redirect": pagina
    }

# --- ENDPOINTS ADMINISTRATIVOS (RRHH) ---
@app.post("/iniciar-onboarding")
def iniciar_onboarding(datos: DatosRRHH, db: Session = Depends(obtener_sesion)):
    # 1. Validar si ya existe
    if db.exec(select(Empleado).where(Empleado.dni == datos.dni)).first():
        raise HTTPException(status_code=400, detail="El DNI ya existe.")

    # 2. Generar Correo
    correo_gen = f"{datos.nombre.lower()}.{datos.apellido.lower()}@empresa.com"
    
    # 3. Guardar en BDD
    nuevo = Empleado(
        nombre=datos.nombre,
        apellido=datos.apellido,
        dni=datos.dni,
        puesto=datos.puesto,
        correo=correo_gen,
        password=datos.password,
        role="TRABAJADOR",
        status="PENDIENTE",
        contrato_pdf=f"Contrato_{datos.dni}.pdf"
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {
        "estado": "Completado",
        "resultados": {
            "correo": correo_gen,
            "password_temporal": datos.password
        }
    }

@app.get("/admin/empleados")
def listar_todos(db: Session = Depends(obtener_sesion)):
    return db.exec(select(Empleado)).all()

# --- ENDPOINTS DEL TRABAJADOR ---
@app.get("/trabajador/mi-contrato/{dni}")
def obtener_mi_contrato(dni: str, db: Session = Depends(obtener_sesion)):
    empleado = db.exec(select(Empleado).where(Empleado.dni == dni)).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return empleado