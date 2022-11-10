from db.base_class import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import  DateTime

class Historial(Base):
    __tablename__ = 'historial'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey ("usuario.id"), nullable=False)
    rutas_id = Column(Integer, ForeignKey ("rutas.id"), nullable=False)
    fecha = Column(DateTime, nullable=False)