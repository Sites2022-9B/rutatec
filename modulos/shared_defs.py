import os
import json
from os.path import exists
import sys
import traceback
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
import pandas as pd
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql.elements import and_, between, or_
from sqlalchemy.sql.functions import coalesce
from modulos.personal.models import *
from modulos.seguridad.models import *
# from modulos.shared_models import Settings
# Importar losschemas del PIDE a pesar de que no se utilicen de forma directa, sino mas bien de forma indirecta por
# la importación desde archivos de excel
from db import database
from routers.plantillas import templates
from datetime import date, datetime
from fastapi import status, HTTPException
from fastapi.responses import FileResponse
import logging
def getFilenamesAndPathFromMembreteGral(idReporteSolicitado, fechaDelRepParaBuscarElFtoaplicable):
    """
    Función empleada por las clases genéricas de reportes.
    Obtener los nombres de los archivos que corresponden al id del Reporte solicitado y a la fecha dada para filtrar
    el formato del membrete general del reporte que sea aplicable a esa fecha
    """
    sql = f"""
        Select r.id, r.nombredoc, rmg.id repmembretegral_id, rmg.header, rmg.fondo, rmg.footer, rmg.fechaini, rmg.fechafin
        From rep r 
        left join repmembretegral rmg on rmg.reptipo_id = r.reptipodoc_id 
            and '{fechaDelRepParaBuscarElFtoaplicable}' between rmg.fechaini and coalesce (rmg.fechafin, date(now() + '1000 day'))
        where rmg.id is not null and r.id = {idReporteSolicitado}
    """
    sqlParams = {}
    [metadata, rows] = database.execSql(sql, sqlParams, False, True)
    filenameHeader = "not_found.png"
    filenameFondo = "not_found.png"
    filenameFooter = "not_found.png"
    if rows:
        filenameHeader = rows[0][3]
        filenameFondo = rows[0][4]
        filenameFooter = rows[0][5]
    # print (filenameHeader)
    # 2.- Verificar que existan los nombres de los archivos a ser aplicados en el reporte según la ruta especificada
    rutaDePlantillasUploads = getSettingsName("$SYS_DIR_REPORTES_PLANTILLAS", "/f/reportes_plantillas")
    rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/"
    # Crear el directorio en caso de que no exista
    if not exists(rutafile):
        os.makedirs(rutafile)
    if not exists(f"{rutafile}{filenameHeader}"): filenameHeader = ""
    if not exists(f"{rutafile}{filenameFondo}"): filenameFondo = ""
    if not exists(f"{rutafile}{filenameFooter}"): filenameFooter = ""

    # fhms = datetime.today().strftime("%Y%m%d%H%M%S%f")
    # print(fhms)
    return rutafile, filenameHeader, filenameFondo, filenameFooter


def getFieldsUserCanEditExcept(claseDada, fieldListUserCanNotEdit):
    """En la ejecución de cada actividad de un proceso, el usuario podrá editar solo un conjunto de datos 
    presentados en cada trámite, por lo que este método retorna esa lista de campos"""
    listaDeCampos = claseDada.__fields__
    fieldList = []
    for fieldName in listaDeCampos:
        # print(fieldName)
        if (not fieldName in fieldListUserCanNotEdit):
            fieldList.append(fieldName)
    return fieldList


async def uploadFilesS1En(rutaDePlantillasUploads, files):
    """
    Almacenar el archivo recibido en la ruta especificada
    """
    rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/"
    # crear el directorio en caso de que no exista
    if not exists(rutafile):
        os.makedirs(rutafile)
    fhms = datetime.today().strftime("%Y%m%d%H%M%S%f")
    # print(fhms)
    listResult = []
    for file in files:
        nombreArchivo = f"{fhms}_{file.filename}"
        msg=""
        try:
            with open(f"{rutafile}{nombreArchivo}", "wb") as myfile:
                content = await file.read()
                myfile.write(content)
                myfile.close()
                file.filename = nombreArchivo
        except (FileNotFoundError, KeyError, ValueError) :
            msg = "Se presentaron errores al recibir el archivo... Reinténtelo nuevamente..."
            listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})            
            os.remove(f"{rutafile}{nombreArchivo}")
            return {"listResult": listResult}
    return listResult, rutafile, nombreArchivo

