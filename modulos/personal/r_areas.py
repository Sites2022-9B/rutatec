from ast import Try
from genericpath import exists
import os
from fastapi.datastructures import UploadFile
import pandas as pd
from fastapi.params import File, Form
from sqlalchemy import false, true
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql.elements import or_
from sqlalchemy.sql.functions import coalesce
from modulos.proc_comision.models import Com
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, getEmpleadoId, getSettingsName, isDateBetween, isDateBetweenTags, isDateExtremeTags, isPeriodBetween, prepParam, prepParamBetween, raiseExceptionDataErr, raiseExceptionNoAuth, hasPermisos, raiseExceptionSinPrivilegios, savelog
from modulos.shared_schemas import BusquedaYPaginacion
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import List, Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter( tags=['Areas'] )

def validateDates(lista,objrecibido,db,mensj):
    if isDateBetweenTags(lista, objrecibido.fechaini) == False:
        if isDateBetweenTags(lista, objrecibido.fechafin) == False:
            if isDateExtremeTags(lista, objrecibido.fechaini,objrecibido.fechafin) ==False:
                datos = AreaResponsable(**objrecibido.dict())
                datos.create(db)
                return true
            raiseExceptionDataErr(f"{mensj} Se encontraron periodos dentro del rango de fechas indicadas.")
        raiseExceptionDataErr(f"{mensj} La fecha de FIN está dentro de un periodo vigente o sin finalizar.")
    raiseExceptionDataErr(f"{mensj} La fecha de INICIO está dentro de un periodo vigente o sin finalizar.")

