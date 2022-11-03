from fastapi import APIRouter, Request, Depends
from modulos.seguridad.models import User
from modulos.seguridad.r_authentication import SessionData, test_session
from typing import List, Tuple
from sqlalchemy.orm import Session
from db import database
from modulos.seguridad.schemas import Addusuario, UserUpdate,UserChangePwd
from modulos.seguridad.sec.sec_hashing import Hash
from routers.plantillas import templates
from modulos.shared_defs import getSettingsNombreEnvActivo, raiseExceptionDataErr, raiseExceptionNoAuth
from sqlalchemy.sql.elements import or_


router = APIRouter( tags=['registrar'] )

@router.get("/registrar")
async def show_U_View(request: Request, ret: str = "/registrar", session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    return templates.TemplateResponse( name="Registrar.html", context={ "request": request, "ret": ret, "envname": getSettingsNombreEnvActivo(db) } )


@router.post("/api/usuario/registrar")
async def addusuario(usuDado: Addusuario , session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    esValido, observa = usuDado.isValid()
    if esValido:
        existe_g = db.query(User).filter(User.correo == usuDado.correo).first()
        if existe_g == None:
            datos = User(
                nombre = usuDado.nombre,
                apellidos = usuDado.apellidos,
                correo = usuDado.correo,
                contra = Hash.bcrypt(usuDado.contra)
            )
            print('Datos registrados: ', datos.contra)
            datos.create(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"El correo ya existe, favor de verificar")
    raiseExceptionDataErr(observa)

@router.get("/api/sidebar")
async def getrutas(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    sql = f"""SELECT * FROM rutas"""
    sqlParams = {}
    metadatas,rows = database.execSql(sql, sqlParams, False, True)
    print('rutas', rows)
    return {"metadata" : metadatas, "data": rows}
    # raiseExceptionNoAuth(f"Permiso denegado")
    # raiseExceptionDataErr(observa)


@router.get("/api/user/perfil")
async def getPerfil(session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    print("datos user",session[0])
    usuario =  db.query(User.id, User.nombre, User.correo, User.apellidos).filter(User.id == session[0].id).first()
    print("usuario",usuario.correo)
    return usuario

@router.post("/api/user/updateuser")
async def addusuario(userDado: UserUpdate , session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    esValido, observa = userDado.isValid()
    if esValido:
        userAct = db.get(User, userDado.id)
        print(userAct)
        existe_u = db.query(User).filter(or_(User.nombre == userDado.nombre, User.correo == userDado.correo)).filter(User.id != userDado.id).first()
        print("existe usuario",existe_u)
        if existe_u == None: 
            datos = userDado.dict(exclude_unset=False)
            for key, value in datos.items():
                setattr(userAct, key, value)
            userAct.update(db)
            return {"message": "Success!!!"}
        raiseExceptionDataErr(f"Ya existe un usuario con este nombre o correo, favor de verificar")
    raiseExceptionDataErr(observa)

@router.put("/api/user/updatepass")
async def updateUserPwd(userDado:UserChangePwd, session: Tuple[SessionData, str] = Depends(test_session), db: Session = Depends(database.get_db)):
    userAactualizar = db.query(User).filter(User.id == userDado.id).first()
    #solo el usuario logueado podrá modificar su cuenta.
    if (userAactualizar != None):
        if(Hash.verify(userAactualizar.contra, userDado.passwordactual)):
            #si la contrasela actual en BD es igual a la del input
            if (len(userDado.passwordnvo) == 0 or userDado.passwordnvo != userDado.passwordnvo2):
                raiseExceptionDataErr(f"Las contraseñas no coinciden")
            else:
                userAactualizar.contra = Hash.bcrypt(userDado.passwordnvo)
                userAactualizar.update(db)
                return {"message": "Success!!!"}
        raiseExceptionDataErr(f"La contraseña Actual no coincide")
    raiseExceptionDataErr(f"Acceso no autorizado")

