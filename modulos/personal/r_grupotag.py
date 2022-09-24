from genericpath import exists
import os
from fastapi.datastructures import UploadFile
import pandas as pd
from fastapi.params import File, Form
from sqlalchemy.sql.elements import or_
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, getSettingsName, hasPermisos, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth, savelog
from modulos.shared_schemas import BusquedaYPaginacion
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import List, Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter( tags=['Grupotag'] )

@router.get("/grupotag")
async def show_U_View(request: Request, ret: str = "/grupotag", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    
    url = "/grupotag"
    pagina = "grupotag.html"
    return accessPageValidate(url, pagina, session, db, request, ret)

@router.post('/api/grupotag')
async def getGrupoTable(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/grupotag'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        sql = 'select * from grupotag'
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'grupo', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'nombre', 'like', busq.search, '')

        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels = GrupoTag().getLabels(database)
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/grupotag/addgrupotag")
async def addGrupo(grupoDado:GrupoAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/grupotag/addgrupotag'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = grupoDado.isValid()
        if esValido:
            existe_g = db.query(GrupoTag).filter(or_(GrupoTag.grupo == grupoDado.grupo, GrupoTag.nombre == grupoDado.nombre)).first()
            if existe_g == None:
                datos = GrupoTag(**grupoDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"El Grupo o el nombre ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/grupotag/update")
async def updateGrupo(grupoDado:GrupoUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/grupotag/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = grupoDado.isValid()
        if esValido:
            grupoAct = db.get(GrupoTag, grupoDado.id)
            existe_g = db.query(GrupoTag).filter(or_(GrupoTag.grupo == grupoDado.grupo, GrupoTag.nombre == grupoDado.nombre)).filter(GrupoTag.id != grupoDado.id).first()
            if existe_g == None:
                grupo_data = grupoDado.dict(exclude_unset=True)
                for key, value in grupo_data.items():
                    setattr(grupoAct, key, value)
                
                grupoAct.update(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"El Grupo o el nombre ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/grupotag/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/grupotag/uploadfiles'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        listResult = []
        rutaDePlantillasUploads = getSettingsName("$SYS_DIR_MODELS_PLANTILLAS_UPLOADS", "/f/models_plantillas_uploads")
        rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/"
        # crear el directorio en caso de que no exista
        if not exists(rutafile):
            os.makedirs(rutafile)
        
        fhms = datetime.today().strftime("%Y%m%d%H%M%S%f")
        # cuando el excel tiene columnas de tipo
        #  text/string pero contienen numeros y se desea que se mantengan como text/string
        col_types = {"grupo":str}
        # print(fhms)
        
        for file in files:
            nombreArchivo = f"{fhms}_{file.filename}"
            try:
                totFilas = 0
                with open(f"{rutafile}{nombreArchivo}", "wb") as myfile:
                    content = await file.read()
                    myfile.write(content)
                    myfile.close()
                    file.filename = nombreArchivo
                    df = pd.read_excel(f"{rutafile}{nombreArchivo}", dtype=col_types)
                    filasError = 0 
                    msg=""
                    listStatus = []
                    for indice, fila in df.iterrows():
                        totFilas += 1
                        # verificar celdas vacías
                        for clave, valor in fila.items():
                            if pd.isna(valor):
                                fila[clave] = ""

                        # print("fila sin NAN", fila)
                        validaFila = GrupoAdd(**fila)
                        esValido, observaciones = validaFila.isValid()

                        if not esValido:
                            listStatus.append(observaciones)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue

                        grupo = fila["grupo"]
                        nombre = fila["nombre"]
                        
                        areabusq = db.query(GrupoTag).filter(or_(GrupoTag.grupo == grupo, GrupoTag.nombre == nombre)).first()
                        if areabusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunos grupos ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        statement = f"insert into grupotag(grupo, nombre) values('{grupo}','{nombre}');"
                        
                        
                        try:
                            db.execute(statement)
                            if tdi == "p":
                                db.commit()
                                listStatus.append("Insertado")
                            else:
                                listStatus.append("OK")
                        except BaseException as err: 
                            savelog(err) 
                            filasError +=1
                            listStatus.append("ERROR")
                    if tdi == "t":
                        if filasError == 0 and totFilas > 0:
                            db.commit()                    
                        elif filasError > 0 and totFilas > 0:
                            db.rollback()
                            msg = "Algunos grupos ya existen, descarga las observaciones"
                if totFilas > 0:            
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"s"})
                    df['status'] = pd.DataFrame(listStatus)
                    df.to_excel( f"{rutafile}{nombreArchivo}" ,index=False)
                else:
                    msg = "No se encontraron registros en el archivo proporcionado"
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})
                    os.remove(f"{rutafile}{nombreArchivo}")
                    
            except BaseException as err: 
                savelog(err) 
                msg = "El archivo no contiene la estructura esperada definida en la plantilla"
                listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})   
                os.remove(f"{rutafile}{nombreArchivo}")
                
        return {"listResult": listResult}
    raiseExceptionNoAuth(f"Acceso no autorizado")

