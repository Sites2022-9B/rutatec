from datetime import date, datetime
from typing import Optional,List

from pydantic import BaseModel

from modulos.shared_schemas import BusquedaYPaginacion

#---------------------------------------------------------
class EmpleadoAdd(BaseModel):
    # id : int
    titulo: str
    nombre: str
    apepat: str
    apemat: str
    codigo: Optional[str] = None
    sexo : Optional[str] = None
    nss: Optional[str] = None
    curp: Optional[str] = None
    rfc: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None

    def isValid(self):
        validado = True
        observa = ""
        #Todo Validaciones descartadas por cambios
        if self.titulo=="":
            validado = False
            observa += "TITULO requerido"
        if self.nombre=="":
            validado = False
            observa += "NOMBRE requerido"
        if self.apemat=="":
            validado = False
            observa += "APELLIDO PATERNO requerido"
        if self.apemat=="":
            validado = False
            observa += "APELLIDO MATERNO requerido"
        # if self.codigo == "":
        #     validado = False
        #     observa += f"CODIGO requerido, "
        # elif not self.codigo.isdigit():
        #     validado = False
        #     observa += f"CODIGO no numérico, "
        
        # if self.sexo == "":
        #     validado = False
        #     observa += f"SEXO requerido, "
        # elif not self.sexo in ["M", "F", "X"]:
        #         validado = False
        #         observa += f"SEXO no válido, "

        # if self.nss == "":
        #     validado = False
        #     observa += f"NSS requerido, "
        # else:
        #     if not self.nss.isdigit():
        #         validado = False
        #         observa += f"NSS no numérico, "
        #     if not len(self.nss) == 11:
        #         validado = False
        #         observa += f"NSS no tiene 11 digitos, "

        # if self.curp == "":
        #     validado = False
        #     observa += f"CURP requerido, "
        # elif not len(self.curp) == 18:
        #     validado = False
        #     observa += f"CURP no tiene 18 digitos, "

        # if self.rfc == "":
        #     validado = False
        #     observa += f"RFC requerido, "
        # elif not len(self.rfc) == 13:
        #     validado = False
        #     observa += f"RFC no tiene 13 digitos, "

        # if self.telefono == "":
        #     validado = False
        #     observa += f"TELEFONO requerido, "
        # elif len(self.telefono) < 10:
        #     validado = False
        #     observa += f"TELEFONO: almenos 10 digitos, "

        # if self.domicilio == "":
        #     validado = False
        #     observa += f"DOMICILIO requerido, "
        # elif len(self.domicilio) < 5:
        #     validado = False
        #     observa += f"DOMICILIO: almenos 5 caracteres, "

        return validado, observa
#---------------------------------------------------------
# Shared properties

class AreaAdd(BaseModel):
    id : Optional[int] = None
    codigo:str
    nombre:str
    areapadre_id:Optional[int] = None
    telefonos:str
    revisor:str
    lugar_id: Optional[int]= None
    idtabla:Optional[List[int]] = None
    operacionArea: Optional[List[str]] = None
    areaRO: Optional[List[int]] = None
    numeroRO: List[str]
    tipoRO: List[str]
    def isValid(self):
        validado = True
        observa = ""
        if self.codigo == "":
            validado = False
            observa += f"CODIGO requerido, "
        elif len(self.codigo) > 4:
            validado = False
            observa += f"CODIGO: máximo 4 digitos, "
        if self.nombre == "":
            validado = False
            observa += f"NOMBRE requerido, "
        
        if self.telefonos =="":
            validado = False
            observa += f"Telefono(s) requerido"
        elif len(self.telefonos) < 10:
            validado = False
            observa += f"Telefono debe de contener minimo 10 digitos"
        return validado, observa

