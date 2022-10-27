from abc import ABC, abstractmethod
from pydantic.networks import EmailStr
from sqlalchemy.sql.expression import null
from .sec.sec_hashing import Hash
from modulos.seguridad.models import *
from modulos.seguridad.schemas import Login, UpdatePassword, ForgotPassword
from typing import Type, Optional, Dict, Any, Tuple
from uuid import uuid4
from fastapi.security.api_key import APIKeyBase, APIKey, APIKeyIn
from datetime import timedelta, datetime
from pydantic import BaseModel
from itsdangerous import TimestampSigner
from itsdangerous.exc import SignatureExpired
from base64 import b64encode, b64decode
from db import database
from fastapi import APIRouter, Depends, HTTPException, FastAPI, Request, Response
from sqlalchemy.orm import Session
from modulos.shared_defs import getSettingsNombreEnvActivo, is_SuperUser, raiseExceptionDataErr, raiseExceptionExpired
from starlette.types import Message
import datetime 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randrange
from routers.plantillas import templates, fastapi
from starlette.responses import RedirectResponse

router = APIRouter(tags=['Authentication'])

# TODO Cambiar InMemoryBackedn por un tipo persistente
class SessionBackend(ABC):
    @abstractmethod
    async def read(self, session_id: str) -> Optional[Dict[str, Any]]:
        """ Read sesion data from the storage."""
        raise NotImplementedError()
    
    @abstractmethod
    async def write(self, data: Dict, session_id: Optional[str] = None) -> str:
        """ Write sesion data to the storage"""
        raise NotImplementedError()

    @abstractmethod
    async def remove(self, session_id: str) -> None:
        """ Remove session data from the storage. """
        raise NotImplementedError()

    @abstractmethod
    async def exists(self, sesion_id: str) -> bool:
        """ Test if storage contains session data for a given session_id. """
        raise NotImplementedError()

    async def generate_id(self) -> str:
        """ Generate a new session id. """
        return str(uuid4())

class InMemoryBackend(SessionBackend):
    """ Stores session data in a dictionary. """

    def __init__(self) -> None:
        print("initalized")
        self.data: dict = {}
    
    async def read(self, session_id: str) -> Optional[Dict]:
        result = self.data.get(session_id)
        if not result:
            return result
        return result.copy()
    
    async def write(self, session_data: Dict, session_id: Optional[str] = None) -> str:
        session_id = session_id or await self.generate_id()
        self.data[session_id] = session_data
        return session_id
    
    async def remove(self, session_id: str) -> None:
        del self.data[session_id]
    
    async def exists(self, session_id: str) -> bool:
        return session_id in self.data

class SessionCookie(APIKeyBase):
    def __init__(
        self,
        *,
        name: str,
        secret_key: str,
        data_model: Type[BaseModel],
        backend: Type[SessionBackend],
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
        max_age: timedelta = timedelta(days=1),
        expires: datetime = None,
        path: str = "/",
        domain: str = None,
        https_only: bool = False,
        httponly: bool = True,
        samesite: str = "strict",
    ):
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=name)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.signer = TimestampSigner(secret_key)
        self.backend = backend
        self.data_model = data_model
        self.max_age = max_age
        self.expires = expires
        self.path = path
        self.domain = domain
        self.https_only = https_only
        self.httponly = httponly
        self.samesite = samesite
    
    async def __call__(self, request: Request) -> Optional[str]:
        #api_key = request.cookies.get(model_name)
        api_key = request.cookies.get(self.model.name)
        if not api_key:
            print("test")
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated"
                )
            else:
                return None
        try:
            decode_api_key = b64decode(api_key.encode('utf-8'))
            session_id = self.signer.unsign(decode_api_key, max_age=self.max_age.total_seconds(), return_timestamp=False).decode('utf-8')
        except Exception as e:
            if self.auto_error:
                detail = "Not authenticated: "
                detail += "Session expired" if e is SignatureExpired else "Session altered"
                raise HTTPException(
                    status_code=401,
                    detail=detail
                )
            else:
                return None
        session_data = await self.backend.read(session_id)
        if not session_data:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated. Invalid session"
                )
            else:
                return None
        return session_data, session_id
    
    async def start_and_set_session(self, data: Type[BaseModel], response: Response):
        if type(data) is not self.data_model:
            raise TypeError("Data is not of right type")
        session_id = self.signer.sign(await self.backend.write(data))
        session_id = b64encode(session_id).decode('utf-8')
        #print("start session")
        #print(self.model.name)
        response.set_cookie(
            key=self.model.name,
            #key=model_name,
            value=session_id,
            max_age=self.max_age.total_seconds(),
            expires=self.expires,
            path=self.path,
            domain=self.domain,
            secure=self.https_only,
            httponly=self.httponly,
            samesite=self.samesite,
        )
        return

    async def end_and_delete_session(self, session: Optional[str], response: Response):
        #print("delete session")
        #print(self.model.name)
        #response.delete_cookie(model_name)
        response.delete_cookie(self.model.name)
        if session is not None:
            #print(session)
            #print(session[1])
            await self.backend.remove(session[1])
        return

