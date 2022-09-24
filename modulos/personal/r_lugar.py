from fastapi import APIRouter, Depends, Request
from sqlalchemy.sql.elements import or_
from modulos.personal.models import Lugares
from modulos.personal.schemas import lugarAdd, lugarUpdate
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from typing import List, Tuple
from sqlalchemy.orm import Session
from db import database
from starlette.responses import RedirectResponse
from datetime import datetime

from modulos.shared_defs import accessPageValidate, hasPermisos, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth
from modulos.shared_schemas import BusquedaYPaginacion


router = APIRouter( tags=['Lugares'] )

@router.get("/lugares")
async def show_U_View(request: Request, ret: str = "/lugares", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    
    url = "/lugares"
    pagina = "lugares.html"
    return accessPageValidate(url, pagina, session, db, request, ret)

@router.post('/api/lugares')
async def getAreasTable(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/lugares'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    # if( hasPermisos(userAutentificado, url) ):
    sql = f"""SELECT * FROM lugares"""
    cond = ""
    sqlParams = {}
    cond += prepParam(sqlParams, '', 'lugar', 'like', busq.search, '')
    busq.validarPaginacion()
    if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
    # Obtener la página de registros derivados de la consulta
    getTotal = True
    [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
    return {"labels":['ID','Lugar'], "metadata" : metadata, "data": rows, "total" : total}
    # raiseExceptionNoAuth(f"Permiso denegado")

@router.post("/api/lugares/addlugar")
async def addArea(areaDado:lugarAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/lugares/addlugar'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        existe_l = db.query(Lugares).filter(Lugares.lugar == areaDado.lugar).first()
        if existe_l == None:
                datos = Lugares(**areaDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El lugar ya existe, favor de verificar")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/lugares/update")
async def updateGrupo(lugarDado:lugarUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/lugares/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        lugarAct = db.get(Lugares, lugarDado.id)
        existe_l = db.query(Lugares).filter(Lugares.lugar == lugarDado.lugar).filter(Lugares.id != lugarDado.id).first()
        if existe_l == None:
            grupo_data = lugarDado.dict(exclude_unset=True)
            for key, value in grupo_data.items():
                setattr(lugarAct, key, value)
            
            lugarAct.update(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El Grupo o el nombre ya existe, favor de verificar")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/lugares/combo")
async def getAreasCombo(q:str="", q_lugar_id:str="", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/lugares/combo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f"select * from lugares"
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'id', '=', q_lugar_id, 'and')
        cond += prepParam(sqlParams, '', 'lugar', 'like', q, '')
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        [metadata, rows] = database.execSql(sql, sqlParams, False, True)
        return {'metadata': metadata, 'data': rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")