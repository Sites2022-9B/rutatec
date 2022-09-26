from typing import Optional
from sqlalchemy import inspect
from sqlalchemy.orm import backref

from modulos.shared_schemas import BusquedaYPaginacion
from ..shared_models import *


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campo = Column(String, nullable=False)
    valor = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, index=True)
    apellidos = Column(String, index=True)
    correo = Column(String, unique=True, index=True, nullable=False)
    contra = Column(String, nullable=False)
    isEncrypted = Column(Boolean(), nullable=False)


class Rol(Base):
    __tablename__ = 'rol'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rol = Column(String, index=True)



class Cat(Base):
    __tablename__ = "cat"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)



class CatUser(Base):
    __tablename__ = "catuser"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #llaves foraneas

    
class CatRol(Base):
    __tablename__ = "catrol"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #llaves foraneas
    fechaini = Column(DateTime, nullable=False)
    fechafin = Column(DateTime, nullable=True)



class UserResetPwd(Base):
    __tablename__ = 'userreset'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False)
    referencia = Column(String, nullable=False, index=True) 
    fechaini = Column(DateTime)
    fechafin = Column(DateTime)
    confirmacion = Column(Boolean(), default=False)
    activado = Column(Boolean(), default=False)


class Catgrupo(Base):
    __tablename__ = 'catgrupo'
    id = Column (Integer, primary_key=True, index=True, autoincrement=True)
    grupo = Column(String, index=True, nullable=False)
    posicion = Column(Integer, index=True, nullable=False)
