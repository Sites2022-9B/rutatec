from datetime import date
from pydantic import BaseModel
from typing import Optional, List
from modulos.shared_schemas import BusquedaYPaginacion


class BusqFecha(BusquedaYPaginacion):
    fechabus : Optional[str]

class lugarAdd(BaseModel):
    lugar: str

class lugarUpdate(lugarAdd):
    id: int

class historialadd(BaseModel):
    id: List[int]
    operacion: List[str]
    nombre: List[str]
    fecha: List[date]
