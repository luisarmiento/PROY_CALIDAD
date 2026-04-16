from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

# Este es el esquema  que se creará en PostgreSQL
class Empleado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    dni: str = Field(unique=True, index=True) # El DNI no se puede repetir
    puesto: str
    correo: str
    contrato_pdf: str
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="PENDIENTE") # Los nuevos nacerán como Pendiente