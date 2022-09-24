from fastapi import APIRouter, Request, Depends
from modulos.seguridad.r_authentication import SessionData, test_session 
from typing import List, Tuple
from sqlalchemy.orm import Session
from db import database
from routers.plantillas import templates, fastapi
from modulos.shared_defs import getSettingsNombreEnvActivo


router = APIRouter( tags=['registrar'] )

@router.get("/registrar")
async def show_U_View(request: Request, ret: str = "/registrar", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    return templates.TemplateResponse( name="Registrar.html", context={ "request": request, "ret": ret, "envname": getSettingsNombreEnvActivo(db) } )