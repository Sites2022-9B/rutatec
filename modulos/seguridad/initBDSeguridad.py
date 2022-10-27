from sqlalchemy.orm import Session
from db.database import get_db
from typing import List
from modulos.seguridad.models import User
from .sec.sec_hashing import Hash

#Inicializar la cuenta de usuario inicial
FIRST_SUPERUSER : str = "pablofabianruizconstantino@gmail.com"
FIRST_SUPERUSER_PASSWORD : str = "1234"
userPredet : User = User()

def initBDdatos():
    # En este contexto, es necesario next to get a session out of the generator según
    # https://stackoverflow.com/questions/65982681/how-to-access-the-database-from-unit-test-in-fast-api 
    try:
        db : Session = next( get_db() )
        # Encriptar el pwd de todas las cuentas de usuario que no lo estén
        queryUsers = db.query(User).filter(User.isEncrypted == False)
        print(queryUsers)
        listUsers : List[User] = queryUsers.all()
        print("list user",listUsers)
        for user in listUsers:
            user.contra = Hash.bcrypt(user.contra)
            user.isEncrypted = True
            user.update(db)
        #print ( jsonable_encoder(user) )
    except (BaseException) as err:
        print("Error presentado en: initBDdatos(). No se pudieron encriptar los pwd que no lo están")
        print(err)