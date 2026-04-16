from sqlmodel import create_engine, SQLModel, Session
from .models import Empleado # Importamos el plano que acabas de crear

# La dirección exacta del contenedor Docker (Usuario:Contraseña@Lugar:Puerto/NombreBD)
DATABASE_URL = "postgresql://admin:adminpassword@db:5432/rrhh_db"

# El motor que se conecta a la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crea las tablas si no existen cuando arranca el programa
def crear_tablas():
    SQLModel.metadata.create_all(engine)

# Da una "sesión" (un turno) para guardar cosas
def obtener_sesion():
    with Session(engine) as session:
        yield session
