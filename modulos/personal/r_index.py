from fastapi import APIRouter, Depends
from modulos.seguridad.r_authentication import SessionData, test_session
from typing import Tuple
from sqlalchemy.orm import Session
from db import database

router = APIRouter( tags=['registrar'] )

@router.get('/api/sidebar')
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = """SELECT * FROM rutas"""
    sqlParams = {}
    metadata,rows = database.execSql(sql, sqlParams, False, True)
    print('rutas',rows)
    return{"metadata": metadata, "data": rows}