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
USERNAME = initBDSeguridad.FIRST_SUPERUSER
PASSWORD = initBDSeguridad.FIRST_SUPERUSER_PASSWORD
SESSION_NAME : str = r_authentication.SESSION_NAME

# Test relacionados a: LOGIN incorrectos y correctos
# --------------------------------------------------------------------------------------------------
def test_api_login_incorrecto1():
    response = client.post("/api/login")
    # si no se envía ninguna cuenta de usuario entonces marcar error de entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_api_login_incorrecto2():
    response = client.post("/api/login", json={"username":USERNAME, "password":"invalidPWD"})
    # si se envía una cuenta de usuario incorrecta entonces marcar error de creenciales inválidas
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid Credentials'}

def test_api_login_correcto():
    response = client.post("/api/login", json={"username": USERNAME, "password":PASSWORD})
    assert response.status_code == status.HTTP_200_OK
    #assert response.json() == {'123':'abc'}
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

def test_page_main_conacceso():
    response = getValidSession("/main")
    assert response.status_code == status.HTTP_200_OK
    # cómo se podrá validar el contenido de la página web? verificando que inicia con index.html?
    assert str(response.content).startswith("b\'<!--index.html-->")


# Test relacionados a: Inserción de datos aleatorios a base de datos
# --------------------------------------------------------------------------------------------------
def test_data_generator_table_user():
    datagen = open('test/user.sql')
    response = database.execFirst(str(datagen.read()), TABLES[0])
    assert response == TABLES[0]

def test_data_generator_table_empleados():
    datagen = open('test/empleados.sql')
    response = database.execFirst(str(datagen.read()), TABLES[1])
    assert response == TABLES[1]

def test_data_generator_table_procexeccont():
    datagen = open('test/procexeccont.sql')
    response = database.execFirst(str(datagen.read()), TABLES[2])
    assert response == TABLES[2]

def test_data_generator_table_procexec():
    datagen = open('test/procexec.sql')
    response = database.execFirst(str(datagen.read()), TABLES[3])
    assert response == TABLES[3]

def test_data_generator_table_procactexec():
    datagen = open('test/procactexec.sql')
    response = database.execFirst(str(datagen.read()), TABLES[4])
    assert response == TABLES[4]