class SessionData(BaseModel):
    id: str
    username: str

SESSION_NAME : str = "session"

test_session = SessionCookie(
    name=SESSION_NAME,
    secret_key="3st4 3s l4 C14v3539ur4",
    data_model=SessionData,
    backend=InMemoryBackend(),
    scheme_name="AppSisuts",
    auto_error=False
)

async def validarSessionforApis(session: Tuple[SessionData, str], db:Session):
    user = is_SuperUser(session, db)
    if user is None:
        raiseExceptionExpired(f"Invalid Credentials")
    return user
    
# TODO: Encapsular un método para redireccionar a una pagina, cuando el usuario no tenga permiso de Administrador
"""async def validarSessionforPages(request:Request, ret:str, session: Tuple[SessionData, str], db: Session = Depends(database.get_db)):
    if session is None:
        return RedirectResponse("/login?ret=" +  ret)
    userAdministrador = db.query(User).filter(User.email == session[0].username).first()
    if userAdministrador.is_superuser == 0:
        return RedirectResponse("/")
"""

@router.post("/api/login")
async def authenticate_User(userDado : Login, response: Response, ret: str = "/", db: Session = Depends(database.get_db)):
    #    formDado = await request.form()
    #    userDado = Login(**formDado)
    #    #print(userDado)
    userinDB = db.query(User).filter( User.correo == userDado.username ).first()
    if (userinDB != None and userDado.username == userinDB.correo  and Hash.verify(userinDB.contra, userDado.password) ):
        test_user = SessionData(username=userDado.username, id=userinDB.id)
        
        await test_session.start_and_set_session(test_user, response)
        print(test_user)
        return {"message": "Welcome!!!", "user": test_user}
        
    else:
        # TODO: borrar cualquier cookie de sesión existente, si se desea emplear el api/login
        #await test_session.end_and_delete_session(session, response)
        response.delete_cookie( "session" )
        raiseExceptionDataErr(f"Credenciales inválidas")
        

@router.get("/login")
def show_Login_View(request: Request, ret: str = "/main", db: Session = Depends(database.get_db)):
    return templates.TemplateResponse( name="login.html", context={ "request": request, "ret": ret, "envname": getSettingsNombreEnvActivo(db) } )

@router.get("/logout")
async def send_logout(response: Response,session: Optional[Tuple[SessionData, str]] = Depends(test_session)):
    await test_session.end_and_delete_session(session, response)
    return RedirectResponse('/login')