def uploadFilesS2ImportData(fnEspecifica, listResult, db, rutafile, nombreArchivo, col_types, datos):
    """
    Importar los datos del archivo de excel y retornar el resultado obtenido 
    """
    totFilas = 0
    try:                
        df = pd.read_excel(f"{rutafile}{nombreArchivo}", dtype=col_types)
        # Call fnEspecífica de proceamiento de filas de excel
        #  ----------------------------------------------------
        msg, totFilas, listStatus = fnEspecifica(df, db, datos)
        #  ----------------------------------------------------
        if totFilas > 0:
            listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"s"})
            df['status'] = pd.DataFrame(listStatus)
            df.to_excel( f"{rutafile}{nombreArchivo}", index=False)
        else:
            msg = "No se encontraron registros empleando la plantilla esperada!!!"
            listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})
    except: # (FileNotFoundError, KeyError, ValueError, IntegrityError) :
        msg = "El archivo no contiene la estructura esperada definida en la plantilla (verifique que no hayan filas vacias)"
        listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})            
        os.remove(f"{rutafile}{nombreArchivo}")
    return {"listResult": listResult}

def uploadFilesS3getDataForAlchemyAndSql(claseDada, tablaBD, listaDeValores, dicValoresAdicionales):
    """Retornar un obj de forma dinámica, rellenando sus campos con la listaDeValores 
    (encontrados en una fila del archivo de Excel), al mismo tiempo,
    Preparar la consulta insert con la lista de campos y la lista de valores proporcionados
    y se retornan en los parámetros: sqlParams y sqlInsert 
    (Nota. Estas variables por ser al menos arreglos (no tipos primitivos), los cambios aquí aplicados son retornados al exterior)
    """
    sqlParams = {} # Prevenir sqlInjection y permitir trabajar con textos amplios
    statement = []
    listaDeCampos = claseDada.__fields__.keys()
    strListaCampos = ""
    strListaParams = ""
    nomClase = claseDada.__name__
    objDado = None
    try:
        objDado = globals()[ nomClase ] #(sqlParams)
        # objDado = eval( f"{claseDada.__module__}.PidemetaBase()" )
        for fieldName in listaDeCampos:
            try:
                valor = listaDeValores[fieldName]
                sqlParams[fieldName] = valor
                strListaCampos += f"{fieldName}, "
                strListaParams += f":{fieldName}, "
                setattr(objDado, fieldName, valor)
            except:
                continue
        # Anexar los datos adicionales al item a devolver
        for item in dicValoresAdicionales:
            fieldName = item[0]
            valor = item[1]
            existAtrib = [campo for campo in listaDeCampos if campo == fieldName]
            if existAtrib:
                sqlParams[fieldName] = valor
                strListaCampos += f"{fieldName}, "
                strListaParams += f":{fieldName}, "
                setattr(objDado, fieldName, valor)
            else:
                print (f"Dev: No existe el campo [{fieldName}] en el schema [{nomClase}], verifica esta situación y elimina todos los campos innecesarios !!!")
        statement.append ( f"insert into {tablaBD} ( {strListaCampos[0:-2]} ) values( {strListaParams[0:-2]} );" )
    except:
        print (f"Dev: Para esta funcionalidad se requiere hacer el import del schema requerido: [{nomClase}]")
    return objDado, sqlParams, statement
    
def uploadFilesS4validarObjAlchemyAndDoInsert(db, objDadoOK, sqlParams, statement, tdi, listStatus, msg, filasError, validarTDIp):
    esValido, observaciones = objDadoOK.isValid()
    idNvoReg = None
    if observaciones:
        listStatus.append(observaciones)
        msg = "Se presentaron algunos errores"
        filasError +=1
    else:
        try:
            result = db.execute(statement, sqlParams)
            idNvoReg = result.lastrowid
            if validarTDIp and tdi == "p": # Parcial
                db.commit()
                listStatus.append("Insertado")
            else:
                listStatus.append("OK")
        except BaseException as err:
            print('An exception occurred: {}'.format(err))
            filasError +=1
            listStatus.append("ERROR")
    return listStatus, msg, filasError, idNvoReg

