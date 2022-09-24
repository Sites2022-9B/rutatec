from genericpath import exists
import os
from fastapi.datastructures import UploadFile
import pandas as pd
from fastapi.params import File, Form
from sqlalchemy.sql.elements import or_
from sqlalchemy.sql.expression import false
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, getEmpleadoId, getSettingsName, hasPermisos, isDateBetweenTags, isDateExtremeTags, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth, savelog, tagExistIn
from modulos.shared_schemas import BusquedaYPaginacion
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session, aliased
from fastapi import APIRouter, Request, Depends, HTTPException, status
from typing import List, Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter( tags=['Puestos'] )

@router.get("/puestos")
async def show_C_View(request: Request, ret: str = "/puestos", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/puestos"
    pagina = "puestos.html"
    return accessPageValidate(url, pagina, session, db, request, ret)
    
@router.post('/api/puestos')
async def getPuesto(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        sql = '''SELECT p.id, p.clave, p.nombre, p.grupotag_id, p.fechaini, p.fechafin, gt.grupo 
                    FROM  ( SELECT *  FROM puestos ) p
                    JOIN grupotag gt ON gt.id = p.grupotag_id
                    '''
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'p.clave', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'p.nombre', 'like', busq.search, '')

        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= Puestos().getLabels(database)
        labels.append("Grupo")
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")
    
@router.post("/api/puestos/addpuesto")
async def addPuesto(puestoDado:PuestoAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/addpuesto'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = puestoDado.isValid()
        if esValido:
            existe_p = db.query(Puestos).filter(or_(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre)).first()
            if existe_p == None:
                datos = Puestos(**puestoDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
            existeClaveYNombre= db.query(Puestos.clave, Puestos.nombre).filter(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre).first()
            print("existe clave y nombre? ", existeClaveYNombre)
            if existeClaveYNombre != None:
                existeFechaPuesto = db.query(Puestos.fechaini, Puestos.fechafin).filter(or_(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre)).all()
                print("existe fecha add? ", existeFechaPuesto)
                if len(existeFechaPuesto) > 0:
                    if isDateBetweenTags(existeFechaPuesto, puestoDado.fechaini) == False:
                        if isDateBetweenTags(existeFechaPuesto, puestoDado.fechafin) == False:
                            if isDateExtremeTags(existeFechaPuesto, puestoDado.fechaini, puestoDado.fechafin) == False:
                                datos = Puestos(**puestoDado.dict())
                                datos.create(db)
                                return {"message": "Success!!!"}
                            raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
                        raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo vigente o sin finalizar.")
                    raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo vigente o sin finalizar.")
            else:
                claveUsada= db.query(Puestos.clave).filter(Puestos.nombre == puestoDado.nombre).first()
                if claveUsada != None:
                    nombreUsado = puestoDado.nombre
                    msgCN=f'El puesto {nombreUsado} esta registrado con la clave {claveUsada[0]}, por lo tanto debe utilizar la misma'
                else:
                    msgCN=f'La clave ya se uso para otro puesto'
            raiseExceptionDataErr(msgCN)
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/puestos/update")
async def updatePuesto(puestoDado:PuestoUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = puestoDado.isValid()
        if esValido:
            puestoAct = db.get(Puestos, puestoDado.id)
            existe_p = db.query(Puestos).filter(or_(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre)).filter(Puestos.id != puestoDado.id).first()
            if existe_p == None:
                p_data = puestoDado.dict(exclude_unset=False)
                for key, value in p_data.items():
                    setattr(puestoAct, key, value)
                puestoAct.update(db)
                return {"message": "Success!!!"}
            else:
                existeClaveYNombre= db.query(Puestos.clave, Puestos.nombre).filter(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre, Puestos.id != puestoDado.id).first()
                print("existe clave y nombre? ", existeClaveYNombre)
                if existeClaveYNombre != None:
                    existeFechaParaPuesto = db.query(Puestos.id, Puestos.fechaini, Puestos.fechafin).filter(or_(Puestos.clave == puestoDado.clave, Puestos.nombre == puestoDado.nombre)).filter(Puestos.id != puestoDado.id).all()
                    print("Existe fecha? ",existeFechaParaPuesto)
                    if existeFechaParaPuesto == None:
                        p_data = puestoDado.dict(exclude_unset=False)
                        for key, value in p_data.items():
                            setattr(puestoAct, key, value)
                        
                        puestoAct.update(db)
                        return {"message": "Success!!!"}
                    else:
                        #verificar si la fecha inicio está dentro de este periodo ya registrado
                        if isDateBetweenTags(existeFechaParaPuesto, puestoDado.fechaini) == False:
                            if isDateBetweenTags(existeFechaParaPuesto, puestoDado.fechafin) == False:
                                if isDateExtremeTags(existeFechaParaPuesto, puestoDado.fechaini, puestoDado.fechafin) == False:
                                    p_data = puestoDado.dict(exclude_unset=True)
                                    for key, value in p_data.items():
                                        setattr(puestoAct, key, value)
                                    
                                    puestoAct.update(db)
                                    return {"message": "Success!!!"}
                                raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
                            raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo vigente o sin finalizar.")
                        raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo vigente o sin finalizar.")
                else:
                    claveUsada= db.query(Puestos.clave).filter(Puestos.nombre == puestoDado.nombre).first()
                    if claveUsada != None:
                        nombreUsado = puestoDado.nombre
                        msgCN=f'El puesto {nombreUsado} esta registrado con la clave {claveUsada[0]}, por lo tanto debe utilizar la misma'
                    else:
                        msgCN=f'La clave ya se uso para otro puesto'
                raiseExceptionDataErr(msgCN)
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/puestos/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/uploadfiles'
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
        col_types = {"clave":str, "grupotag_id": str}
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
                        notas = ""
                        # verificar celdas vacías
                        print("fila: ", fila)
                        for clave, valor in fila.items():
                            if pd.isna(valor):
                                fila[clave] = ""

                        #si el campo grupotag está vacío estonces eliminarlo de la fila
                        if fila["grupotag_id"] == "":
                            del fila["grupotag_id"]
                        
                        #verificar que grupotag_id sea numerico y que exista en la BD
                        if "grupotag_id" in fila:
                            if not str(fila["grupotag_id"]).isdigit():
                                del fila["grupotag_id"]
                            else:
                                tag_existe = db.get(GrupoTag, fila["grupotag_id"])
                                if tag_existe == None:
                                    del fila["grupotag_id"]
                                    notas += "GRUPOTAG no encontrado"

                        # print("fila sin NAN", fila)
                        validaFila = PuestoAdd(**fila)
                        esValido, observaciones = validaFila.isValid()
                        
                        if not esValido:
                            listStatus.append(observaciones+notas)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue

                        codigoInsert = fila["clave"]
                        nombreInsert = fila["nombre"]
                        gtagInsert = fila["grupotag_id"]
                        
                        areabusq = db.query(Puestos).filter(or_(Puestos.clave == codigoInsert, Puestos.nombre == nombreInsert)).first()
                        if areabusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunos puestos ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        statement = f"insert into puestos (clave, nombre, grupotag_id) values('{codigoInsert}','{nombreInsert}','{gtagInsert}');"
                        
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
                            msg = "Algunos puestos ya existen, descarga las observaciones"
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

@router.get("/api/puestos/tags")
async def getTagsCombo(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/tags'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        tags = db.query(GrupoTag).order_by(GrupoTag.grupo).all()
        return {"tags": tags}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/puestos/combo")
async def getPuestosCombo(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/combo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        p, gt = aliased(Puestos), aliased(GrupoTag)
        # puestoList =  db.query(Puestos).order_by(Puestos.clave).all()
        puestoList = db.query(p.id, p.clave, gt.grupo, p.nombre).join(gt, gt.id == p.grupotag_id).order_by(gt.grupo).all()
        return {"puestos": puestoList}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/puestos/assign")
async def newPuestoEmp(puestoDado:PuestoEmpAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/assign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        print("puestoDado: ", puestoDado.user_id, puestoDado.puesto_id, puestoDado.fechaini, puestoDado.fechafin)
        # con id_user recuperar el empleado_id asociado
        empleado_id = getEmpleadoId(puestoDado.user_id, db)
        print("empleado_id: ", empleado_id)
        #verificar si existe un puesto "vigente" con el mismo grupoTAG,
        tags_p = tagExistIn(puestoDado.puesto_id, empleado_id, db)
        
        print("existe_p: ", tags_p)
        if len(tags_p) == 0:
            #crear un nuevo registro de puesto
            new_puestoemp = PuestoEmpleado(puesto_id = puestoDado.puesto_id, empleado_id = empleado_id, fechaini = puestoDado.fechaini, fechafin = puestoDado.fechafin)
            print("new_PuestoEmp: ", new_puestoemp)
            new_puestoemp.create(db)
            return {"message": "Nuevo puesto asignado"}  
        else:
            #verificar si la fecha inicio está dentro de este periodo ya registrado
            if isDateBetweenTags(tags_p, puestoDado.fechaini) == False:
                if isDateBetweenTags(tags_p, puestoDado.fechafin) == False:
                    if isDateExtremeTags(tags_p, puestoDado.fechaini, puestoDado.fechafin) == False:
                        new_puestoemp = PuestoEmpleado(puesto_id = puestoDado.puesto_id, empleado_id = empleado_id, fechaini = puestoDado.fechaini, fechafin = puestoDado.fechafin)
                        print("new_PuestoEmp: ", new_puestoemp)
                        new_puestoemp.create(db)
                        return {"message": "Nuevo puesto asignado"} 
                    raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
                raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo vigente o sin finalizar del mismo TIPO.")
            raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo vigente o sin finalizar del mismo TIPO.")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#establece fecha de fin de puesto actual..
@router.put("/api/puestos/finish")
async def putPuestoFinish(fin_puesto:PuestoEmpFinish, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/puestos/finish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        puesto_act = db.query(PuestoEmpleado).filter(PuestoEmpleado.id == fin_puesto.id_pe).first()
        print("puesto_act: ", puesto_act)
        if(puesto_act != None):
            puesto_act.fechafin = fin_puesto.fechafin
            puesto_act.update(db)
            return {"message", "success"}
        raiseExceptionDataErr(f"el puesto no fue encontrado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

