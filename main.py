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
from modulos.seguridad import initBDSeguridad, r_authentication, r_user, r_rol, r_catalogos, r_catgrupo
from modulos.gestion import r_procesos
from modulos.proc_pide import r_pide, r_planes
from modulos.proc_poainst import r_poainst, r_poainst_regautorizado
from modulos.finanzas_ppto import r_ctabancfte, r_pptoaportipo, r_cuenta_bancaria, r_capypart, r_banco
from modulos.proc_proy import r_pptostatus, r_proytipo, r_proyectos, r_tipoproc
from modulos.personal import r_areas, r_empleados, r_puestos, r_grupotag, r_lugar
from modulos.proc_comision import r_comedo, r_comtipo, r_viaticos, r_marcavehiculo, r_vehiculo, r_comisiones
from modulos.proc_req import r_requni, r_articulos, r_requisiciones, r_proveedor, r_tramite
from modulos.reportes import r_reportes, r_repmembretegral
from modulos.cedulas import r_cedulas
from modulos.shared_defs import getAnioFiscalActual, getAreaActual2, getEmpleadoId, getPermisos, getSettingsNombreEnvActivo, is_SuperUser
from modulos import shared_routers
from modulos.proc_pagos import r_pagos

# Cargar en memoria todos los modelos para su creación automática
from modulos.seguridad.models import *
from modulos.gestion.models import *

# Crear las tablas en BD según los modelos previamente cargados
#Base.metadata.create_all(engine)

# Ejecutar los archivos de scritps de sql de cambios sobre estructuras y datos de la base de datos
if not createLastChangesInDB():
    print('Se presentaron errores de conexión con el servidor de base de datos y con los scripts de actualizaciones')
else:
    # Inicializar estructuras y datos del modulo de seguridad
    initBDSeguridad.initBDdatos()

app = FastAPI( title="SisutsWeb")

app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(r_authentication.router)
app.include_router(r_user.router)
app.include_router(r_catalogos.router)
app.include_router(r_procesos.router)
app.include_router(r_pide.router)
app.include_router(r_poainst.router)
app.include_router(r_poainst_regautorizado.router)
app.include_router(r_areas.router)
app.include_router(r_empleados.router)
app.include_router(r_puestos.router)
app.include_router(r_rol.router)
app.include_router(r_planes.router)
app.include_router(r_ctabancfte.router)
app.include_router(r_banco.router)
app.include_router(r_cuenta_bancaria.router)
app.include_router(shared_routers.router)
app.include_router(r_proytipo.router)
app.include_router(r_tipoproc.router)
app.include_router(r_comedo.router)
app.include_router(r_viaticos.router)
app.include_router(r_pptostatus.router)
app.include_router(r_comtipo.router)
app.include_router(r_requni.router)
app.include_router(r_pptoaportipo.router)
app.include_router(r_marcavehiculo.router)
app.include_router(r_vehiculo.router)
app.include_router(r_reportes.router)
app.include_router(r_capypart.router)
app.include_router(r_repmembretegral.router)
app.include_router(r_articulos.router)
app.include_router(r_requisiciones.router)
app.include_router(r_proveedor.router)
app.include_router(r_tramite.router)
app.include_router(r_grupotag.router)
app.include_router(r_proyectos.router)
app.include_router(r_catgrupo.router)
app.include_router(r_comisiones.router)
app.include_router(r_cedulas.router)
app.include_router(r_lugar.router)
app.include_router(r_pagos.router)


 
@app.get('/logourutatec.png', include_in_schema=False)
def logoutselva():
    return RedirectResponse(url='/static/sites.png')


@app.get("/")
async def looking_Main(request: Request, ret: str = "/main"):
    return RedirectResponse('/main?ret='+ ret)

@app.get("/main")
async def show_Main_Index(request:Request, session: Tuple[SessionData, str] = Depends(test_session), ret: str = "/main", db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    user = is_SuperUser(session, db)
    permisos = getPermisos(user, session, db)
    # catgrupo = db.query(Catgrupo.id, Catgrupo.grupo, Catgrupo.posicion).all()
    catgrupo = db.query(Catgrupo).all()
    # Enviar el área al que pertenece el usuario, y el año fiscal anual
    emp_id = getEmpleadoId(user.id, db)
    area_emp = None
    if emp_id != None:
        area_emp = getAreaActual2(emp_id, db)
    aniofiscalActual = getAnioFiscalActual()
    return templates.TemplateResponse( name="index.html", context={ "request": request, "user": session[0], "full_name": user[2],
        "is_superuser": user[1], "permisos":permisos, "ret":ret, "envname": getSettingsNombreEnvActivo(db)
        , "emp_id":emp_id, "area":area_emp, "catgrupo":jsonable_encoder(catgrupo), "aniofiscal": aniofiscalActual })

@app.get("/err")
@app.exception_handler(404)
def page_not_found(request:Request, detail :str = "" ):
    if ( isinstance(detail, HTTPException) ) : detail = "" #detail.detail
    return templates.TemplateResponse( name="error.html", context={ "request": request, "detail":detail } )

@app.get("/about_us")
async def show_about_us(request:Request, session: Tuple[SessionData, str] = Depends(test_session),ret: str = "/about_us", db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    user = is_SuperUser(session,db)
    permisos = getPermisos(user, session, db)
    return templates.TemplateResponse( name="acerca_de.html", context={ "request": request, "user": session[0]
    , "envname": getSettingsNombreEnvActivo(db)
    , "is_superuser": user.is_superuser,"permisos":permisos} )

@app.get("/popups")
async def show_Main_Test_Popups():
    # Esta prueba es una prueba sencilla para validar que es posible abrir nuevas ventanas 
    # desde la página principal o subpáginas, en coordinación con el script
    html_content = """
    <html><body><h1>TEST: OK</h1></body>
        <script type="text/javascript">window.close();</script>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/forgot-password")
def page_forgot_password(request:Request):
    return templates.TemplateResponse( name="forgot-password.html", context={ "request": request } )

@app.get('/logoutselva.png', include_in_schema=False)
def logoutselva():
    return RedirectResponse(url='/static/logoutselva.png')

HOST="127.0.0.1"
PORT=8000
print (f"Presiona CTRL + click en: http://{HOST}:{PORT}")
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
