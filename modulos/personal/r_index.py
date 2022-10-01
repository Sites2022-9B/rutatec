from importlib.metadata import MetadataPathFinder, metadata
import sqlite3
from fastapi import APIRouter, Request, Depends
from modulos.seguridad.r_authentication import SessionData, test_session, validarSessionforApis 
from typing import List, Tuple
from sqlalchemy.orm import Session
from db import database
from modulos.shared_schemas import BusquedaYPaginacion
from routers.plantillas import templates, fastapi
from modulos.shared_defs import getSettingsNombreEnvActivo
from modulos.shared_defs import prepParam



router = APIRouter( tags=['registrar'] )

@router.get('/api/sidebar')
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = """SELECT * FROM rutas"""
    sqlParams = {}
    metadata,rows = database.execSql(sql, sqlParams, False, True)
    print('rutas',rows)
    return{"metadata": metadata, "data": rows}