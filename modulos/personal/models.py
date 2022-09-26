from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, inspect, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.sqltypes import Date

from db.base_class import Base
#from typing import TYPE_CHECKING

#if TYPE_CHECKING:
#    from .item import Item  # noqa: F401

class Area(Base):
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(3), unique=True, index=True, nullable=False)
    nombre = Column(String, index=True, nullable=False)
    areapadre_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    telefonos = Column(String, index=True, nullable=False)
    revisor = Column(String(1),index=True, nullable=True)
    lugar_id = Column(Integer, ForeignKey("lugares.id"), nullable=True)
    #items = relationship("Item", back_populates="owner")

class Areatipo(Base):
    __tablename__='areatipo'

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    num = Column(String(3), index=True, nullable=False)
    tipo = Column(String(1), index=True, nullable=False)

class Empleado(Base):
    __tablename__ = 'empleados'
    id = Column(Integer, primary_key=True, index=True)
    titulo= Column(String(7), index=True, nullable=True)
    nombre = Column(String, index=True, nullable=False)
    apepat = Column(String, index=True, nullable=False)
    apemat = Column(String, index=True, nullable=False)
    codigo = Column(String, unique=True, index=True, nullable=True)
    titulo = Column(String, index=True, nullable=True)
    sexo = Column(String(1), index=True, nullable=True)
    nss = Column(String(11), index=True, nullable=True)
    curp = Column(String(18), index=True, nullable=True)
    rfc = Column(String(13), index=True, nullable=True)
    telefono = Column(String, nullable=True)
    domicilio = Column(String, nullable=True)

    def getLabels(self, database):
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
        labels= []
        for index, md in enumerate(mdColumn):
            if md == "codigo": md = "Código" 
            elif md == "apepat": md = "Apellido Paterno" 
            elif md == "apemat": md = "Apellido Materno"
          
            labels.append(md)
        return labels

class AreaEmpleado(Base):
    __tablename__ = 'areaempleado'

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    areas = relationship("Area")
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    empleados = relationship("Empleado")
    fechaini = Column(Date, nullable=False)
    fechafin = Column(Date, nullable=True)

class AreaResponsable(Base):
    __tablename__ = 'arearesponsable'

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    areas = relationship("Area")
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    empleados = relationship("Empleado")
    fechaini = Column(Date, nullable=False)
    fechafin = Column(Date, nullable=True)

class AreaResponsableGetView(Base):
    __tablename__ = 'arearesponsable_get_vw'

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    areas = relationship("Area")
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False)
    empleados = relationship("Empleado")
    nombreemp = Column(String, nullable=False)
    fechaini = Column(Date, nullable=False)
    fechafin = Column(Date, nullable=True)
    areapadre_id = Column(Integer, nullable=True)

class Puestos(Base):
    __tablename__ = 'puestos'

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String, index=True, nullable=False)
    nombre = Column(String, index=True, nullable=False)
    grupotag_id = Column(Integer, ForeignKey("grupotag.id"))
    fechaini = Column(Date, index=True, nullable=False)
    fechafin = Column(Date, index=True, nullable=True)

    def getLabels(self, database):
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
        labels= []
        for index, md in enumerate(mdColumn):
            if md == "id": md = "id" 
            elif md == "clave": md = "clave" 
            elif md == "nombre": md = "Nombre"
            elif md == "grupotag_id": md = "IdGrupo" 
            elif md == "fechaini": md = "Fecha Inicio"
            elif md == "fechafin": md = "Fecha Finalización"
          
            labels.append(md)
        return labels

class PuestoEmpleado(Base):
    __tablename__ = 'puestoempleado'

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"))
    empleados = relationship("Empleado")
    puesto_id = Column(Integer, ForeignKey("puestos.id"))
    puestos = relationship("Puestos")
    fechaini = Column(Date, nullable=False)
    fechafin = Column(Date, nullable=True)

class UserEmpleado(Base):
    __tablename__ = 'userempleados'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    empleado_id = Column(Integer, ForeignKey("empleados.id"))
    employers = relationship("Empleado")

class GrupoTag(Base):
    __tablename__ = 'grupotag'
    id = Column(Integer, primary_key=True, index=True)
    grupo = Column(String, index=True, nullable=False)
    nombre = Column(String, nullable=False)

    def getLabels(self, database):
        mdColumn = [ col["name"] for col in inspect(database.engine).get_columns(self.__tablename__) ]
        labels= []
        for index, md in enumerate(mdColumn):
            if md == "id": md = "id" 
            elif md == "grupo": md = "Código" 
            elif md == "nombre": md = "Clasificador" 
          
            labels.append(md)
        return labels

class EmpleadoFoto(Base):
    __tablename__ = 'empleadofoto'

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"))
    nombre = Column(String(50), nullable=False)

class Lugares(Base):
    __tablename__ = 'lugares'

    id = Column(Integer, primary_key=True, index=True)
    lugar = Column(String(100), nullable=False)
    