@router.get("/api/resetPassword/confirm-pwd/{email}")
async def reset_password( request: Request, email: EmailStr, referencia: str, response: Response, ret: str ="/api/resetPassword/confirm-pwd" , db: Session = Depends(database.get_db)):
    # datosVerificacion = UserResetPwdVerify(email=email, referencia=referencia)
    horaActual = datetime.datetime.now()
    tokenValido = db.query(UserResetPwd).filter( UserResetPwd.referencia == referencia ).first()
    
    print(tokenValido)
    if(tokenValido!= None and tokenValido.referencia != None and tokenValido.activado != 1 and horaActual<tokenValido.fechafin ):
        return templates.TemplateResponse(name="reset-password.html", context={"request": request, "email": email, "referencia": referencia, "ret": ret})
    else:
        return templates.TemplateResponse(name="invalid-token.html", context={"request": request, "message": "SU TOKEN SE HA CADUCADO, SOLICITE OTRO!!"})


@router.post("/api/resetPassword/update")
#async def update_password( request: Request, datosUpdate: UpdatePassword, referencia: str, email: EmailStr, pwdNuevo:str, pwdNuevoRepetir:str, ret: str = "/", db: Session = Depends(database.get_db) ):
async def update_password( request: Request, datosUpdate: UpdatePassword, response: Response, ret: str = "/", db: Session = Depends(database.get_db) ):
    #return({"message": "dentro de la api"})
    #if(email != null and referencia != null and pwdNuevo != null and pwdNuevoRepetir != null):
    print(datosUpdate)
    if(datosUpdate.email != null and datosUpdate.referencia != null and datosUpdate.pwdNuevo != null and datosUpdate.pwdNuevoRepetir != null):
        newUpdatePWd = Hash.bcrypt(datosUpdate.pwdNuevo)
        print(newUpdatePWd)
        user = db.query(User).filter(User.correo == datosUpdate.email).first()
        activadoReset = db.query(UserResetPwd).filter(UserResetPwd.referencia == datosUpdate.referencia).first()

        if (user != None and activadoReset != None):
            user.contra = newUpdatePWd
            user.update(db)

            activadoReset.activado = True
            activadoReset.update(db)
            print("password actualizado en la BD")
        return({"sms": "SU CONTRASEÑA HA SIDO ACTUALIZADA CORRECTAMENTE!!"})
    else:
        print("token no valido...")
        raiseExceptionDataErr(f"NO LLEGARON DATOS!!")


