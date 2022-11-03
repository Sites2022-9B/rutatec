from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

#---------------------------------------------------------
class Login(BaseModel):
    username: str
    password:str

    class Config():
        orm_mode = True
#---------------------------------------------------------
class UserChangePwd(BaseModel):
    id : int
    passwordactual :str
    passwordnvo :str
    passwordnvo2 : str    

class ForgotPassword(BaseModel):
    email: str

class UpdatePassword(BaseModel):
    email:  str
    pwdNuevo: str
    pwdNuevoRepetir: str
    referencia: str

class Addusuario(BaseModel):
    nombre: str
    apellidos: str
    correo: str
    contra: str

    def isValid(self):
        validado = True
        observa = ""
        if self.nombre == "":
            validado = False
            observa += f"Nombre requerido, "
        if self.apellidos == "":
            validado = False
            observa += f"apellidos requerido, "
        if self.contra == "":
            validado = False
            observa += f"Contraseña requerida, "
        
        return validado, observa

class UserUpdate(BaseModel):
    id: int
    nombre:str
    apellidos: str
    correo:str
    def isValid(self):
        validado = True
        observa = ""
        if self.nombre == "":
            validado = False
            observa += f"Nombre requerido, "
        if self.apellidos == "":
            validado = False
            observa += f"apellidos requerido, "
        if self.correo == "":
            validado = False
            observa += f"correo requerido, "
        
        return validado, observa