def addObservInProcexec(procexec_id, procactexec_id, user_id, db, observaciones):
    objPe = db.query(Procexec).filter(Procexec.id == procexec_id ).first()
    empleado = getEmpleadoDatos(user_id, db)
    procactid = db.query(Procactexec).filter(Procactexec.id == procactexec_id).first()
    print('PROC ACT ID', procactid)
    procactividad = db.query(Procact).filter(Procact.id == procactid.procact_id).first()
    print('PROC ACT ID', procactividad)
    # Buscar las posiciones entre las fechas dadas
    fecha = datetime.today().strftime("%Y-%m-%d")
    hora = datetime.today().strftime("%H:%M")
    
    # Convertir las observaciones en json
    listObserv = {}
    if ( objPe.observaciones != None and len(objPe.observaciones) != 0 ):
        listObserv = json.loads( objPe.observaciones )

    # Protocolo para observaciones:
    # {
    #   '2021-12-15': [
    #       
    #       {'fecha': '2021-12-15','hora': '1424-00000','empleado': 'Henry Lopez Vazquez', 'actividad': 'ajustar', 'observacion': 'jscnskjc'},
    #       {'fecha': '2021-12-15','hora': '2020-00000','empleado': 'Juan Carlos lopez', 'actividad': 'ajustar', 'observacion': 'jscnskjc'},
    #    ]
    # },
    # 
    horas = f"{hora}"
    empleado = f"{empleado.titulo} {empleado.nombre} {empleado.apepat} {empleado.apemat}"
    print('Empleado', empleado)
    actividadObser = f"{procactividad.actividad}"
    nvoMsg = {f'hora': horas, 'empleado': empleado, 'actividad': actividadObser, 'observaciones': observaciones}
    print('NvoMsg', nvoMsg)
    if (not fecha in listObserv):
        listObserv[fecha] = [nvoMsg]
    else:
        # Insertar en el arreglo de la fecha, la hora y el mensaje dados
        listObserv.get(fecha).append(nvoMsg)
    # configAct["objPe"]= jsonable_encoder(objPe)
    objPe.observaciones = json.dumps(listObserv, ensure_ascii=False)
    print('obj observaciones', objPe.observaciones)
    objPe.addtrans(db)
    return jsonable_encoder(objPe), listObserv



def raiseExceptionDataErr( msgError ):
    """" Método para comprimir los raise HTTPException referentes a errores en datos a procesar """
    if len(msgError)>0 : raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msgError)

def raiseException404( msgError ):
    """" Método para lanzar un error 404 controlado """
    if len(msgError)>0 : raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, error=msgError)

def raiseExceptionNoAuth( msgError ):
    """" Método para comprimir los raise HTTPException referentes a Credenciales inválidas ó sessión expirada """
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msgError)

def raiseExceptionExpired( msgError ):
    """" Método para comprimir los raise HTTPException referentes a Credenciales inválidas ó sessión expirada """
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msgError)


def raiseExceptionSinPrivilegios(msgError):
    """" Método para comprimir los raise HTTPException referentes a Sin privilegios """
    # No tiene acceso a iniciar trámites de este proceso...
    raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail=msgError)
    # raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail=f"Su rol no permite ejecutar esta actividad")
    # raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, 
    # detail=f"ACCESO RESTRINGIDO. Solo puede consultar sus propios trámites, no de otros usuarios, asgúrese de haber enviado su id de usuario")

def prepParam(sqlParams, parentesisOpen, campoTbl, comparacion, valor, parentesisCloseAndOr):
    """"Preparar parámetro para consulta sql"""
    cond = ""
    if (valor):
        campoTblLimpio = campoTbl.replace(".","_")
        cond = f"{parentesisOpen} {campoTbl} {comparacion} :{campoTblLimpio} {parentesisCloseAndOr} "
        if (comparacion=="like"):
            ca,sa = 'áéíóúüñÁÉÍÓÚÜÑ','aeiouunAEIOUUN'
            valorlike = str.maketrans(ca,sa)

            cond = f"{parentesisOpen} UNACCENT({campoTbl}) ILIKE :{campoTblLimpio} {parentesisCloseAndOr} "
            sqlParams[campoTblLimpio] = f'%{valor.translate(valorlike)}%'
        elif (comparacion=="start"):
            ca,sa = 'áéíóúüñÁÉÍÓÚÜÑ','aeiouunAEIOUUN'
            valorlike = str.maketrans(ca,sa)
            cond = f"{parentesisOpen} UNACCENT({campoTbl}) ILIKE :{campoTblLimpio} {parentesisCloseAndOr} "
            sqlParams[campoTblLimpio] = f'{valor.translate(valorlike)}%'
        else:
            sqlParams[campoTblLimpio] = valor
    return cond

def prepParamList(sqlParams, parentesisOpen, campoTbl, comparacion, valores:List, parentesisCloseAndOr):
    """"Preparar parámetro para consulta sql, recibiendo una lista de valores"""
    cond = ""
    if (valores):
        if len(valores) == 1:
            cond = prepParam(sqlParams, parentesisOpen, campoTbl, comparacion, valores[0], parentesisCloseAndOr)
        else:
            pos = 0
            campoTblLimpio = campoTbl.replace(".","_")
            for valor in valores:
                cond += f" {campoTbl} {comparacion} :{campoTblLimpio}_{pos} or "
                if (comparacion=="like"):
                    sqlParams[f"{campoTblLimpio}_{pos}"] = f'%{valor}%'
                else:
                    sqlParams[f"{campoTblLimpio}_{pos}"] = valor
                pos+=1
            cond = f"{parentesisOpen} ( {cond[0:-3]} ) {parentesisCloseAndOr} "
    return cond

