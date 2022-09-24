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
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    isEncrypted = Column(Boolean(), default=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    roles = relationship("RolUser", back_populates="user")

    def getLabels(self, database):
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
        labels= []
        for index, md in enumerate(mdColumn):
            if md == "id": md = "Id" 
            elif md == "full_name": md = "Nombre completo" 
            elif md == "email": md = "Correo" 
            elif md == "isEncrypted": md = "Encriptado" 
            elif md == "is_active": md = "Activo" 
            elif md == "is_superuser": md = "Administrador" 
            labels.append(md)
        return labels

class Rol(Base):
    __tablename__ = 'rol'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rol = Column(String, index=True)
    users = relationship("RolUser", back_populates="rol")

    def getLabels(self, database):
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
        labels= []
        for index, md in enumerate(mdColumn):
            if md == "id": md = "id" 
            elif md == "rol": md = "Nombre rol"
          
            labels.append(md)
        return labels

class BusqRolFecha(BusquedaYPaginacion):
    fechabus : Optional[str]

class RolUser(Base):
    __tablename__ = 'roluser'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    rol_id = Column(Integer, ForeignKey("rol.id"))
    fechaini = Column(DateTime, nullable=False)
    fechafin = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="roles")
    rol = relationship("Rol", back_populates="users")

class Cat(Base):
    __tablename__ = "cat"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    url = Column(String, nullable=False)
    icono = Column(String, nullable=False)
    showsidebar = Column(Boolean)
    posicion = Column(Integer, nullable=False)
    catgrupo_id = Column(Integer, ForeignKey("catgrupo.id"))

    def getLabels(self, database):
            mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
            labels= []
            for index, md in enumerate(mdColumn):
                if md == "nombre": md = "Catálogo"
                elif md == "url": md = "URL" 
                elif md == "showsidebar": md = "Mostrar en el sidebar"
                elif md == "catgrupo_id": md = "Grupo" 
                labels.append(md)
            return labels

class CatUser(Base):
    __tablename__ = "catuser"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #llaves foraneas
    user_id = Column(Integer, ForeignKey("user.id"))
    cat_id = Column(Integer, ForeignKey("cat.id"))
    fechaini = Column(DateTime, nullable=False)
    fechafin = Column(DateTime, nullable=True)

    user_rel = relationship(User, backref=backref('catuser'), uselist= True)
    cat_rel = relationship(Cat, backref=backref('catuser'), uselist= True)
    
class CatRol(Base):
    __tablename__ = "catrol"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #llaves foraneas
    rol_id = Column(Integer, ForeignKey("rol.id"))
    cat_id = Column(Integer, ForeignKey("cat.id"))
    fechaini = Column(DateTime, nullable=False)
    fechafin = Column(DateTime, nullable=True)

    rol_rel = relationship(Rol, backref=backref('catrol'), uselist= True)
    cat_rel2 = relationship(Cat, backref=backref('catrol'), uselist= True)


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

    def getLabels(self, database):
            mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
            labels= []
            for index, md in enumerate(mdColumn):
                if md == "grupo": md = "Grupo"
                elif md == "posicion": md = "Posición" 
                labels.append(md)
            return labels