class GrupoAdd(BaseModel):
    #id : Optional[int]
    grupo:str
    nombre:str

    def isValid(self):
        validado = True
        observa = ""
        if self.grupo == "" or len(self.grupo) > 4 or len(self.grupo) < 3:
            validado = False
            observa += f"El código debe contener entre 3 y 4 caracteres"
        if self.nombre == "" or len(self.nombre) > 45 or len (self.nombre) < 3:
            validado = False
            observa += f" El clasificador debe contener entre 3 y 45 caracteres " 
        
        return validado, observa


class AreaUpdate(AreaAdd):
    id : int

class GrupoUpdate(GrupoAdd):
    id : int

class EmpleadoUpdate(EmpleadoAdd):
    id : Optional[int]
    # pass

class AreaEmpAdd(BaseModel):
    area_id: int
    user_id: int
    fechafin: Optional[date] = None
    fechaini: date

class AreaResAdd(BaseModel):
    area_id: int
    empleado_id: int
    fechaini: date
    fechafin: Optional[date] = None
    def isValid(self):
        validado = True
        observa = ""
        if self.fechaini == None:
            validado = False
            observa += f"FECHAINI requerido (Ej. 2021-11-07),"             
        if self.fechaini != None and self.fechafin != None:
            if self.fechafin <= self.fechaini:
                validado = False
                observa += f"La FECHA de Fin debe ser mayor que la fecha de Inicio, " 
        return validado, observa

class AreaResUpdate(AreaResAdd):
    id : int
    fechafin: date

class AreaEmpFinish(BaseModel):
    id_ar: int
    fechafin: date
    fechaini: date

class PuestoEmpAdd(BaseModel):
    puesto_id: int
    user_id: int
    fechafin: Optional[date] = None
    fechaini: date

class PuestoEmpFinish(BaseModel):
    id_pe: int
    fechafin: date
    fechaini: date

class PuestoAdd(BaseModel):
    # id : Optional[int]
    clave: str
    nombre:str
    grupotag_id: Optional[int] = None
    fechaini: date
    fechafin: Optional[date] = None

    def isValid(self):
        validado = True
        observa = ""
        if self.clave == "":
            validado = False
            observa += f"CLAVE requerida, "
        elif len(self.clave) > 4:
            validado = False
            observa += f"CLAVE: máximo 4 digitos, "

        if self.nombre == "":
            validado = False
            observa += f"NOMBRE requerido, "
        
        if self.grupotag_id == None:
            validado = False
            observa += f"GRUPOTAG numérico requerido, "

        if self.fechaini != None and self.fechafin != None:
            if self.fechaini >= self.fechafin:
                validado = False
                observa += f"FECHA FIN debe ser mayor que FECHA INICIO, "
          
        return validado, observa

class PuestoUpdate(PuestoAdd):
    id : int

class busqAreaRes(BusquedaYPaginacion):
    id_area : int


class RolUserAdd(BaseModel):
    user_id: List[int]
    rol_idf: int
    fechaini : datetime
    fechafin : Optional[datetime] = None

class RolUserFinish(BaseModel):
    rol_idf:int
    fechafin : Optional[datetime] = None

class UserEmpAdd(BaseModel):
    user_id: int
    empleado_id: int

class busqUsuFech(BusquedaYPaginacion):
    fechabusU: Optional[str]
    id_rol : int

class UserEmpUpdate(BaseModel):
    id_ue: int
    empleado_id: int

class grupotagAdd(BaseModel):
    grupo:str
    nombre:str
    
    def isValid(self):
        validado = True
        observa = ""
        if self.grupo == "":
            validado = False
            observa += f"GRUPO requerido, "
        elif len(self.grupo) > 4:
            validado = False
            observa += f"GRUPO: máximo 4 digitos, "

        if self.nombre == "":
            validado = False
            observa += f"NOMBRE requerido, "
        
        return validado, observa
    
class grupotagupdate(grupotagAdd):
    id: int

class BusqFecha(BusquedaYPaginacion):
    fechabus : Optional[str]

class lugarAdd(BaseModel):
    lugar: str

class lugarUpdate(lugarAdd):
    id: int
