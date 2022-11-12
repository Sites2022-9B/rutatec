from db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.sql.sqltypes import  DateTime


class Rutas(Base):
    __tablename__='rutas'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, index=True)


class Historial(Base):
    __tablename__ = 'historial'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey ("usuario.id"), nullable=False)
    rutas_id = Column(Integer, ForeignKey ("rutas.id"), nullable=False)
    fecha = Column(DateTime, nullable=False)