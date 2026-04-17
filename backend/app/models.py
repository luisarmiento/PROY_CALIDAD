from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

# Este es el esquema  que se creará en PostgreSQL
class Empleado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    dni: str = Field(index=True, unique=True)
    nombre: str
    apellido: str
    puesto: str
    correo: str = Field(unique=True) # El usuario para el login
    password: str # La contraseña (inicialmente puede ser el DNI)
    role: str = Field(default="TRABAJADOR") # "ADMIN" o "TRABAJADOR"
    status: str = Field(default="PENDIENTE")

class Documento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    tipo: str  # Ejemplo: 'Contrato', 'Manual', 'Reglamento'
    ruta_archivo: str
    fecha_subida: datetime = Field(default_factory=datetime.now)
    id_empleado: Optional[int] = Field(default=None, foreign_key="empleado.id")