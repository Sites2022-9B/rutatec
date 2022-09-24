from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class BusquedaYPaginacion(BaseModel):
    search : Optional[str] = None
    offset : Optional[str] = None
    limit  : Optional[str] = None
    pagination_position : Optional[str] = None
    
    def validarPaginacion(self):
        if(self.limit == '' or self.limit==None ): self.limit = '5'
        if (self.limit != None and len(self.limit)>0 ) : 
            try: 
                size = int(self.limit)
                self.limit = str(size)
            except: 
                self.limit = "5"

        if(self.pagination_position == '' or self.pagination_position==None ): self.pagination_position = '1'
        if (self.pagination_position != None and len(self.pagination_position)>0 ) : 
            try: 
                numPage = int(self.pagination_position)
                self.pagination_position = str(numPage)
            except: 
                self.pagination_position = "1"

        db_limit = int(self.limit) * int(self.pagination_position)
        db_offset = db_limit - int(self.limit)
        self.offset = str(db_offset)

class BusquedaYPaginacionConFecha(BusquedaYPaginacion):
    fechaini : Optional[str]
    fechafin : Optional[str]

    def validarPaginacionYFechas(self):
        self.validarPaginacion()
        self.fechaini = self._validarFecha(self.fechaini)
        self.fechafin = self._validarFecha(self.fechafin)
        if self.fechafin: self.fechafin += " 23:59" # agregar la hora para que considere todo el día

    def _validarFecha(self, fechadada):
        if (fechadada != None and len(fechadada)>0 ) : 
            try: 
                fini = datetime.strptime(fechadada, "%Y-%m-%d")
            except:
                fechadada = ""
        return fechadada
