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