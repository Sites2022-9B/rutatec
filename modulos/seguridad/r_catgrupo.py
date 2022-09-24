from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, hasPermisos, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth
from .models import *
from .schemas import *
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session


router = APIRouter( tags=['catgrupo'] )
hoy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@router.get("/catgrupo")
async def show_R_View(request: Request, ret: str = "/catgrupo", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/catgrupo"
    pagina = "catgrupo.html"
    return accessPageValidate(url, pagina, session, db, request, ret)


@router.post('/api/catgrupo')
async def getcat(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        sql = '''Select id, grupo, posicion from(
                    select c.id, c.grupo, Cast(c.posicion AS Varchar) posicion from catgrupo
                    c
                    )p'''
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'grupo', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'posicion', 'like', busq.search, '')

        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        print("SQL: ", sql)
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= Catgrupo().getLabels(database)
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/catgrupo/addcat")
async def addCat(CatDado:CatAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catgrupo/addcat'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = CatDado.isValid()
        if esValido:
            existe_r = db.query(Catgrupo).filter(Catgrupo.grupo == CatDado.grupo).first()
            if existe_r == None:
                datos = Catgrupo(**CatDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"El nombre del grupo ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")
    
@router.put("/api/catgrupo/update")
async def updateCatalogo(CatDado:CatUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catgrupo/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        catAactualizar = db.get(Catgrupo, CatDado.id)
        catAactualizar.grupo = CatDado.grupo
        catAactualizar.posicion = CatDado.posicion
        catAactualizar.update(db)
        return {"message": "Success!!!"}
    raiseExceptionNoAuth(f"Acceso no autorizado")