def prepParamBetween(sqlParams, parentesisOpen, campoTbl, valorIni, valorFin, parentesisCloseAndOr):
    """"Preparar parámetro para consulta sql con between"""
    cond = ""
    if (valorIni and valorFin):
        campoTblLimpio = campoTbl.replace(".","_")
        cond = f"{parentesisOpen}{campoTbl} between :{campoTblLimpio}valIni and :{campoTblLimpio}valFin {parentesisCloseAndOr} "
        sqlParams[f'{campoTblLimpio}valIni'] = valorIni
        sqlParams[f'{campoTblLimpio}valFin'] = valorFin
    return cond

def getPermisos(user:tuple, session:tuple, db: Session, showOnlyInSidebar: bool = True):
    """Retorna la lista de permisos sobre catálogos, que tiene un usuario [id, is_superuser] dado"""
    permisos = []
    condicion = ""
    if (showOnlyInSidebar):
        condicion = "WHERE cat.showsidebar = true"
    try:
        #if user.is_pueruser:
        if user[1]== True:
            permisos = db.query(Cat).filter(Cat.showsidebar == True).all()    
        else:
            sql = f"""
                    SELECT cu.cat_id, cu.nombre, cu.url, cu.icono, cu.posicion, cu.catgrupo_id
                    FROM
                    (SELECT catuser.cat_id, cat.nombre, cat.url, cat.icono, cat.posicion, cat.catgrupo_id
                    FROM catuser, cat WHERE catuser.user_id = :user_id AND cat.id = catuser.cat_id) cu
                    LEFT JOIN cat ON cu.cat_id = cat.id {condicion}
                    UNION
                    SELECT cr.cat_id, cr.nombre, cr.url, cr.icono, cr.posicion, cr.catgrupo_id
                    FROM
                    (SELECT catrol.cat_id, cat.nombre, cat.url, cat.icono, cat.posicion, cat.catgrupo_id
                    FROM roluser, catrol, cat WHERE roluser.user_id = :user_id and roluser.rol_id = catrol.rol_id AND cat.id = catrol.cat_id
                    ) cr
                    LEFT JOIN cat ON cr.cat_id = cat.id {condicion}
                    ORDER BY cat_id
            """
            sqlParams = {'user_id':f'{user[0]}'}
            # cond = prepParam(sqlParams, '', 'user_id', '=', user[0], '')
            permisos = database.execSql(sql, sqlParams, True)
            # print(permisos)
    except(BaseException) as err:
        savelog(err)
        print("error ", err)
    return permisos

def hasPermisos(userAutentificado:tuple, urldada:str):
    """Retorna True o False, dependiendo si el usuario autentificado  [id, is_superuser], tiene o no privilegios sobre catálogos, ya sea de forma pesonal o por sus roles asignados"""
    try:
        sql = f"""
            Select user_id from catuser cu 
            where user_id = :user_id and date(now()) between fechaini and coalesce (fechafin, date(now() +'1 day') )
                and cat_id in ( Select id from cat where url = :urldada )
            Union
            Select user_id from roluser 
            Where user_id = :user_id
            and rol_id in (
                Select rol_id from catrol cu 
                where date(now()) between fechaini and coalesce (fechafin, date(now() +'1 day') )
                    and cat_id in ( Select id from cat where url = :urldada )
            )
        """
        sqlParams = {'user_id':userAutentificado[0],'urldada':urldada }
        # cond = prepParam(sqlParams, '', 'user_id', '=', userAutentificado[0], '')
        permisos = database.execSql(sql, sqlParams, True)
    except BaseException as err :
        savelog(err)
        pass
    # tieneAcceso = [item for item in permisos if item.url.startswith(urldado) ]
    # if user.is_superuser == 1 or len(tieneAcceso) > 0 :
    if (userAutentificado!=None and (userAutentificado[1] == True) or (permisos!=None and len(permisos) > 0)) :
        return True
    else:
        return False

def is_SuperUser(session:tuple, db:Session):
    """is_SuperUser(session, db) -> return [id, is_superuser]"""
    is_su = None
    if session != None:
        is_su = db.query(User.id, User.is_superuser, User.full_name).filter(User.email == session[0].username and User.is_active == True).first()
    return is_su

