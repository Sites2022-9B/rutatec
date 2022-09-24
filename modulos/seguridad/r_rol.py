from genericpath import exists
import os
from fastapi.datastructures import UploadFile
from fastapi.params import File, Form
import pandas as pd
from modulos.seguridad.r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from modulos.shared_defs import accessPageValidate, getRolesActual, getSettingsName, hasPermisos, isDateBetweenRol, isDateExtremeRol, prepParam, raiseExceptionDataErr, raiseExceptionNoAuth, rolExistIn
from .models import *
from .schemas import *
from modulos.personal.models import *
from modulos.personal.schemas import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from typing import List, Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

router = APIRouter( tags=['Roles'] )

@router.get("/roles")
async def show_R_View(request: Request, ret: str = "/roles", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/roles"
    pagina = "rol.html"
    return accessPageValidate(url, pagina, session, db, request, ret)
    
@router.post('/api/roles')
async def getRol(busq: BusqRolFecha, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        fecha = ""
        if(busq.fechabus==''):
            fecha = datetime.today().strftime('%Y-%m-%d')
        else:
            fecha = busq.fechabus
        sql = f"""SELECT ra.id, ra.rol,ra.catr,count(ru.id) as cantru
            FROM (
            SELECT r.id,r.rol, count(cr.id) as catr FROM (SELECT * FROM rol)r 
            LEFT JOIN catrol cr on  r.id = cr.rol_id AND '{fecha}' BETWEEN date(cr.fechaini) AND coalesce(date(cr.fechafin),'2999-10-16')
            GROUP BY r.id, r.rol
            ORDER BY r.id
            )ra
            LEFT JOIN roluser ru on ra.id = ru.rol_id AND '{fecha}' BETWEEN date(ru.fechaini) AND coalesce(date(ru.fechafin),'2999-10-16')
            """
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'rol', 'like', busq.search, '')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        sql +="""GROUP BY ra.id, ra.rol,ra.catr
        ORDER BY ra.id"""
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= Rol().getLabels(database)
        return {"labels":["ID","Nombre del rol","Catalogos y usuarios","cantru"], "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")


@router.post("/api/roles/addrol")
async def addRol(rolDado:RolAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/addrol'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = rolDado.isValid()
        if esValido:
            existe_r = db.query(Rol).filter(Rol.rol == rolDado.rol).first()
            if existe_r == None:
                datos = Rol(**rolDado.dict())
                datos.create(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"el nombre del rol ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/roles/update")
async def updateRol(rolDado:RolUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/update'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = rolDado.isValid()
        if esValido:
            rolAactualizar = db.get(Rol, rolDado.id)
            existe_r = db.query(Rol).filter(Rol.rol == rolDado.rol).filter(Rol.id != rolDado.id).first()
            if existe_r == None:
                rolAactualizar.rol = rolDado.rol
                rolAactualizar.update(db)
                return {"message": "Success!!!"}
            raiseExceptionDataErr(f"el nombre del rol ya existe, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/roles/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/uploadfiles'
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
        col_types = {"rol":str}
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
                        validaFila = RolAdd(**fila)
                        esValido, observaciones = validaFila.isValid()

                        if not esValido:
                            listStatus.append(observaciones)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue

                        rolInsert = fila["rol"]
                                            
                        areabusq = db.query(Rol).filter(Rol.rol == rolInsert).first()
                        if areabusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunos roles ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        statement = f"insert into rol (rol) values('{rolInsert}');"
                        
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
                            msg = "Algunos roles ya existen, descarga las observaciones"
                if totFilas > 0:            
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"s"})
                    df['status'] = pd.DataFrame(listStatus)
                    df.to_excel( f"{rutafile}{nombreArchivo}" ,index=False)
                else:
                    msg = "No se encontraron registros en el archivo proporcionado"
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})
                    os.remove(f"{rutafile}{nombreArchivo}")
                    
            except (FileNotFoundError, KeyError, ValueError):
                msg = "El archivo no contiene la estructura esperada definida en la plantilla"
                listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})   
                os.remove(f"{rutafile}{nombreArchivo}")
                
        return {"listResult": listResult}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/roles/combo")
