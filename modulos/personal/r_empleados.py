from genericpath import exists
import os
from fastapi.datastructures import UploadFile
import pandas as pd
from fastapi.params import File, Form
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql.elements import or_
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_schemas import BusquedaYPaginacion
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import List, Tuple
from starlette.responses import RedirectResponse
from modulos.shared_defs import accessPageValidate, getPermisos, getSettingsName, hasPermisos, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth, savelog

router = APIRouter( tags=['Empleados'] )


@router.get("/empleados")
async def show_E_View(request: Request, ret: str = "/empleados", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    
    url = "/empleados"
    pagina = "empleados.html"
    return accessPageValidate(url, pagina, session, db, request, ret)

@router.post('/api/empleados')
async def getEmpleadosTable(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        sql = 'select * from empleados'
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'codigo', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'nombre', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'apepat', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'apemat', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'nss', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'curp', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'rfc', 'like', busq.search, '')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= Empleado().getLabels(database)
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Permiso denegado")

@router.post("/api/empleados/addempleado")
async def addEmpleado(empleadoDado:EmpleadoAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/addempleado'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = empleadoDado.isValid()
        if esValido:
            existe_e = db.query(Empleado).filter(or_(Empleado.codigo == str(empleadoDado.codigo), Empleado.nss == empleadoDado.nss, 
                        Empleado.curp == empleadoDado.curp, Empleado.rfc == empleadoDado.rfc)).first()
            if existe_e == None:
                datos = Empleado(**empleadoDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"El código, NSS, CURP o RFC ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/empleados/update")
async def updateEmpleado(empleadoDado:EmpleadoUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        empAct = db.get(Empleado, empleadoDado.id)
        esValido, observaciones = empleadoDado.isValid()
        if esValido:
            existe_e = db.query(Empleado).filter(or_(Empleado.codigo == empleadoDado.codigo, Empleado.nss == empleadoDado.nss, 
                        Empleado.curp == empleadoDado.curp, Empleado.rfc == empleadoDado.rfc)).filter(Empleado.id != empleadoDado.id).first()
            if existe_e == None:
                emp_data = empleadoDado.dict(exclude_unset=True)
                for key, value in emp_data.items():
                    setattr(empAct, key, value)
                
                empAct.update(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"El código, NSS, CURP o RFC ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/empleados/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/uploadfiles'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        listResult = []
        rutaDePlantillasUploads = getSettingsName("$SYS_DIR_MODELS_PLANTILLAS_UPLOADS", "/f/models_plantillas_uploads")
        rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/"
        # crear el directorio en caso de que no exista
        if not exists(rutafile):
            os.makedirs(rutafile)
        
        fhms = datetime.today().strftime("%Y%m%d%H%M%S%f")
        # cuando el excel tiene columnas de tipo text/string pero contienen numeros y se desea que se mantengan como text/string
        col_types = {"codigo":str, "nss":str, "telefono":str}
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
                    # print(df.iterrows())
                    for indice, fila in df.iterrows():
                        totFilas += 1
                        # verificar celdas vacías
                        for clave, valor in fila.items():
                            if pd.isna(valor):
                                fila[clave] = ""

                        # print("fila sin NAN", fila)
                        validaFila = EmpleadoAdd(**fila)
                        print(validaFila)
                        esValido, observaciones = validaFila.isValid()

                        if not esValido:
                            listStatus.append(observaciones)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue

                        codigo = fila["codigo"].zfill(6)
                        nombre = fila["nombre"]
                        ap = fila["apepat"]
                        am = fila["apemat"]
                        sex = fila["sexo"]
                        nss = fila["nss"]
                        curp = fila["curp"]
                        rfc = fila["rfc"]
                        tel = fila["telefono"]
                        dom = fila["domicilio"]
    
                        areabusq = db.query(Empleado).filter(or_(Empleado.codigo == codigo, Empleado.nss == nss, Empleado.curp == curp, Empleado.rfc == rfc)).first()
                        if areabusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunos empleados ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        
                        statement = f"""insert into empleados (codigo, nombre,apepat, apemat, sexo, nss, curp, rfc, telefono, domicilio) 
                                        values('{codigo}','{nombre}','{ap}','{am}','{sex}','{nss}','{curp}','{rfc}','{tel}','{dom}');"""
                        
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
                            msg = "Algunos empleados ya existen, descarga las observaciones"
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
    
@router.get("/api/empleados/combo")
async def getEmpleadosCombo(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/combo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        e, ue = aliased(Empleado), aliased(UserEmpleado)
        emp_list = db.query(e.id, e.codigo, e.nombre, e.apepat, e.apemat, ue.user_id).outerjoin(ue, ue.empleado_id == e.id).all()
        return {"lista_emp":emp_list}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#asocia un usuario a un empleado
@router.post("/api/empleados/assign")
async def addUserEmpleado(userEmpDado:UserEmpAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/assign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        existe_e = db.query(UserEmpleado).filter(UserEmpleado.empleado_id == userEmpDado.empleado_id).first()
        if existe_e == None:
            datos = UserEmpleado(**userEmpDado.dict())
            datos.create(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El empleado ya está asignado a otro usuario, favor de verificar")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#cambia el empleado asociado a un usuario
@router.put("/api/empleados/change")
async def updateUserEmpleado(userEmpDado:UserEmpUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/empleados/change'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        ue_act = db.get(UserEmpleado, userEmpDado.id_ue)
        if(ue_act != None):
            existe_e = db.query(UserEmpleado).filter(UserEmpleado.empleado_id == userEmpDado.empleado_id).filter(UserEmpleado.id != userEmpDado.id_ue).first()
            if existe_e == None:
                ue_act.empleado_id = userEmpDado.empleado_id
                ue_act.update(db)
                return {"message", "success"}
            raiseExceptionDataErr(f"El empleado ya está asignado a otro usuario, favor de verificar")
        raiseExceptionDataErr(f"El registro a actualizar no fue encontrado")
    raiseExceptionNoAuth(f"Acceso no autorizado")
