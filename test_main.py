# Para efectuar las pruebas https://fastapi.tiangolo.com/tutorial/testing/
# Para realizar depuraciones https://fastapi.tiangolo.com/tutorial/debugging/
# Una vez instalado: pip install pytest
# ejecutar: cls; pytest -vv
from fastapi.testclient import TestClient
from fastapi import status
from modulos.seguridad.schemas import Login
from modulos.seguridad import r_authentication, initBDSeguridad
from db import database
#from .main import app
import main
client = TestClient(main.app)

TABLES = ['user', 'empleados', 'procexeccont','procexec', 'procactexec']

# Datos predeterminados de prueba, usando una cuenta válida
USERNAME = "pablofabianruizconstantino@gmail.com"
PASSWORD = "pablofabian123"
SESSION_NAME : str = r_authentication.SESSION_NAME

# Test relacionados a: LOGIN incorrectos y correctos
# --------------------------------------------------------------------------------------------------
def test_api_login_incorrecto1():
    response = client.post("/api/login")
    # si no se envía ninguna cuenta de usuario entonces marcar error de entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_api_login_correcto():
    response = client.post("/api/login", json={"username": USERNAME, "password":PASSWORD})
    assert response.status_code == status.HTTP_200_OK
    message : str = response.json()['message']
    assert message.startswith('Welcome')

    resp = response.json()['user']
    resp.update( {'password': '*'} ) # Se asigna un pwd dummy
    user = Login (**resp)
    assert user.username == USERNAME
    return response


# Método genérico para autentificar al usuario válido
# --------------------------------------------------------------------------------------------------
# def getValidSession(webPage):
#     response = test_api_login_correcto()
#     mycookieSession = str( dict(response.headers)["set-cookie"] ).split( SESSION_NAME + '="')[1].split('"; ')[0]
#     return client.get(webPage, cookies= {SESSION_NAME: mycookieSession } )


# Test relacionados a: Main sin acceso y con accesso
# --------------------------------------------------------------------------------------------------
def getValidSession(webPage):
    response = test_api_login_correcto()
    mycookieSession = str( dict(response.headers)["set-cookie"] ).split(SESSION_NAME + '="')[1].split('"; ')[0]
    return client.get(webPage, cookies= {SESSION_NAME: mycookieSession } )

def test_page_main_sinacceso():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    # cómo se podrá validar el contenido de la página web? verificando que se solicite el username y el password?
    assert str(response.content).__contains__("username") and str(response.content).__contains__("password") 

# def test_page_main_conacceso():
#     response = getValidSession("/main")
#     assert response.status_code == status.HTTP_200_OK
#     # cómo se podrá validar el contenido de la página web? verificando que inicia con index.html?
#     assert str(response.content).startswith("b\'<!--index.html-->")

