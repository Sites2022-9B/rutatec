from pydantic import BaseModel
from typing import Optional
from modulos.shared_schemas import BusquedaYPaginacion


class BusqFecha(BusquedaYPaginacion):
    fechabus : Optional[str]

class lugarAdd(BaseModel):
    lugar: str

class lugarUpdate(lugarAdd):
    id: int
