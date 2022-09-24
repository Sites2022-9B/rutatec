from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, hasPermisos, isDateBetweenRol, isDateExtremeRol, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth
from .models import *
from .schemas import *
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter( tags=['Catálogos'] )
hoy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@router.get("/catalogos")
async def show_R_View(request: Request, ret: str = "/catalogos", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/catalogos"
    pagina = "catalogos.html"
    return accessPageValidate(url, pagina, session, db, request, ret)
    
@router.post('/api/catalogos')
async def getCat(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = 'select * from cat'
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'nombre', 'like', busq.search, 'or ')
        cond += prepParam(sqlParams, '', 'url', 'like', busq.search, 'or')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
        print("SQL: ", sql)
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= Cat().getLabels(database)
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/catalogos/update")
async def updateCatalogo(CatalogoDado:CatalogoUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        catalogoAactualizar = db.get(Cat, CatalogoDado.id)
        catalogoAactualizar.nombre = CatalogoDado.nombre
        catalogoAactualizar.icono = CatalogoDado.icono
        catalogoAactualizar.posicion = CatalogoDado.posicion
        catalogoAactualizar.catgrupo_id = CatalogoDado.catgrupo_id

        catalogoAactualizar.update(db)
        return {"message": "Success!!!"}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna los usuarios ligados al catalogo
@router.post('/api/catalogos/user')
async def getCatUser(busq: CatUserBusq, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/user'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f'''SELECT "user".id, "user".full_name, "user".email, catuser.fechaini, catuser.fechafin
                    FROM "user", catuser, cat
            '''
        cond = f""""user".id = catuser.user_id AND cat.id = catuser.cat_id AND catuser.cat_id = {busq.id_cat} and """
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'full_name', 'like', busq.search, 'and')

        #condicones de las busquedas por filtro
        if (busq.filtro == "Vigentes"):
            cond += f"""catuser.fechafin >= '{hoy}' UNION
                        SELECT "user".id, "user".full_name, "user".email, catuser.fechaini, catuser.fechafin
                        FROM "user", catuser WHERE "user".id = catuser.user_id AND catuser.cat_id = {busq.id_cat}
                        AND catuser.fechafin IS NULL AND"""
        elif (busq.filtro == "Historial"):
            cond += f"catuser.fechafin <= '{hoy}' AND"
            print("sql:",sql)
        elif (busq.filtro == "Todos"):
            cond
        if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
        print("sql: ", sql)
        busq.validarPaginacion()
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        # labels= ["full_name", "email", "fechaini", "fechafin"]
        labels= ["ID","Nombre", "Email", "Fecha inicio", "Fecha fin"]
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna el nombre del catalogo
@router.get("/api/catalogos/nomCat/{id_cat}")
async def getCatalogosNombre(id_cat: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/nomCat'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        cat_act = []
        cat_act = db.query(Cat.nombre).filter(Cat.id == id_cat).first()
        print(cat_act[0])
        return {"cat_act":cat_act[0]}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/catalogos/catUserFinish")
async def catUserFinish(fin_catUser:catUserFin, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/catUserFinish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        catUser_act = db.query(CatUser).filter(CatUser.user_id == fin_catUser.user_id[0]).filter(CatUser.cat_id == fin_catUser.cat_id).first()
        print("catUser: ", catUser_act)
        if(catUser_act != None):
            catUser_act.fechafin = fin_catUser.fechafin
            catUser_act.update(db)
            return {"message", "success"}
        raiseExceptionDataErr(f"El catálogo no fue encontrado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#nuevo Entry Point para desplegar en otra página los datos de los catalogos
@router.get("/catalogos/details/{id_cat}")
async def showCatalogosView(request: Request, id_cat:int, ret: str = "/catalogos", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/catalogos/"
    pagina = "catalogos_detalle.html"
    return accessPageValidate(url, pagina, session, db, request, ret, id_cat = str(id_cat))

#obtenemos los catalogos
@router.get("/api/catalogos/userCombo")
async def getCatalogosCombo(q : str ="",users_id:int=0,session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/userCombo'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        sql = f"""SELECT id, full_name from "user" """
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'full_name', 'like', q, '')
        cond += prepParam(sqlParams, '', 'id', '=', users_id, '')
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}" 
        [metadata, rows] = database.execSql(sql, sqlParams, False, True)
        return {'metadata': metadata, 'data': rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")
    
@router.post("/api/catalogos/userAssign")
async def newCatUser(catalogoDado:catalogoUserAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/catalogos/userAssign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        success = 0
        periodos = 0
        iniPeriodo = 0
        finPeriodo = 0
        for i in catalogoDado.user_id:
            print("CatDado: ", catalogoDado.user_id, catalogoDado.cat_id, catalogoDado.fechaini, catalogoDado.fechafin)
            #verificar si el catalogo ya fue asignado a un usuario
            exist_catUser = db.query(CatUser.user_id, CatUser.fechaini, CatUser.fechafin).filter(
                CatUser.cat_id == catalogoDado.cat_id).filter(CatUser.user_id == i).all()
            print("existe_p: ", exist_catUser)
            if exist_catUser == None:
                #crear un nuevo registro de puesto
                new_catUser = CatUser(user_id = i, cat_id = catalogoDado.cat_id, fechaini = catalogoDado.fechaini, fechafin = catalogoDado.fechafin)
                print("new Catalogo: ", new_catUser)
                new_catUser.create(db)
                success+=1
            else:
                #verificar si la fecha inicio está dentro de este periodo ya registrado
                if isDateBetweenRol(exist_catUser, catalogoDado.fechaini) == False:
                    if isDateBetweenRol(exist_catUser, catalogoDado.fechafin) == False:
                        if isDateExtremeRol(exist_catUser, catalogoDado.fechaini, catalogoDado.fechafin) == False:
                            #crear un nuevo registro de puesto
                            new_catUser = CatUser(user_id = i, cat_id = catalogoDado.cat_id, fechaini = catalogoDado.fechaini, fechafin = catalogoDado.fechafin)
                            print("new Catalogo: ", new_catUser)
                            new_catUser.create(db)
                            success+=1
                        periodos+=1 
                    finPeriodo+=1
                iniPeriodo=+1
        if (success >0):
            return {"message": "Catalogos asignados"}
        elif (periodos>0):
             raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
        elif (finPeriodo>0):
            raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo vigente o sin finalizar del mismo ROL.")
        elif (iniPeriodo>0):
            raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo vigente o sin finalizar del mismo ROL.")
    raiseExceptionNoAuth(f"Acceso no autorizado")
