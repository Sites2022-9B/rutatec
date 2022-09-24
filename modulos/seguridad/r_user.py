from sqlalchemy.sql.elements import or_
from fastapi.datastructures import UploadFile
from fastapi.params import File, Form
import pandas as pd
from .r_authentication import SessionData, validarSessionforApis, test_session 
from db import database
from .models import *
from .schemas import *
from modulos.shared_defs import *
from modulos.personal.schemas import *
from modulos.personal.models import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from .sec.sec_hashing import Hash
from typing import List, Tuple
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import FileResponse
import pathlib
import os
import re

router = APIRouter( tags=['Users'] )


#retorna todos los datos del usuaurio logueado desde perfil
@router.get("/api/users/miperfil")
async def getPerfil(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/roles/catalogoFinish'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( userAutentificado ):
        usuario =  db.query(User.id, User.full_name, User.email, User.is_active, User.is_superuser).filter(User.id == session[0].id).first()
        roles_u = getRolesActuales(usuario.id, db)
        roles_user = dict(usuario)
        roles_user['roles'] = tuple(roles_u)
        empleado = getEmpleadoDatos(usuario.id, db)
        area_emp = getAreaActual(empleado.id, db)
        puestos_emp = getPuestosActuales(empleado.id, db)
        return {"perfil": roles_user, "empleado":empleado, "area":area_emp, "puesto":puestos_emp}

@router.put("/api/users/updatepwd")
async def updateUserPwd(userDado:UserChangePwd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    userAactualizar = db.query(User).filter(User.id == userDado.id).first()
    #solo el usuario logueado podrá modificar su cuenta.
    if (userAactualizar != None and userAutentificado[0] == userAactualizar.id):
        if(Hash.verify(userAactualizar.password, userDado.passwordactual)):
            #si la contrasela actual en BD es igual a la del input
            if (len(userDado.passwordnvo) == 0 or userDado.passwordnvo != userDado.passwordnvo2):
                raiseExceptionDataErr(f"Las contraseñas no coinciden")
            else:
                userAactualizar.password = Hash.bcrypt(userDado.passwordnvo)
                userAactualizar.update(db)
                return {"message": "Success!!!"}
        raiseExceptionDataErr(f"La contraseña Actual no coincide")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post('/api/users')
async def getUsers(busq: BusquedaYPaginacion, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if (userAutentificado[1]):
        sql = '''select u.id, u.full_name, u.email, u."isEncrypted", u.is_active, u.is_superuser, ue.empleado_id 
                from "user" u LEFT JOIN userempleados ue ON ue.user_id = u.id'''
        cond = ""
        sqlParams = {}
        cond += prepParam(sqlParams, '', 'full_name', 'like', busq.search, 'or')
        cond += prepParam(sqlParams, '', 'email', 'like', busq.search, '')
        busq.validarPaginacion()
        if ( len(cond)>0 ) : sql = f"{sql} where {cond}"  # -4 = len("and ")
        # Obtener la página de registros derivados de la consulta
        getTotal = True
        [metadata, rows, total] = database.execSql(sql, sqlParams, False, True, getTotal, busq.offset, busq.limit)
        labels= User().getLabels(database)
        labels.remove("password")
        labels.append("Con empleado")
        return {"labels":labels, "metadata" : metadata, "data": rows, "total" : total}
    raiseExceptionNoAuth(f"Acceso no autorizado")
    
@router.get('/api/users/combo')
async def getUsers4Combo(q:str="", q_user_id:str="", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if not userAutentificado.is_superuser:
        # Si es un usuario normal entonces solo puede obtener su propio registro
        if ( str(userAutentificado.id) != q_user_id ) :
            # si intenta el usuario actual (que no es admin),
            # consultar la lista de acts de otro usuario,
            # no le será permitido, por lo que se le retornará el mensaje de error correspondiente
            raiseExceptionSinPrivilegios(f"ACCESO RESTRINGIDO. Solo puede consultar sus propios trámites, no de otros usuarios")
    sql = f'select id, full_name from "user"'
    cond = ""
    sqlParams = {}
    cond += prepParam(sqlParams, '', 'id', '=', q_user_id, 'and')
    cond += prepParam(sqlParams, '', 'full_name', 'like', q, 'and')
    
    if ( len(cond)>0 ) : sql = f"{sql} where {cond[0:-4]}"  # -4 = len("and ")
    [metadata, rows] = database.execSql(sql, sqlParams, False, True)
    return {'metadata': metadata, 'data': rows}

@router.get("/users")
async def show_U_View(request: Request, ret: str = "/users", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    # userAdministrador = db.query(User).filter(User.email == session[0].username).first()
    # if userAdministrador.is_superuser == 0:
    #     return RedirectResponse("/")
    url = "/users"
    pagina = "usuarios.html"
    return accessPageValidate(url, pagina, session, db, request, ret)

#agrega un usuario con la asignación de un empleado_id
@router.post("/api/users/adduser")
async def addUser(userDado:UserAdd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/adduser'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = userDado.isValid()
        if esValido:
            existe_u = db.query(User).filter(or_(User.full_name == userDado.full_name, User.email == userDado.email)).first()
            emp_asignado = db.query(UserEmpleado).filter(UserEmpleado.empleado_id == userDado.empleado_id).first()
            if existe_u == None:
                if emp_asignado == None:
                    #Iniciar una transacción para varias operaciones
                    trans = db.begin_nested()
                    try: 
                        userDado.password = Hash.bcrypt(userDado.password)
                        datos = User(full_name = userDado.full_name, email = userDado.email, password = userDado.password, isEncrypted = userDado.isEncrypted, is_active = userDado.is_active, is_superuser = userDado.is_superuser)
                        datos.addtrans(db)
                        #asignar el empleado seleccionado a este nuevo usuario
                        nu = db.query(User.id).filter(User.email == userDado.email).first()
                        new_userEmp = UserEmpleado(user_id = nu[0], empleado_id = userDado.empleado_id)
                        new_userEmp.addtrans(db)
                        #Si todo es correcto confirmar la transacción
                        trans.commit()
                        db.commit() 
                    except:
                        #Si se genera un error no se guardan cambios
                        trans.rollback()
                        db.commit() 
                        raiseExceptionDataErr(f"Error al crear el usuario")

                    return {"message": "Success!!!"}
                raiseExceptionDataErr(f"El empleado seleccionado ya está asignado a otro usuario, favor de verificar")    
            raiseExceptionDataErr(f"Ya existe un usuario con este nombre o correo, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")

#actualiza datos usuario con asignación de un empleado y SIN contraseña
@router.put("/api/users/updateuser")
async def updateUser(userDado:UserUpdate, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/updateuser'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        esValido, observaciones = userDado.isValid()
        if esValido:
            userAct = db.get(User, userDado.id)
            existe_u = db.query(User).filter(or_(User.full_name == userDado.full_name, User.email == userDado.email)).filter(User.id != userDado.id).first()
            emp_asignado = db.query(UserEmpleado).filter(UserEmpleado.empleado_id == userDado.empleado_id, UserEmpleado.user_id != userDado.id).first()
            if existe_u == None:
                if emp_asignado == None:
                    user_data = userDado.dict(exclude_unset=False)
                    for key, value in user_data.items():
                        setattr(userAct, key, value)
                    userAct.update(db)
                    # asignar el empleado seleccionado a este usuario
                    userEmpAct = db.query(UserEmpleado).filter(UserEmpleado.user_id == userDado.id).first()
                    if userEmpAct == None:
                        #insertar nuevo
                        new_userEmp = UserEmpleado(user_id = userDado.id, empleado_id = userDado.empleado_id)
                        new_userEmp.create(db)
                    else:
                        #Actualizar
                        userEmpAct.empleado_id = userDado.empleado_id
                        userEmpAct.update(db)
                    return {"message": "Success!!!"}
                raiseExceptionDataErr(f"El empleado seleccionado ya está asignado a otro usuario, favor de verificar")    
            raiseExceptionDataErr(f"Ya existe un usuario con este nombre o correo, favor de verificar")
        raiseExceptionDataErr(observaciones)
    raiseExceptionNoAuth(f"Acceso no autorizado")


##actualizar password solo por el admin 
@router.put("/api/users/updatepwd/{id_user}")
async def updateUserPwd_SU(id_user: int, userDado:UserChangePwd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    userAactualizar = db.query(User).filter(User.id == id_user).first()
    if (userAutentificado[1] and userAactualizar != None):
        if(Hash.verify(userAactualizar.password, userDado.passwordactual)):
            #si la contrasela actual en BD es igual a la del input
            if (len(userDado.passwordnvo) == 0 or userDado.passwordnvo != userDado.passwordnvo2):
                raiseExceptionDataErr(f"Las contraseñas no coinciden")
            else:
                userAactualizar.password = Hash.bcrypt(userDado.passwordnvo)
                userAactualizar.update(db)
                return {"message": "Success!!!"}
        raiseExceptionDataErr(f"La contraseña Actual no coincide")
    raiseExceptionNoAuth(f"Acceso no autorizado")

##actualizar cuenta de usuario (fullname, correo, isActivo, isSuperuer)
@router.put("/api/users/updateAccount/{id_user}")
async def updateUserAccount(id_user: int, userDado:UserUpdateAccount, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/updateAccount'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        userAct = db.get(User, id_user)
        existe_u = db.query(User).filter(or_(User.full_name == userDado.full_name, User.email == userDado.email)).filter(User.id != userDado.id).first()
        if existe_u == None:
            user_data = userDado.dict(exclude_unset=False)
            for key, value in user_data.items():
                setattr(userAct, key, value)
            
            userAct.update(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El nombre o el correo ya existe, favor de verificar")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#nuevo Entry Point para desplegar en otra página los datos de usuario, empleado, areas..
@router.get("/users/details/{id_user}")
async def showUserDetailsView(request: Request, id_user:int, ret: str = "/users", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    url = "/users/"
    pagina = "usuarios_detalle.html"
    emp_id = getEmpleadoId(id_user, db)
    area_emp = None
    if emp_id != None:
        area_emp = getAreaActual2(emp_id, db)
    # otros = {"id_user":user_id}
    return accessPageValidate(url, pagina, session, db, request, ret, id_user = id_user, area = area_emp)

#retorna solo datos de cuenta de usuario sin password
@router.get("/api/users/account/{id_user}")
async def getPerfil(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/account'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        user_query = db.query(User.id, User.full_name, User.email, User.is_active, User.is_superuser)\
                        .filter(User.id == id_user).first()
        if(user_query != None):
            return {"cuenta": user_query}
        raiseExceptionDataErr(f"el usuario consultado no existe")
    raiseExceptionNoAuth(f"Acceso no autorizado")


#retorna los datos personales del empleado asociado a un usuario
@router.get("/api/users/personal/{id_user}")
async def getUserPersonal(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/personal'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        user_employeer = getEmpleadoDatos(id_user, db)
        if(user_employeer != None):
            id_ue = db.query(UserEmpleado.id).filter(UserEmpleado.empleado_id == user_employeer.id).first()
            return {"empleado": user_employeer, "userEmp_id":id_ue}
        raiseExceptionDataErr(f"El usuario no ha sido asociado a un empleado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna area actual e historial
@router.get("/api/users/area/{id_user}")
async def getUserArea(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/area'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        emp_id = getEmpleadoId(id_user, db)
        if emp_id != None:
            area_act = getAreaActual(emp_id, db)
            area_hist = getAreasHistorial(emp_id, db)
            return {"area": area_act, "historial": area_hist}
        raiseExceptionDataErr(f"El usuario no ha sido asociado a un empleado") 
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna puesto actual e historial
@router.get("/api/users/puesto/{id_user}")
async def getUserPuesto(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/puesto'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        emp_id = getEmpleadoId(id_user, db)
        if emp_id != None:
            puesto_act = getPuestosActuales(emp_id, db)
            # print(puesto_act)
            puesto_hist = getPuestosHistorial(emp_id, db)
            # print(puesto_hist)
            return {"puesto": puesto_act, "historial": puesto_hist}
        raiseExceptionDataErr(f"El usuario no ha sido asociado a un empleado")
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/users/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...), tdi: str = Form(...), session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/uploadfiles'
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
        col_types = {"password":str}
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
                        print("fila: ", fila)
                        for clave, valor in fila.items():
                            if pd.isna(valor):
                                fila[clave] = ""

                        #si el campo email está vacío estonces eliminarlo de la fila
                        if fila["email"] == "":
                            del fila["email"]
                        
                        #validar estructura del correo
                        correo = re.compile(r"\b[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,6}\b")
                        if "email" in fila:
                            coincide = correo.match(fila["email"])
                            print("email correcto: ", coincide)
                            if coincide == None:
                                del fila["email"]
                        
                        print("fila sin NAN: ", fila)
                        #use .contruct() para no validar con pydantic
                        # validaFila = UserAdd.construct(**fila)
                        validaFila = UserAdd(**fila)
                        esValido, observaciones = validaFila.isValid()

                        if not esValido:
                            listStatus.append(observaciones)
                            msg = "Errores en algunos campos, descarga las observaciones"
                            filasError +=1
                            continue

                        emailInsert = fila["email"]
                        nombreInsert = fila["full_name"]
                        passwordInsert = Hash.bcrypt(str(fila["password"]))
                        # isEncryptedInsert = fila["isEncrypted"]                
                        # is_activeInsert = fila["is_active"]
                        # is_superuserInsert = fila["is_superuser"]    
                        userbusq = db.query(User).filter(User.email == emailInsert).first()
                        if userbusq != None: 
                            listStatus.append("Ya existe")
                            msg = "Algunos usuarios ya existen, descarga las observaciones"
                            filasError +=1
                            continue                    
                        # statement = f"insert into user (full_name, email, password, isEncrypted, is_active, is_superuser) values('{nombreInsert}','{emailInsert}','{passwordInsert}','{isEncryptedInsert}','{is_activeInsert}','{is_superuserInsert}');"
                        statement = f"insert into user (full_name, email, password, isEncrypted, is_active, is_superuser) values('{nombreInsert}','{emailInsert}','{passwordInsert}','1','1','0');"
                        
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
                            msg = "Existen registros duplicados en el archivo de excel, descarga las observaciones"
                if totFilas > 0:
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"s"})
                    df['status'] = pd.DataFrame(listStatus)
                    df.to_excel( f"{rutafile}{nombreArchivo}" ,index=False)
                else:
                    msg = "No se encontraron registros en el archivo proporcionado"
                    listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})
                    os.remove(f"{rutafile}{nombreArchivo}")
                        
            except (FileNotFoundError, KeyError, ValueError) :
                msg = "El archivo no contiene la estructura esperada definida en la plantilla"
                listResult.append({"file": nombreArchivo, "msg":msg, "showLink":"n"})            
                os.remove(f"{rutafile}{nombreArchivo}")

        return {"listResult": listResult}
    raiseExceptionNoAuth(f"Acceso no autorizado")

#retorna rol actual e historial
@router.get("/api/users/rol/{id_user}")
async def getUserRol(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    url = '/api/users/rol'
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if( hasPermisos(userAutentificado, url) ):
        rol_act = getRolesActuales(id_user, db)
        # print(rol_act)
        rol_hist = getRolesHistorial(id_user, db)
        # print(rol_hist)
        return {"rol": rol_act, "historial": rol_hist}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.post("/api/users/uploadFotos/{id_user}")
async def create_upload_files(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), files: List[UploadFile] = File(...), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        listResult = []
        # global filename 
        rutaDePlantillasUploads = getSettingsName("$SYS_DIR_FOTOS", "/f/emp/fotos")
        rutafile=f"{os.getcwd()}{rutaDePlantillasUploads}/"
        # crear el directorio en caso de que no exista
        if not exists(rutafile):
            os.makedirs(rutafile)
        for file in files:
            path = pathlib.Path(f'{file.filename}')
            nombreArch = f"emp_{id_user}"
            nuevoNombre = f"{nombreArch}{path.suffix}"
            with os.scandir(f"{os.getcwd()}{rutaDePlantillasUploads}") as ficheros:
                archFotoEmp = [fichero.name for fichero in ficheros if fichero.is_file() and \
                    fichero.name.startswith(nombreArch+".") ]            
                if len(archFotoEmp) != 0:
                    archi = archFotoEmp[0]
                    os.remove(f"{rutafile}{archi}")    
            sql = f'select nombre from empleadofoto where empleado_id = {id_user}'
            s1 = database.execSql(sql)
            try:
                with open(f"{rutafile}{nuevoNombre}", "wb") as myfile:
                    content = await file.read()
                    myfile.write(content)
                    myfile.close()
                    if s1 == []:
                        statement = f"insert into empleadofoto (empleado_id, nombre) values('{id_user}','{nuevoNombre}');"
                        db.execute(statement)
                        try:
                            db.commit()    
                        except:
                            db.rollback()
                            print("Error")
                    else:
                        statement = f"update empleadofoto set nombre='{nuevoNombre}' where empleado_id='{id_user}';"
                        db.execute(statement)
                        try:
                            db.commit()
                        except:
                            db.rollback()
                            print("Error")
            except (FileNotFoundError, KeyError, ValueError) :
                msg = "El archivo no contiene la estructura esperada definida en la plantilla"
        return {"listResult": listResult}
    raiseExceptionNoAuth(f"Acceso no autorizado")

@router.get("/api/users/changefotoperfil/{id_user}")
async def change_foto(id_user: int, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAutentificado = await validarSessionforApis(session=session, db=db)
    if userAutentificado:
        rutafoto = getSettingsName("$SYS_DIR_FOTOS", "/f/emp/fotos")
        sql = f'select nombre from empleadofoto where empleado_id = {id_user}'
        s1 = database.execSql(sql)
        if len(s1) == 0:
            rutafin = f"{os.getcwd()}{rutafoto}/"+"demo.jpg"
        else:
            s2 = s1[0][0]
            # s3 = s2[0]
            rutafin = f"{os.getcwd()}{rutafoto}/{s2}"
        return FileResponse(path=rutafin)
    raiseExceptionNoAuth(f"Acceso no autorizado")
