import os
import json
import sys
import traceback
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from modulos.seguridad.models import Settings
# from modulos.shared_models import Settings
# Importar losschemas del PIDE a pesar de que no se utilicen de forma directa, sino mas bien de forma indirecta por
# la importación desde archivos de excel
from db import database
from routers.plantillas import templates
from datetime import datetime
from fastapi import status, HTTPException
from fastapi.responses import FileResponse
import logging


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