async def getRolesCombo(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        rolList =  db.query(Rol).all()
        return {"roles": rolList}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#asigna un nuevo rol a un usuario
@router.post("/api/roles/assign")
async def newRolUser(rolDado:RolUserAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/assign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        aceptados = 0
        rechazados = 0
        usuariosnamesacep = ''
        usuariosnamesrecha = ''
        totaldatos = len(rolDado.user_id)
        #verificar si rolDado ya existe y "vigente"
        # TODO:Queda pendiente implementar la inserción de varios registros mediante una transacción
        for usuarios in rolDado.user_id:
            objNombre = db.query(User.full_name).filter(User.id==usuarios).first()
            roles = rolExistIn(usuarios, rolDado.rol_idf,  db)
            if len(roles) == 0:
                #crear un nuevo registro de roluser
                new_roluser = RolUser(user_id=usuarios,rol_id=rolDado.rol_idf,fechaini=rolDado.fechaini,fechafin=rolDado.fechafin)
                usuariosnamesacep += objNombre.full_name+","
                aceptados += 1
                new_roluser.create(db)
            else:
                #verificar si la fecha inicio está dentro de este periodo ya registrado
                if isDateBetweenRol(roles, rolDado.fechaini) == False:
                    if isDateBetweenRol(roles, rolDado.fechafin) == False:
                        if isDateExtremeRol(roles, rolDado.fechaini, rolDado.fechafin) == False:
                            new_roluser = RolUser(user_id=usuarios,rol_id=rolDado.rol_idf,fechaini=rolDado.fechaini,fechafin=rolDado.fechafin)
                            usuariosnamesacep += objNombre.full_name+","
                            aceptados += 1
                            new_roluser.create(db)
                        else:
                            usuariosnamesrecha += objNombre.full_name+","
                            rechazados+=1    
                        
                    else:
                        usuariosnamesrecha += objNombre.full_name+","
                        rechazados+=1
                    
                else:
                    usuariosnamesrecha += objNombre.full_name+","
                    rechazados+=1
               
        if aceptados==totaldatos and rechazados==0:
            return {"message": "succes"}
        elif aceptados>0 and rechazados<totaldatos:
            raiseExceptionDataErr(f"Agregados: "+usuariosnamesacep+". No agregados: "+usuariosnamesrecha+" porque ya tienen el rol")
        elif rechazados<=totaldatos and aceptados==0:
             raiseExceptionDataErr(f"No se agregaron registros porque los usuarios están vigentes")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#establece fecha de fin de rol actual..
@router.put("/api/roles/finish")
async def putRolFinish(fin_rol:RolUserFinish, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/finish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        rol_act = db.query(RolUser).filter(RolUser.id == fin_rol.rol_idf).first()
        print("puesto_act: ", rol_act)
        if(rol_act != None):
            rol_act.fechafin = fin_rol.fechafin
            rol_act.update(db)
            return {"message", "success"}
        raiseExceptionDataErr(f"el rol no fue encontrado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#nuevo Entry Point para desplegar en otra página los datos de los roles
@router.get("/roles/details/{id_rol}")
async def showUserDetailsView(request: Request, id_rol:int, ret: str = "/roles", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/roles/details/"
    pagina = "roles_detalle.html"
    return accessPageValidate(url, pagina, session, db, request, ret, id_rol = str(id_rol))

#retorna los catalogos pertenecientes al rol
@router.post("/api/roles/catalogos/{id_rol}")
async def getCatalogosDatos(id_rol: int,busq:CatRolBusq, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:    
        fecha = ""
        if(busq.fechabus==''):
            fecha = datetime.today().strftime('%Y-%m-%d')
        else:
            fecha = busq.fechabus
        print(fecha)
        # if userAutentificado[1]:
        sql = f"""select catrol.id, cat.id as catrol,cat.nombre, cat.url, cat.icono, catrol.fechaini, catrol.fechafin,case WHEN cat.showsidebar = true THEN 'Si' ELSE 'No' END showsidebar
            from cat 
            LEFT JOIN catrol ON cat.id = catrol.cat_id AND '{fecha}' BETWEEN date(catrol.fechaini) AND coalesce(date(catrol.fechafin),'2999-10-16')
            left JOIN rol 
            ON rol.id = catrol.rol_id where rol.id = {id_rol}
            """
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, 'and ', 'nombre', 'like', busq.search, '')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} {cond}"
        sql +="""ORDER BY catrol.id"""
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels = ["ID","Catid","Nombre","Url","Icono","Fecha inicio","Fecha fin","Se muestra en el menú"]
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post('/api/roles/user')
async def getUsers(busq: busqUsuFech, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        fecha = ""
        if(busq.fechabusU==None or busq.fechabusU==''):
            fecha = datetime.today().strftime('%Y-%m-%d')
        else:
            fecha = busq.fechabusU
        sql = f'''
            select roluser.id,"user".id as usuarid,"user".full_name, "user".email, roluser.fechaini, roluser.fechafin from "user"
            LEFT JOIN roluser ON "user".id = roluser.user_id and '{fecha}' BETWEEN date(roluser.fechaini)  AND coalesce(date(roluser.fechafin),'2999-10-16')
            '''
        cond = ''
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'roluser.rol_id', '=', busq.id_rol, 'and') 
        cond += prepParam(sqlParams, 'and(', 'full_name', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'email', 'like', busq.search, ')')

        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        # labels= ["full_name", "email", "fechaini", "fechafin"]
        labels= ["ID","Userid","Nombre", "Email", "Fecha inicio", "Fecha fin"]
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna el nombre del rol
@router.get("/api/roles/nomRol/{id_rol}")
async def getRolNombre(id_rol: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        rol_act = getRolesActual(id_rol, db)
        return {"rol_act":rol_act}
    raiseExceptionNoAuth(f"Acceso no autorizado")
    
#obtenemos los catalogos
@router.get("/api/roles/catalogoCombo")
async def getCatalogosCombo(q : str ="",cat_id:int=0,session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        sql = f"""SELECT ct.* from (SELECT id,(nombre||' - '||url) as cato FROM cat)ct"""
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'cato', 'like', q, '')
        cond += prepParam(sqlParams, '', 'id', '=', cat_id, '')
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}" 
        [metadata, rows] = database.execSql(sql, sqlParams, False, True)
        return {'metadata': metadata, 'data': rows}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/roles/catalogoAssign")
async def newPuestoEmp(catalogoDado:catalogoAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/catalogoAssign'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        #verificar si el catalogo ya fue asignado al rol
        exist_cat = db.query(CatRol.fechaini, CatRol.fechafin).filter(CatRol.cat_id == catalogoDado.cat_id).filter(CatRol.rol_id == catalogoDado.rol_id).all()        
        print("existe_p: ", exist_cat)
        if exist_cat == None:
            #crear un nuevo registro de puesto
            new_catRol = CatRol(rol_id = catalogoDado.rol_id, cat_id = catalogoDado.cat_id, fechaini = catalogoDado.fechaini, fechafin = catalogoDado.fechafin)
            print("new Catalogo: ", new_catRol)
            new_catRol.create(db)
            return {"message": "Nuevo puesto asignado"}  
        else:
            print("fecha ini",catalogoDado.fechaini)
            #verificar si la fecha inicio está dentro de este periodo ya registrado
            if isDateBetweenRol(exist_cat, catalogoDado.fechaini) == False:
                if isDateBetweenRol(exist_cat, catalogoDado.fechafin) == False:
                    if isDateExtremeRol(exist_cat, catalogoDado.fechaini, catalogoDado.fechafin) == False:
                        new_catRol = CatRol(rol_id = catalogoDado.rol_id, cat_id = catalogoDado.cat_id, fechaini = catalogoDado.fechaini, fechafin = catalogoDado.fechafin)
                        print("new Catalogo: ", new_catRol)
                        new_catRol.create(db)
                        return {"message": "Nuevo catalogo asignado"} 
                    raiseExceptionDataErr(f"Se encontraron periodos dentro del rango de fechas indicadas.")
                raiseExceptionDataErr(f"La fecha de FIN está dentro de un periodo vigente o sin finalizar del mismo TIPO.")
            raiseExceptionDataErr(f"La fecha de INICIO está dentro de un periodo vigente o sin finalizar del mismo TIPO.")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.put("/api/roles/catalogoFinish")
async def catalogoFinish(fin_cat:catalogoFin, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/catalogoFinish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        rol_act = db.query(CatRol).filter(CatRol.id == fin_cat.id,CatRol.cat_id == fin_cat.cat_id,CatRol.rol_id==fin_cat.rol_id).first()
        print("rol_act: ", rol_act)
        if(rol_act != None):
            rol_act.fechafin = fin_cat.fechafin
            rol_act.update(db)
            return {"message", "success"}
        raiseExceptionDataErr(f"El catálogo no fue encontrado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