def accessPageValidate(url, pagina, session, db, request, ret, isForaPI:bool = False, **kwargs):
    """Retorna al usuario actualmente autentificado, la pagina correspondiente a un catálogo solicitado 
    siempre y cuando tenga permisos para ello, de lo contrario, se le retorna la página de error"""
    # user = db.query(User).filter(User.email == session[0].username).first()
    # print("kwargs: ", kwargs)
    user = is_SuperUser(session, db)
    permisos = getPermisos(user, session, db, True)
    catgrupo = db.query(Catgrupo.id, Catgrupo.grupo, Catgrupo.posicion).all()
    urlSinLlaves = url
    if "{" in url:
        urlSinLlaves = url[0:url.find("{")]
        if urlSinLlaves[-1] == "/":
            urlSinLlaves = urlSinLlaves[0:-1]
    tieneAcceso = [item for item in permisos if item.url.startswith(urlSinLlaves) ]
    # if user.is_superuser == 1 or len(tieneAcceso) > 0 :
    if user!=None and (user[1] == 1 or len(tieneAcceso) > 0) :
        ruta_bd = []
        url_cadena = url.split('/')
        ruta_bd = db.query(Cat).filter(Cat.url == '/'+url_cadena[1]).first()
        if (isForaPI):
            return True
        else:
            return templates.TemplateResponse( name=pagina, context={ "request": request, "ret": ret, "user": session[0], "full_name": user[2], "envname": getSettingsNombreEnvActivo(db),
            "is_superuser": user[1], "ruta_bd": ruta_bd, "permisos":jsonable_encoder (permisos), "catgrupo":jsonable_encoder(catgrupo), **kwargs } )
    else:
        if (isForaPI):
            return False
        else:
            return templates.TemplateResponse( name="error.html", context={ "request": request } )

def getEmpleadoId(user_id:int, db:Session):
    """empleadoId(user_id, db) -> return solo empleado_id """
    emp_id = db.query(UserEmpleado.empleado_id).filter(UserEmpleado.user_id == user_id).first()
    if emp_id != None:
        return emp_id[0]
    else:
        return None

def getEmpleadoDatos(user_id:int, db:Session):
    """getEmpleadoDatos(user_id) -> return datos personales de UN empleado"""
    emp = db.query(Empleado).select_from(UserEmpleado).filter(UserEmpleado.user_id == user_id, Empleado.id == UserEmpleado.empleado_id).first()
    return emp

def getAreaActual(empleado_id:int, db:Session):
    """getAreaActual(empleado_id, db) -> Retorna un arreglo de areas actuales de un empleado_id dado"""
    ae, a = aliased(AreaEmpleado), aliased(Area)
    area = db.query(a.codigo, a.nombre, ae.id, ae.area_id, ae.fechaini, ae.fechafin)\
                .filter(ae.empleado_id == empleado_id).join(a, a.id == ae.area_id)\
                .filter(or_(ae.fechafin == None, ae.fechafin >= datetime.today().date())).all()
    return area

def getAreaActual2(empleado_id:int, db:Session):
    """Retorna SOLO el area actual de un empleado_id dado"""
    ae, a = aliased(AreaEmpleado), aliased(Area)
    area = db.query(a).select_from(ae).filter(ae.empleado_id == empleado_id).join(a, a.id == ae.area_id)\
                .filter(or_(ae.fechafin == None, ae.fechafin >= datetime.today().date())).first()
    return area


def getRolesActuales(user_id:int, db:Session):
    """getRolesActuales(user_id) -> return TODOS los roles vigentes asociados a UN usuario"""
    ru, r = aliased(RolUser), aliased(Rol)
    roles = db.query(r.rol, ru.id, ru.rol_id, ru.fechaini, ru.fechafin)\
                .filter(ru.user_id == user_id).join(r, r.id == ru.rol_id)\
                .filter(or_(ru.fechafin == None, ru.fechafin >= datetime.today())).all()

    return roles

def getPuestosActuales(empleado_id:int, db:Session):
    """getPuestosActuales(empleado_id) -> return TODOS los puestos actuales de UN empleado"""
    pe, p, gt = aliased(PuestoEmpleado), aliased(Puestos), aliased(GrupoTag)
    puestos = db.query(pe.id, p.clave, gt.grupo, p.nombre, pe.puesto_id, pe.fechaini, pe.fechafin)\
                .filter(pe.empleado_id == empleado_id).join(p, p.id == pe.puesto_id).join(gt, gt.id == p.grupotag_id)\
                .filter(or_(pe.fechafin == None, pe.fechafin >= datetime.today().date())).all()
    return puestos

