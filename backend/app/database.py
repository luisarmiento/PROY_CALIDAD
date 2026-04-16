from sqlmodel import create_engine, SQLModel, Session
from .models import Empleado # Importamos el plano que acabas de crear

# La dirección exacta de tu contenedor Docker (Usuario:Contraseña@Lugar:Puerto/NombreBD)
DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/rrhh_db"

# El motor que se conecta a la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Esta función crea las tablas si no existen cuando arranca el programa
def crear_tablas():
    SQLModel.metadata.create_all(engine)

# Esta función nos da una "sesión" (un turno) para guardar cosas
def obtener_sesion():
    with Session(engine) as session:
        yield session