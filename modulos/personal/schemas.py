from pydantic import BaseModel
from modulos.shared_schemas import BusquedaYPaginacion


class BusqFecha(BusquedaYPaginacion):
    fechabus : Optional[str]

class lugarAdd(BaseModel):
    lugar: str

class lugarUpdate(lugarAdd):
    id: int
