from typing import List
from sqlalchemy.sql.sqltypes import ARRAY
from modulos.shared_schemas import *
# from typing import Optional
# from pydantic import BaseModel, EmailStr

#---------------------------------------------------------
class Login(BaseModel):
    username: str
    password:str

    class Config():
        orm_mode = True
#---------------------------------------------------------
# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None

    def isValid(self):
        validado = True
        observa = ""
        if self.email == None:
            validado = False
            observa += f"EMAIL válido requerido, "
        
        if self.full_name == "":
            validado = False
            observa += f"FULL_NAME requerido, "

        return validado, observa
    
# Properties to receive via API on update
class UserChangePwd(BaseModel):
    id : int
    passwordactual :str
    passwordnvo :str
    passwordnvo2 : str
    
class UserUpdateAccount(UserBase):
    id: int

class UserInDBBase(UserBase):
    id: Optional[int] = None

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Add user
class UserAdd(UserBase):
    password: str
    isEncrypted: Optional[bool] = True
    empleado_id: Optional[int] = None

    def isValid(self):
        validado, observa = super().isValid()

        if self.password == "":
            validado = False
            observa += f"PASSWORD requerido, "
        elif len(self.password) < 3:
            validado = False
            observa += f"PASSWORD: mínimo 3 caracteres, "

        return validado, observa

class UserUpdate(UserBase):
    id: int
    empleado_id: Optional[int] = None

class ForgotPassword(BaseModel):
    email: str

# class UserResetPwdVerify(BaseModel):
#     email: str
#     referencia: str 

class UpdatePassword(BaseModel):
    email:  str
    pwdNuevo: str
    pwdNuevoRepetir: str
    referencia: str

class RolAdd(BaseModel):
    # id: Optional[int]
    rol:str

    def isValid(self):
        validado = True
        observa = ""
        if self.rol == "":
            validado = False
            observa += f"ROL requerido"
        
        return validado, observa

class RolUpdate(RolAdd):
    id: int

class CatalogoUpdate(BaseModel):
    id:int
    nombre:str
    icono:str
    showsidebar: Optional[bool] = False
    posicion: int
    catgrupo_id:int

class catalogoAdd(BaseModel):
    rol_id: int
    cat_id: int
    fechaini: datetime
    fechafin: Optional[datetime] = None

class catalogoFin(BaseModel):
    id: int
    rol_id : int
    cat_id: int
    fechaini: datetime
    fechafin: datetime

class catUserFin(BaseModel):
    user_id: List[int]
    cat_id: int
    fechafin: datetime

class catalogoUserAdd(BaseModel):
    user_id: List[int]
    cat_id: int
    fechaini: datetime
    fechafin: Optional[datetime] = None

class CatUserBusq(BusquedaYPaginacionConFecha):
    filtro : Optional[str] = ""
    id_cat : int

class CatRolBusq(BusquedaYPaginacion):
    fechabus : Optional[str]

class CatUpdate(BaseModel):
    id: int
    grupo: str
    posicion: int

class CatAdd(BaseModel):
    grupo: str
    posicion: int

    def isValid(self):
        validado = True
        observa = ""
        if self.grupo == "":
            validado = False
            observa += f"Grupo requerido, "
        
        if self.posicion == "":
            validado = False
            observa += f"Posicion requerido, "

        return validado, observa