def getPuestosHistorial(empleado_id:int, db:Session):
    """getPuestosHistorial(empleado_id) -> return el historial completo de puestos de UN empleado"""
    pe, p, gt = aliased(PuestoEmpleado), aliased(Puestos), aliased(GrupoTag)
    puesto_hist = db.query(pe.id, p.clave, gt.grupo, p.nombre, pe.puesto_id, pe.fechaini, pe.fechafin)\
                .filter(pe.empleado_id == empleado_id).join(p, p.id == pe.puesto_id).join(gt, gt.id == p.grupotag_id).order_by(pe.fechaini.desc()).all()
    return puesto_hist

def getSettingsName(campo, valorPredefinido="por asignar"):
    """Retorna el valor asignado de una setting almacenada en la base de datos,
    haciendo el insert correspondiente en caso de no encontrarse registrado
    En donde:
        campo: Es el nombre de la setting cuyo valor se desea obtener de la base de datos
        valorPredefinido: Es el valor predefinido a insertarse en caso de no encontrarse aún almacenado
    """
    sys_name = ""
    if campo != None:
        sql = f"SELECT valor FROM settings WHERE campo = '{campo}'"
        sys_name = database.execSql(sql, {}, True)
    if ( sys_name is None or len(sys_name) == 0 ):
        sql = f"insert into settings (campo, valor, user_id) values ('{campo}', '{valorPredefinido}',0)"
        sys_name = database.execSql(sql, {}, True)
        sql = f"SELECT valor FROM settings WHERE campo = '{campo}'"
        sys_name = database.execSql(sql, {}, True)
    return sys_name[0].valor
        
def getAreasHistorial(empleado_id:int, db:Session):
    """getAreasHistorial(empleado_id) -> return el historial completo de areas de adscripción de UN empleado"""
    ae, a = aliased(AreaEmpleado), aliased(Area)
    puesto_hist = db.query(a.codigo, a.nombre, ae.id, ae.fechaini, ae.fechafin).filter(ae.empleado_id == empleado_id)\
                    .join(a, a.id == ae.area_id).order_by(ae.fechaini.desc()).all()
    return puesto_hist

def getRolesHistorial(user_id:int, db:Session):
    """getRoleshistorial(user_id) -> return TODOS los roles asociados a UN usuario"""
    ru, r = aliased(RolUser), aliased(Rol)
    roles = db.query(r.rol, ru.id, ru.fechaini, ru.fechafin).filter(ru.user_id == user_id).join(r, r.id == ru.rol_id).all()
    return roles

async def makeFilePlantilla(modelPlantilla:str, estructura:list):
    """Crea un archivo excel en la ruta indicada, con las hojas y columnas indicadas."""
    #   Crear el archivo en el directorio de models_plantillas
    #       generarlo con las columnas y el numero de hojas indicadas
    try:
        with pd.ExcelWriter(modelPlantilla, mode="w", engine="openpyxl") as writer:
            for hoja in estructura:
                # df = pd.DataFrame([["ABC", "XYZ"]], columns=["Foo", "Bar"])
                if hoja["datos"] == None:
                    df = pd.DataFrame(columns=hoja["columnas"])
                else:
                    df = pd.DataFrame(data = hoja["datos"], columns=hoja["columnas"])

                df.to_excel(writer,sheet_name=hoja["nombreHoja"], index=False)
            
            writer.save()
            # return true
    except BaseException as err:
        savelog(err)
        # return false

async def getFilePlantilla (tablaAconsultar:str, rutaPlantillas:str, estructura:list):
    """Retorna la ruta del archivo de excel creado (plantilla de un model)"""
    wd = os.getcwd()
    wd = f"{wd}{rutaPlantillas}"
    # crear el directorio en caso de que no exista
    if not exists(wd): 
        os.makedirs(wd)

    modelPlantilla = f"{wd}/{tablaAconsultar}.xlsx"
    # print(modelPlantilla)
    await makeFilePlantilla(modelPlantilla, estructura)
    return modelPlantilla

def rolExistIn(user_id:int, rol_id:int,  db:Session):
    """retorna todos los registros de roles de un usuario"""
    ru = aliased(RolUser)
    roles = db.query(ru.id, ru.fechaini, ru.fechafin).filter(ru.user_id == user_id, ru.rol_id == rol_id).all()
    return roles

