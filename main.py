from typing import Tuple
from db.database import createLastChangesInDB
from sqlalchemy.orm import Session
from db import database
from routers.plantillas import templates
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from modulos.seguridad.r_authentication import SessionData, test_session
from modulos.seguridad import r_authentication, initBDSeguridad
from modulos.personal import r_usuario, r_index
from modulos.shared_defs import getSettingsNombreEnvActivo
from modulos.seguridad.models import User, UserResetPwd, Settings
from modulos.personal.schemas import BusqFecha, lugarAdd, lugarUpdate
# import sentry_sdk




if not createLastChangesInDB():
    print('Se presentaron errores de conexión con el servidor de base de datos y con los scripts de actualizaciones')
else:
    # Inicializar estructuras y datos del modulo de seguridad
   initBDSeguridad.initBDdatos()

app = FastAPI( title="Rutatec")

app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(r_authentication.router)
app.include_router(r_usuario.router)
app.include_router(r_index.router)

@app.get('/perfil.png', include_in_schema=False)
def perfil():
    return RedirectResponse(url='/static/perfil.png')
    
@app.get("/")
async def looking_Main(request: Request, ret: str = "/main"):
    return RedirectResponse('/main?ret='+ ret)

@app.get("/main")
async def show_Main_Index(request:Request, session: Tuple[SessionData, str] = Depends(test_session), ret: str = "/main", db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" + ret)
    return templates.TemplateResponse( name="index.html", context={ "request": request})

@app.get("/err")
@app.exception_handler(404)
def page_not_found(request:Request, detail :str = "" ):
    if ( isinstance(detail, HTTPException) ) : detail = "" #detail.detail
    return templates.TemplateResponse( name="error.html", context={ "request": request, "detail":detail } )

@app.get("/about_us")
async def show_about_us(request:Request, session: Tuple[SessionData, str] = Depends(test_session),ret: str = "/about_us", db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    return templates.TemplateResponse( name="acerca_de.html", context={ "request": request, "user": session[0]
    , "envname": getSettingsNombreEnvActivo(db)
    } )

@app.get("/popups")
async def show_Main_Test_Popups():
    html_content = """
    <html><body><h1>TEST: OK</h1></body>
        <script type="text/javascript">window.close();</script>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/RecuperarContraseña")
def page_forgot_password(request:Request):
    return templates.TemplateResponse( name="recuperarcon.html", context={ "request": request } )

@app.get("/pruebashtml")
def page_pruebas_html(request:Request):
    return templates.TemplateResponse( name="pruebas.html", context={ "request": request } )

@app.get('/sites.png', include_in_schema=False)
def logoutselva():
    return RedirectResponse(url='/static/sites.png')

HOST="127.0.0.1"
PORT=8000
print (f"Presiona CTRL + click en: http://{HOST}:{PORT}")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

# sentry_sdk.init(
#     dsn="https://90a7cd6f5f104cffa312959b6c528f4e@o4504214988587008.ingest.sentry.io/4504214998614016",

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate= 1.0
# )