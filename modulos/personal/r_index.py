from datetime import datetime
from fastapi import APIRouter, Depends
from modulos.personal.models import Historial
from modulos.personal.schemas import historialadd
from modulos.seguridad.r_authentication import SessionData, test_session
from typing import Tuple
from sqlalchemy.orm import Session
from db import database
from modulos.shared_defs import raiseExceptionDataErr

router = APIRouter( tags=['registrar'] )

@router.get('/api/sidebar')
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = """SELECT * FROM rutas"""
    sqlParams = {}
    metadata,rows = database.execSql(sql, sqlParams, False, True)
    return{"metadata": metadata, "data": rows}

@router.get('/api/terminales')
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = """SELECT nombre, latitud, longitud FROM terminales"""
    sqlParams = {}
    metadata,rows = database.execSql(sql, sqlParams, False, True)
    return{"metadata": metadata, "data": rows}

@router.get('/api/puntrutas/{id_ruta}')
async def getrutas(id_ruta: str ,session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    fechaact = datetime.today().strftime('%Y-%m-%d')
    existe_r = db.query(Historial).filter(Historial.user_id == session[0].id, Historial.rutas_id == id_ruta).first()
    if existe_r == None:
        datos = Historial(
            user_id = session[0].id,
            rutas_id = id_ruta,
            fecha = fechaact,
        )
        datos.create(db)
    sql = 'SELECT latitud, longitud FROM puntrutas Where rutas_id =' + id_ruta
    sqlParams = {}
    rows = database.execSql(sql, sqlParams, False, True)
    return{"data": rows}

@router.get('/api/historial')
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = '''SELECT hs.rutas_id , rt.nombre, hs.fecha FROM(SELECT * FROM historial WHERE user_id = '''+str(session[0].id)+''')hs
            LEFT JOIN rutas rt ON rt.id = hs.rutas_id'''
    sqlParams = {}
    rows = database.execSql(sql, sqlParams, False, True)
    return{"historial": rows}

@router.post('/api/historial/delete')
async def getrutas(Hdado: historialadd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    for i in range(len(Hdado.nombre)):
        if(Hdado.operacion[i] == 'Delete'):
            eliminarInst = db.query(Historial).filter(Historial.rutas_id == Hdado.id[i]).first()
            eliminarInst.delete(db)
    return {"message": "Success!!!"}  


