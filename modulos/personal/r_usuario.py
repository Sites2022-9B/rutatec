from fastapi import APIRouter, Request, Depends
from modulos.seguridad.models import User
from modulos.seguridad.r_authentication import SessionData, test_session
from typing import List, Tuple
from sqlalchemy.orm import Session
from db import database
from modulos.seguridad.schemas import Addusuario
from modulos.seguridad.sec.sec_hashing import Hash
from routers.plantillas import templates, fastapi
from modulos.shared_defs import getSettingsNombreEnvActivo, raiseExceptionDataErr, raiseExceptionNoAuth


router = APIRouter( tags=['registrar'] )

@router.get("/registrar")
async def show_U_View(request: Request, ret: str = "/registrar", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    return templates.TemplateResponse( name="Registrar.html", context={ "request": request, "ret": ret, "envname": getSettingsNombreEnvActivo(db) } )


@router.post("/api/usuario/registrar")
async def addusuario(usuDado: Addusuario , session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    esValido, observa = usuDado.isValid()
    if esValido:
        existe_g = db.query(User).filter(User.correo == usuDado.correo).first()
        if existe_g == None:
            datos = User(
                nombre = usuDado.nombre,
                apellidos = usuDado.apellidos,
                correo = usuDado.correo,
                contra = Hash.bcrypt(usuDado.contra)
            )
            print('Datos registrados: ', datos.contra)
            datos.create(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El correo ya existe, favor de verificar")
    raiseExceptionDataErr(observa)

@router.get("/api/sidebar")
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = f"""SELECT * FROM rutas"""
    sqlParams = {}
    metadatas,rows = database.execSql(sql, sqlParams, False, True)
    print('rutas', rows)
    return {"metadata" : metadatas, "data": rows}
    # raiseExceptionNoAuth(f"Permiso denegado")
    raiseExceptionDataErr(observa)

