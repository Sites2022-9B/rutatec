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

class UserResetPwd(Base):
    __tablename__ = 'userreset'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False)
    referencia = Column(String, nullable=False, index=True) 
    fechaini = Column(DateTime)
    fechafin = Column(DateTime)
    confirmacion = Column(Boolean(), default=False)
    activado = Column(Boolean(), default=False)
