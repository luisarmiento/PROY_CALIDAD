from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

# Este es el esquema  que se creará en PostgreSQL
class Empleado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    dni: str = Field(index=True, unique=True)
    puesto: str
    correo: str
    contrato_pdf: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="PENDIENTE")
    role: Optional[str] = Field(default="candidato")
    hashed_password: Optional[str] = Field(default=None)