@router.get("/areas")
async def show_U_View(request: Request, ret: str = "/areas", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    
    url = "/areas"
    pagina = "areas.html"
    return accessPageValidate(url, pagina, session, db, request, ret)

@router.post('/api/areas')
async def getAreasTable(busq: BusqFecha, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        fecha = ""
        if(busq.fechabus==''):
            fecha = datetime.today().strftime('%Y-%m-%d')
        else:
            fecha = busq.fechabus
        sql = f"""SELECT are.id, are.codigo, are.subarea, are.areasuperior, are.telefonos, are.areapadre_id, are.emplead, are.periodovig, are.revisor, are.lugar_id, are.lugar, string_agg(are.tipo,',') FROM
            (SELECT a.id, a.codigo, a.nombre subarea, a2.nombre areasuperior, a.telefonos, a.areapadre_id ,coalesce(ap.nombreemp,'Sin asignar') emplead, 
            coalesce((ap.fechaini || ' - ' || coalesce(cast(ap.fechafin AS varchar),'Vigente')),'Sin asignar') periodovig, a.revisor, a.lugar_id, l.lugar, coalesce(ar.tipo,'Sin asignar')tipo 
            FROM(SELECT * FROM areas )a 
            LEFT JOIN arearesponsable_get_vw ap ON a.id = ap.area_id AND '2022-01-1' BETWEEN date(fechaini) AND coalesce(date(fechafin),'2999-10-16')
            LEFT JOIN areas a2 ON a2.id = a.areapadre_id 
            LEFT JOIN lugares l ON l.id = a.lugar_id
            LEFT JOIN areatipo ar ON ar.area_id = a.id
            )are
            """
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'are.codigo', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'are.subarea', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '','are.areasuperior', 'like', busq.search, '')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        sql +="GROUP BY are.id, are.codigo, are.subarea, are.areasuperior, are.telefonos, are.areapadre_id, are.emplead, are.periodovig, are.revisor, are.lugar_id, are.lugar"
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        return {"labels":['ID','CODIGO','ÁREA','AREA SUPERIOR','TELEFONOS', '2' , 'RESPONSABLE ACT', 'FECHA VIGENCIA','Revisor', '','LUGAR', 'TIPO'], "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Permiso denegado")

@router.get('/api/areatipo/{area_id}')
async def getareatipo(area_id: int,session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areatipo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url)):
        sql = f'''SELECT * FROM areatipo WHERE area_id = {area_id}'''
        cond = ''
        sqlParams = {}
        if ( len(cond)>0 ) : sql = f"{sql}"  # -4 = len("and ")
        metadata, rows = database.execSql(sql, sqlParams, False, True)
        print(rows)
        return {"metadata" : metadata, "data":rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")

def validacionAreaTipo(db,areaDado):
    addArea = False
    for i in range(len(areaDado.numeroRO)):
        if areaDado.tipoRO[i]=='R':
            existe_t = db.query(Areatipo).filter(Areatipo.num==areaDado.numeroRO[i],Areatipo.tipo==areaDado.tipoRO[i]).first()
            print(areaDado.areapadre_id)
            if existe_t==None:
                addArea = True
            else:
                addArea = False
                break
        else:
            sql = f"""
            SELECT a.id,a.nombre FROM 
            (
                SELECT area_id FROM areatipo WHERE num='{areaDado.numeroRO[i]}' and tipo='O'
            )at
            JOIN areas a ON at.area_id = a.id"""
            if areaDado.areapadre_id!=None:
                sql += f""" and a.areapadre_id = {areaDado.areapadre_id}"""
            if areaDado.areapadre_id==None:
                sql += f""" and a.areapadre_id is null"""
            if areaDado.id!=None:
                sql += f""" AND a.id!={areaDado.id}"""
            sqlParams = {}
            cond = ""
            if ( len(cond)>0 ) : sql = f"{sql}"  # -4 = len("and ")
            metadata, rows = database.execSql(sql, sqlParams, False, True)
            if rows!=[]:
                addArea = False
                break
            else:
                addArea = True
    return addArea


@router.post("/api/areas/addarea")
async def addArea(areaDado:AreaAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/addarea'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = areaDado.isValid()
        if esValido:
            existe_g = db.query(Area).filter(or_(Area.codigo == areaDado.codigo, Area.nombre == areaDado.nombre)).first()
            if existe_g == None:
                valArea = validacionAreaTipo(db,areaDado)
                if valArea:
                    try:
                    # if existe_r == None:
                        print('entro al if')
                        trans = db.begin_nested()
                        AreaR = Area(
                            codigo = areaDado.codigo,
                            nombre = areaDado.nombre,
                            areapadre_id = areaDado.areapadre_id,
                            telefonos = areaDado.telefonos,
                            revisor = areaDado.revisor,
                            lugar_id = areaDado.lugar_id
                        )
                        AreaR.addtrans(db)
                        Rareas = db.query(Area.id).filter(Area.codigo == areaDado.codigo ,Area.nombre == areaDado.nombre).first()
                        print('Debe ser id del Area',Rareas[0])
                        for i in range(len(areaDado.numeroRO)):
                            campostipo = Areatipo(
                                area_id = Rareas[0],
                                num = areaDado.numeroRO[i],
                                tipo = areaDado.tipoRO[i]
                            )
                            db.add(campostipo)
                        existe_r = db.query(Area.id,Area.revisor).filter(Area.revisor==areaDado.revisor).first()
                        print('ACa caca',existe_r[0])
                        print('existe_r', existe_r)
                        if existe_r != None:
                            print('entro al if de existe_r')
                            revisorUp = db.get(Area, existe_r[0])
                            revisorUp.revisor = None
                            db.add(revisorUp)
                        trans.commit()
                        db.commit()
                    except BaseException as err:
                        trans.rollback()
                        db.commit() 
                        print (err)
                        raiseExceptionDataErr(f"Error al crear el área")
                    return {"message": "Success!!!"}
                raiseExceptionDataErr(f"El número del Área ya esta repetido")
            raiseExceptionDataErr(f"El código o el nombre de área ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

#nuevo Entry Point para desplegar en otra página los datos de areas
@router.get("/responsables/details/{id_area}")
async def showAreaDetailsView(request: Request, id_area:int, ret: str = "/areas", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    area_db = db.query(Area).filter(Area.id == id_area).first()
    url = "/areas/"
    pagina = "area_responsable.html"
    return accessPageValidate(url, pagina, session, db, request, ret, id_area = str(id_area), n_area = area_db.nombre)

@router.put("/api/areas/update")
async def updateArea(areaDado:AreaAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = areaDado.isValid()
        if esValido:
            areaAct_editar = db.get(Area, areaDado.id)
            print('is valid', areaAct_editar)
            existe_a = db.query(Area).filter(or_(Area.codigo == areaDado.codigo, Area.nombre == areaDado.nombre)).filter(Area.id != areaDado.id).first()
            print('is valid 2', existe_a)
            if existe_a == None:
                valArea = validacionAreaTipo(db,areaDado)
                if valArea:
                    print('Entró al None')
                    trans = db.begin_nested()
                    try:
                        print('Entró al try')
                        areaAct_editar.codigo = areaDado.codigo,
                        areaAct_editar.nombre = areaDado.nombre,
                        areaAct_editar.areapadre_id = areaDado.areapadre_id,
                        areaAct_editar.telefonos = areaDado.telefonos,
                        areaAct_editar.revisor = areaDado.revisor,
                        areaAct_editar.lugar_id = areaDado.lugar_id
                        areaAct_editar.addtrans(db)
                        print('Se recupera el id del registro')
                        Rareas = db.query(Area.id).filter(Area.codigo == areaDado.codigo ,Area.nombre == areaDado.nombre).first()
                        print('Rareas',Rareas[0])
                        for i in range(len(areaDado.tipoRO)):
                            print('i', i)
                            print('Entró al range')
                            if(areaDado.operacionArea[i] == 'Delete'):
                                print('Entró al Delete')
                                eliminarRecor = db.get(Areatipo, areaDado.idtabla[i])
                                # print('Entró al Delete', eliminarRecor.id)
                                db.delete(eliminarRecor)
                            elif(areaDado.operacionArea[i] == 'BD'):
                                print('Entró al BD')
                                print('idtabla', areaDado.idtabla[i])
                                print('Operacion', areaDado.operacionArea[i])
                                # print('areaRO', areaDado.areaRO[i])

                                idartipo = db.get(Areatipo, areaDado.idtabla[i])
                                # print('idartipo', 'idartipo[0]', idartipo[0])
                                print('idartipo', idartipo.id, idartipo.area_id, idartipo.num, idartipo.tipo)
                                setattr(idartipo, 'area_id', areaDado.areaRO[i])
                                print('areaRO', areaDado.areaRO[i])
                                setattr(idartipo, 'num', areaDado.numeroRO[i])
                                print('numRO', areaDado.numeroRO[i])
                                setattr(idartipo, 'tipo', areaDado.tipoRO[i])
                                print('tipoRO', areaDado.tipoRO[i])
                                idartipo.addtrans(db)
                                print('Pasó el add')
                            elif(areaDado.operacionArea[i] == 'N'):
                                # print('Entró al N')
                                campostipo = Areatipo(area_id = Rareas[0],num = areaDado.numeroRO[i],tipo = areaDado.tipoRO[i])
                                campostipo.addtrans(db)
                        print('Pasó todo los if')
                        trans.commit()
                        db.commit() 
                    except BaseException as err:
                        trans.rollback()
                        db.commit() 
                        raiseExceptionDataErr(f"Error al actualizar el área")
                    return {"message": "Success!!!"}
                raiseExceptionDataErr(f"El número del área ya existe")
            raiseExceptionDataErr(f"El código o el nombre ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

#Api que retorna los datos de los responsables
@router.get("/api/areas/datosresponsables/{id_area}")
async def getArea(id_area: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/datosresponsables'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        responsable_query = db.query(Area.id, Area.codigo, Area.nombre).filter(Area.id == id_area).first()
        if(responsable_query != None):
            return {"responsable": responsable_query}
        raiseExceptionDataErr(f"El responsable consultado no existe")
    raiseExceptionNoAuth(f"Acceso no autorizado")


#Agrega un nuevo responsable de area
@router.post("/api/areas/responsables/addresponsables")
async def addAreaRes(AreaResDado:AreaResAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/responsables/addresponsables'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones= AreaResDado.isValid()
        if esValido:
            emp_encontrado = false
            ar = aliased(AreaResponsable)
            tabArearesList = db.query(ar.area_id,ar.empleado_id,ar.fechaini,ar.fechafin).filter(ar.area_id==AreaResDado.area_id).all()
            print("no se que es ",tabArearesList) 
            areaem = db.query(ar.fechaini,ar.fechafin).filter(ar.area_id==AreaResDado.area_id).all()
            print("areaem",areaem)
            for fila in tabArearesList:
                if fila[1] == AreaResDado.empleado_id:
                    emp_encontrado = true
                    break
            if emp_encontrado == false:
                print(areaem)
                if len(areaem) == 0:
                    resultado = validateDates(tabArearesList,AreaResDado,db,"")
                    if resultado:
                        return {"message": "Success!!!"}
                else:
                    resultado = validateDates(areaem,AreaResDado,db,"ya existe un usuario en esta área, ")
                    if resultado:
                        return {"message": "Success!!!"}
            else:
                if isDateBetweenTags(tabArearesList, AreaResDado.fechaini) == False:
                    if isDateBetweenTags(tabArearesList, AreaResDado.fechafin) == False:
                        if isDateExtremeTags(tabArearesList, AreaResDado.fechaini,AreaResDado.fechafin)==False:
                            if len(areaem) == 0:
                                datos = AreaResponsable(**AreaResDado.dict())
                                datos.create(db)
                                return {"message": "Success!!!"}
                            else:
                                resultado = validateDates(areaem,AreaResDado,db,"El usuario ya existe en otra área.")
                                if resultado:
                                    return {"message": "Success!!!"}
                        raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
                    raiseExceptionDataErr(f"La fecha de FIN debe de estar fuera de un periodo ya registrado")
                raiseExceptionDataErr(f"La fecha de INICIO debe de estar fuera de un periodo ya registrado")       
        raiseExceptionDataErr(observaciones)    
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/areas/responsables/updateresponsables")
async def updateAreaRes(AreaResDado:AreaResUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/responsables/updateresponsables'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        arearesAct = db.get(AreaResponsable, AreaResDado.id)
        esValido, observaciones = AreaResDado.isValid()
        if esValido:
            arearesAct.fechafin = AreaResDado.fechafin
            arearesAct.update(db)
            return {"message":"Success!!!"}
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post('/api/areas/responsables')
async def getResponsables(request:Request, busq: busqAreaRes, ret: str = "/areas", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/responsables'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        sql = f"SELECT * FROM arearesponsable_get_vw" 
        cond = ''
        sqlParams = {}  
        cond += prepParam(sqlParams, '', 'area_id', '=', busq.id_area, 'and')     
        cond += prepParam(sqlParams, '', 'nombreemp', 'like', busq.search, 'and')
        busq.validarPaginacion()
        if (len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"
        sql = f'{sql} ORDER by fechaini DESC'
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        # labels= AreaResponsable().getLabels(database)
        labels = ["Id", "area_id" ,"empleado_id", "Nombre", "Fecha Inicial", "Fecha Final"]
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

def getRespArea(q_arearesp_id, listaAcumResponsablesVigentes, q_fechadada:str, area_idDada: int, empleado_idDado: int, q_revisor, q):
    sql = f"""
        Select ar.id
        , e.nombre || ' ' || e.apepat || ' ' || e.apemat || ' [' || a.codigo || ': ' || ar.fechaini || ' - ' || coalesce( cast(ar.fechafin as varchar) ,'...') ||']' AS responsable
        , '' disponible, ar.empleado_id, a.areapadre_id
        From arearesponsable ar
        left join areas a on a.id = ar.area_id
        left join empleados e on e.id = ar.empleado_id
        """
    cond = ""
    sqlParams = {}    
    if q_arearesp_id:
        cond += prepParam(sqlParams, '', 'ar.id', '=', q_arearesp_id, 'and')
    else:
        if area_idDada != 0:
            cond += prepParam(sqlParams, '' , 'area_id', '=', area_idDada, 'and')
        cond += prepParam(sqlParams, '' , 'a.revisor', '=', q_revisor, 'and')
        cond += prepParam(sqlParams, '(', 'e.nombre', 'like', q, 'or')
        cond += prepParam(sqlParams, '' , 'e.apepat', 'like', q, 'or')
        cond += prepParam(sqlParams, '' , 'e.apemat', 'like', q, ') or')
        if q_fechadada:            
            cond += f""" '{q_fechadada}' between ar.fechaini and coalesce(ar.fechafin, date(now() +'100 day')) and"""
    if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
    sql += " order by ar.fechaini desc, e.nombre asc"
    [metadata, rows] = database.execSql(sql, sqlParams, False, True)
    if rows:
        # Verificar si el comisionado es igual al responsable de área
        # si es así, entonces obtener nuevamente el responsable del área padre siempre y cuando exista
        empleado_id = rows[0][ metadata.index("empleado_id") ]
        areapadre_id = rows[0][ metadata.index("areapadre_id") ]
        if empleado_id == empleado_idDado and areapadre_id:
            getRespArea( q_arearesp_id, listaAcumResponsablesVigentes, q_fechadada, areapadre_id, empleado_idDado, "", q )
        else:
            for row in rows:
                rowtoAppend = [row[0], row[1], row[2] ]
                listaAcumResponsablesVigentes.append( rowtoAppend )


@router.get("/api/areas/responsables/combo")
async def getAreasResponsablesCombo( q_area_id:int=0, q_categoriacomisionado_id:str="", q:str="", q_arearesp_id:str="", q_revisor:str="", q_fechadada:str="", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    """
    Se retorna la lista de responsables de área, de acuerdo a los parámetros proporcionados
    ya sea que se indique: el id de la tabla principal, o bien: el revisor, el area_id, o una fecha dada
    """
    url = "/api/areas/responsables/combo"
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if (userAutentificado):
        empleado_id = ""
        if q_categoriacomisionado_id:
            objEmpleado = db.query(PuestoEmpleado.empleado_id).filter(PuestoEmpleado.id == q_categoriacomisionado_id).first()
            empleado_id = objEmpleado.empleado_id
        listaAcumResponsablesVigentes = []
        getRespArea(q_arearesp_id, listaAcumResponsablesVigentes, q_fechadada, q_area_id, empleado_id, q_revisor, q )
        return {'data':listaAcumResponsablesVigentes}
    raiseExceptionNoAuth(f"Acceso no autorizado")


@router.post("/api/areas/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/uploadfiles'
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
        col_types = {"codigo":str}
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
                        validaFila = AreaAdd(**fila)
                        esValido, observaciones = validaFila.isValid()
                        if not esValido:
                            listStatus.append(observaciones)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue
                        codigoInsert = fila["codigo"]
                        nombreInsert = fila["nombre"]
                        
                        areabusq = db.query(Area).filter(or_(Area.codigo == codigoInsert, Area.nombre == nombreInsert)).first()
                        if areabusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunas areas ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        statement = f"insert into areas (codigo, nombre) values('{codigoInsert}','{nombreInsert}');"
                        
                        try:
                            db.execute(statement)
                            if tdi == "p":
                                db.commit()
                                listStatus.append("Insertado")
                            else:
                                listStatus.append("OK")
                        except:
                            filasError +=1
                            listStatus.append("ERROR")
                    if tdi == "t":
                        if filasError == 0 and totFilas > 0:
                            db.commit()                    
                        elif filasError > 0 and totFilas > 0:
                            db.rollback()
                            msg = "Algunas areas ya existen, descarga las observaciones"
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
    

@router.get("/api/areas/combo")
async def getAreasCombo(q:str="", q_area_id:str="",filtro_proy:str="T", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/combo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        cond = ""
        sqlParams = {}
        if(filtro_proy!="T"):
            sql = f"""
            SELECT a.id,(at.num||' - '||a.descr) as descr FROM 
            (
                select id, (nombre || ' (' || codigo || ')') as descr 
                From areas WHERE id = {filtro_proy} OR areapadre_id = {filtro_proy}
            )a
            LEFT JOIN areatipo at ON at.area_id = a.id and at.tipo = 'O'
            order by at.num
            """
        else:
            sql = f"select id, (nombre || ' (' || codigo || ')') as descr from areas"
            cond += prepParam(sqlParams, '', 'id', '=', q_area_id, 'and')
            cond += prepParam(sqlParams, '(', 'nombre', 'like', q, 'or')
            cond += prepParam(sqlParams, ' ', 'codigo', 'like', q, ') or')
        if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
        [metadata, rows] = database.execSql(sql, sqlParams, False, True)
        return {'metadata': metadata, 'data': rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/areas/assign")
async def newAreaEmpleado(areaDado:AreaEmpAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/assign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        print("areaDado: ", areaDado.user_id, areaDado.area_id, areaDado.fechaini, areaDado.fechafin)
        # con id_user recuperar el empleado_id asociado
        empleado_id = getEmpleadoId(areaDado.user_id, db)
        print("empleado_id: ", empleado_id)
        #verificar si la fecha inicio está dentro de un periodo ya registrado para un empleado especifico.
        f_ini_entre = isDateBetween(areaDado.fechaini, empleado_id, db)
        print("f_ini_entre: ", f_ini_entre)
        # verifica que f_ini no esté dentro de un periodo ya registrado.
        if len(f_ini_entre) == 0:
            f_fin_entre = isDateBetween(areaDado.fechafin, empleado_id, db)
            print("f_fin_entre: ",f_fin_entre)
            # verifica que f_fin no esté dentro de un periodo ya registrado.
            if len(f_fin_entre) == 0:
                #verificar que no haya registros entre f_ini y f_fin, si f_fin == None -> hoy+10 años
                periodo_entre = isPeriodBetween(areaDado.fechaini, areaDado.fechafin, empleado_id, db)
                print("periodo_entre: ",periodo_entre)
                if len(periodo_entre) == 0:
                    #crear un nuevo registro de area de adscripción con f_fin = Null
                    new_AreaEmp = AreaEmpleado(area_id = areaDado.area_id, empleado_id = empleado_id, fechaini = areaDado.fechaini, fechafin = areaDado.fechafin)
                    print("New_AreaResp: ", new_AreaEmp)
                    new_AreaEmp.create(db)
                    return {"message": "Nueva adscripción registrada"}
                raiseExceptionDataErr(f"Se encontraron periodos registrados entre las fechas indicadas.")
            raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo registrado, indica otra fecha de FIN.")
        raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo ya registrado o sin finalizar.")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#establece fecha de fin de adscripción..
@router.put("/api/areas/finish")
async def putUserAreaFinish(fin_area: AreaEmpFinish, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/areas/finish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        area_act = db.get(AreaEmpleado, fin_area.id_ar)
        if(area_act != None):
            area_act.fechafin = fin_area.fechafin
            area_act.update(db)
            return {"message", "success"}
        raiseExceptionDataErr(f"El área no fue encontrada")
    raiseExceptionNoAuth(f"Acceso no autorizado")