@router.post("/api/forgotPassword")
async def reset_password(request: Request, emailDado: ForgotPassword, responde: Response,  ret: str = "/ForgotPassword", db: Session = Depends(database.get_db)):
    #return templates.TemplateResponse( name="forgot-password.html", context={ "request": "correo", "ret": ret } )
    siExiste = ''
    mensajeRetorno = ''

    userinDB = db.query(User).filter( User.correo == emailDado.email ).first()
    # setting_email = db.query(Settings).filter( Settings.campo == "$EMAIL_CUENTA" ).first()
    # setting_password = db.query(Settings).filter( Settings.campo == "$EMAIL_PASSWORD").first()
    
    # # TODO: Obtener de la tabla de settings, la variable environment para obtener cual es el entorno actualmente activo
    # # y con ello, su respectiva url
    # setting_baseUrl = db.query(Settings).filter(Settings.campo == "$BASE_URL").first()

    # setting_emailResetTimeToken = db.query(Settings).filter(Settings.campo == "$EMAIL_RESET_TIME_TOKEN").first()
    SYS_NAME        = "Sites RUTA-TEC"
    EMAIL_CUENTA    = "sites2022gyds@gmail.com"
    EMAIL_PASSWORD  = "pwuzuxpwgjdfhaeh"
    BASE_URL        = "http://127.0.0.1:8000/"
    TIME_TOKEN_RP   = "10"

    
    if(userinDB):
        siExiste = 'si'
        # remitente = 'sisutscorporation21@gmail.com'
        newPassword = ''
        newPBcrypt = ''
        iterador = 0

        while iterador <= 6:
            newPassword += str(randrange(10))
            iterador+=1

        newPBcrypt = Hash.bcrypt(newPassword)

        horaActual = datetime.datetime.now()
        horaEspera = horaActual + datetime.timedelta(minutes=int(TIME_TOKEN_RP))
        #horaEspera = horaActual + datetime.timedelta(minutes=5)

        UserReset = UserResetPwd(
            email = emailDado.email,
            referencia = newPBcrypt,
            fechaini = horaActual,
            fechafin = horaEspera,
            confirmacion = True,
            activado = False
        )

        UserReset.create(db)
        db.commit()

        msg = MIMEMultipart()
        msg['Subject'] = "SERVICIO " + SYS_NAME
        msg['From'] = EMAIL_CUENTA
        msg['To'] = emailDado.email

        #text = "Por algún prublema reportese con el administrador del sistema"
        html = f"""\
        <!DOCTYPE html>
        <html lang="es">
            <head>
                <meta charset="utf-8">
                <title>{SYS_NAME}</title>
            </head>
            <body style="background-color: #fff ">
                <table style="max-width: 600px; padding: 10px; margin:0 auto; border-collapse: collapse;">
                    <tr>
                        <td style="background-color: #b7b7b7; text-align: left; padding: 0">
                            <center>
                                <img width="40%" style="display:block; margin: 1.5% 3%" src="https://drive.google.com/file/d/1s3Yc79ZueQz7mJpvMKgHaudNYFnTnP6G/view">
                            </center>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #002F5C">
                            <div style="color: #34495e; margin: 4% 10% 2%; text-align: justify;font-family: sans-serif">
                                <center><h2 style="color: #4edaf3; margin: 0 0 7px;">Solicitud para el cambio de contraseña</h2></center>
                                <p style="color: #ffffff; margin: 2px; font-size: 15px"> Ha solicitado el cambio de contraseña para su cuenta de la plataforma {SYS_NAME}, favor de <strong>confirmar</strong> en el siguiente botón y será redireccionado a un formulario.</p>
                                <ul style="font-size: 15px;  margin: 10px 0; list-style:none; color: #ffffff">
                                    <li>1. Cuenta con 10 minutos de valides para su token</li>
                                    <li>2. Si usted no realizo esta acción ignore el correo</li>
                                </ul>
                                    <br>
                                    <div style="width: 100%; text-align: center">
                                        <a href="{BASE_URL}api/resetPassword/confirm-pwd/{emailDado.email}?referencia={newPBcrypt}" style="text-decoration: none; border-radius: 5px; padding: 11px 23px; color: white; background-color: #3498db">CONFIRMAR</a>	
                                    </div><br>
                                <p style="color: #b3b3b3; font-size: 12px; text-align: center; margin: 30px 0 0"> {SYS_NAME}</p>
                            </div>
                        </td>
                    </tr>
                </table>

            </body>
        </html>
        """
        #part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        #msg.attach(part1)
        msg.attach(part2)
        #sms = 'HOLA! SU NUEVA CONTRASEÑA ES: '+ newPassword +' FAVOR DE INGRESAR Y CAMBIAR NUEVAMENTE SU CONTRASEÑA'
        #encabezado = 'Contraseña nueva para SISUTS'
        #sms = 'Subject: {}\n\n{}'.format(encabezado, sms)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.ehlo()
        s.login(EMAIL_CUENTA,EMAIL_PASSWORD)
        #server.sendmail(remitente, emailDado.email, sms.encode('utf-8'))
        #server.quit()
        s.sendmail(EMAIL_CUENTA, emailDado.email, msg.as_string())
        s.quit()
        mensajeRetorno = 'CORREO ENVIADO CORRECTAMENTE!!'

        db.query(User).filter_by(correo=emailDado.email).update(dict(contra=newPBcrypt))
        db.commit()
        #db.session.commit()
    else:
        siExiste= 'no'
        mensajeRetorno = 'No existen una cuenta de usuario con los datos proporcionados'
    return({"message": mensajeRetorno, "email": emailDado.email, "Existe": siExiste})