def isDateBetweenRol(tags_list:list, f_buscar:datetime):
    """Verifica si una fecha-hora esta dentro de una lista de registros de roles"""
    f_hoy = datetime.today()
    #si hay un perido registrado sin f_fin, se asigna a este la fecha de hoy+100 años temporalmente
    f_100 = datetime(f_hoy.year+100,f_hoy.month, f_hoy.day)
    #si f_fin se recibió en null asignar 10 años, y verifica que no esté dentro de un periodo ya registrado
    if f_buscar == None:
        f_buscar = datetime(f_hoy.year+10,f_hoy.month, f_hoy.day)
    # print("f_100: ", f_100, " -- f_buscar: ",f_buscar)
    for tag in tags_list:
        # tag = list(tag)
        if tag["fechafin"] == None:
            # tag["fechafin"] = f_100
            print(f_buscar,tag["fechaini"],f_100)
            if f_buscar > tag["fechaini"] and f_buscar < f_100:
                return True
        if f_buscar > tag["fechaini"] and f_buscar < tag["fechafin"]:
            return True
    return False

def isDateExtremeRol(tags_list:list, f_ini:datetime, f_fin:datetime):
    """Verifica si dentro de un periodo existen registros de roles"""
    f_hoy = datetime.today()
    f_100 = datetime(f_hoy.year+100,f_hoy.month, f_hoy.day)
    if f_fin == None:
        f_fin = datetime(f_hoy.year+10,f_hoy.month, f_hoy.day)

    for tag in tags_list:
        if tag["fechafin"] == None:
            tag["fechafin"] = f_100
        if f_ini < tag["fechaini"] and tag["fechafin"] < f_fin  :
            return True
    return False

def isDateBetween(f_buscar:date, empleado_id:int, db:Session):
    """Retorna los registros de areas que contienen la fecha buscada"""
    f_hoy = date.today()
    #si hay un perido registrado sin f_fin, se asigna a este la fecha de hoy+100 años temporalmente
    f_100 = date(f_hoy.year+100,f_hoy.month, f_hoy.day)
    #si f_fin se recibió en null asignar 10 años, y verifica que no esté dentro de un periodo ya registrado
    if f_buscar == None:
        f_buscar = date(f_hoy.year+10,f_hoy.month, f_hoy.day)

    print("f_100: ", f_100, " -- f_buscar: ",f_buscar)
    AE = aliased(AreaEmpleado)
    f_entre = db.query(AE.id, AE.fechaini, AE.fechafin).filter(and_(AE.empleado_id == empleado_id,
                between(f_buscar, AE.fechaini, coalesce(AE.fechafin, f_100)))).all()
    return f_entre

def isPeriodBetween(f_ini:date, f_fin:date, empleado_id:int, db:Session):
    """Retorna los registros de areas que estan entre un periodo de tiempo"""
    if f_fin == None:
        f_hoy = date.today()
        f_fin = date(f_hoy.year+10,f_hoy.month, f_hoy.day)
    AE = aliased(AreaEmpleado)
    periodo_entre = db.query(AE.id, AE.fechaini, AE.fechafin).filter(and_(AE.empleado_id == empleado_id,between(AE.fechaini, f_ini, f_fin))).all()
    return periodo_entre

def tagExistIn(puesto_id:int, empleado_id:int, db:Session):
    """Retorna los registros de puestos/etiquetas asignados a un empleado"""
    #recuperar puesto.id y puesto.grupotag_id
    tag_id = db.query(Puestos.grupotag_id).filter(Puestos.id == puesto_id).first()
    print("tag_id: ", tag_id)
    #verificar si existen registros en puestoempleado para empleado_id, con fechafin mayor a hoy o en NULL
    # y con el mismo tag_id
    pe, p = aliased(PuestoEmpleado), aliased(Puestos)
    tag_p = db.query(pe.id, pe.puesto_id, pe.fechaini, pe.fechafin, p.grupotag_id)\
                .filter(pe.empleado_id == empleado_id).join(p, and_(p.id == pe.puesto_id, p.grupotag_id == tag_id[0])).all()
    return tag_p

def isDateBetweenTags(tags_list:list, f_buscar:date):
    """Verifica si una fecha está dentro de una lista de puestos/etiquetas"""
    f_hoy = date.today()
    #si hay un perido registrado sin f_fin, se asigna a este la fecha de hoy+100 años temporalmente
    f_100 = date(f_hoy.year+100,f_hoy.month, f_hoy.day)
    #si f_fin se recibió en null asignar 10 años, y verifica que no esté dentro de un periodo ya registrado
    if f_buscar == None:
        f_buscar = date(f_hoy.year+10,f_hoy.month, f_hoy.day)

    # print("f_100: ", f_100, " -- f_buscar: ",f_buscar)
    for tag in tags_list:
        # tag = list(tag)
        if tag["fechafin"] == None:
            # tag["fechafin"] = f_100
            if f_buscar >= tag["fechaini"] and f_buscar <= f_100:
                return True
        elif f_buscar >= tag["fechaini"] and f_buscar <= tag["fechafin"]:
            return True
    return False

def isDateExtremeTags(tags_list:list, f_ini:date, f_fin:date):
    """Verifica si hay registros de puestos/etiquetas dentro de periodo de tiempo (f_ini -- f_fin)"""
    f_hoy = date.today()
    f_100 = date(f_hoy.year+100,f_hoy.month, f_hoy.day)
    if f_fin == None:
        f_fin = date(f_hoy.year+10,f_hoy.month, f_hoy.day)

    for tag in tags_list:
        if tag["fechafin"] == None:
            # tag["fechafin"] = f_100
            if f_ini < tag["fechaini"] and f_100 < f_fin  :
                return True
        elif f_ini < tag["fechaini"] and tag["fechafin"] < f_fin  :
            return True
    return False

# getCatalogosDetail(rol_id) -> return datos personales de UN empleado
def getCatalogosDetail(rol_id:int, db: Session):
    catDatos = []
    sql = f"""
            select cat.id, cat.nombre, cat.url, cat.icono, catrol.fechaini, catrol.fechafin,rol.rol 
            from cat LEFT JOIN catrol ON cat.id = catrol.cat_id left JOIN rol 
            ON rol.id = catrol.rol_id where rol.id = :rol_id
        """
    sqlParams = {'rol_id':f'{rol_id}'}
    catDatos = database.execSql(sql, sqlParams, True)
    return catDatos

# getRolesActual(rol_id) -> return el rol actual
def getRolesActual(rol_id:int, db:Session):
    rol = db.query(Rol.rol).filter(Rol.id == rol_id).first()
    return rol
    
def getAnioFiscalActual():
    """Retorna el año actual considerando la fecha actual existente en el servidor"""
    f_hoy = datetime.today()
    return f_hoy.year

def getAnioFiscalList():
    """Retorna una lista de años, iniciando desde el año registrado en el sistema anterior, hasta el año actual mas uno """
    aniosList = [] 
    for anio in range(getAnioFiscalActual()+1, 2014, -1):
        aniosList.append([anio,anio])
    return aniosList

def getMesesDelAnio():
    return ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre' , 'Diciembre'];

def getPuestosTAG(tag_id: int, db:Session):
    """Retorna una lista de puestos de acuerdo al grupotag_id indicado (PTO, CAT, SIN, CTO...)"""
    puestos_list = db.query(Puestos.id, Puestos.clave, Puestos.nombre).filter(Puestos.grupotag_id == tag_id).all()

    return puestos_list


def getValSetting(campo):
    """Retornar el nombre de la universidad"""
    # dep_name = db.query(Settings.DEP_NAME).filter(Settings.DEP_NAME == '$DEP_NAME').first()
    sql = f"SELECT valor FROM settings WHERE campo = '{campo}'"
    val_setting = database.execSql(sql, {}, True)
    return val_setting

def getSettingsNombreEnvActivo(db: Session = Depends(database.get_db)):
    """Retornar el nombre del entorno de desarrollo que se encuentre activo marcado en la BD"""
    settingEnv = db.query(Settings).filter(Settings.campo == "environments").first()
    dicjson = json.loads( settingEnv.valor )
    entornoDefault = 'DEV - Desarrollo local' # Valor predefinido
    for entorno in dicjson:
        if (dicjson[entorno]['activo'] == 'true'):
            entornoDefault = entorno
            break
    print (entornoDefault)
    return entornoDefault

def savelog(msg):
    # Se obtiene los datos del error actual
    exc_type, exc_value, exc_traceback = sys.exc_info()
    for tb_info in traceback.extract_tb(exc_traceback):
        filename, linenum, funcname, source = tb_info
    fechact =datetime.today()
    dirraiz = 'logg'
    direrrs = dirraiz+'/'+fechact.strftime('%Y')
    # %Y-%m-%d'
    fileName = direrrs+'/'+fechact.strftime('%m')+'.txt'
    if os.path.exists(dirraiz)==False:
        os.mkdir(dirraiz)  
    if os.path.exists(direrrs) == False :
        os.mkdir(direrrs)           
    logging.basicConfig(
    level= logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style= '{',
    filename=fileName,
    filemode='a'
    # w = se remplaza los datos del archivo
    # a = agrega al archivo las lineas de error nuevas
    )

    msg = f'File {os.path.abspath(filename)} line {linenum} {msg}'
    logging.warning(msg)
    # logging.debug(msg)
    # logging.info(msg)
    # logging.error(msg)
    # logging.critical(msg)

