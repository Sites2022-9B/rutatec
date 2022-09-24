## comidas

Aplicación web correspondiente al Sistema de Información Institucional de la UTSelva
Tiene como funcionalidades las que corresponden a las tareas que se llevan a cabo en los diferentes
procesos administrativos, contemplando de forma general y principalmente el control del presupuesto,
y en lo particular, el registro de las operaciones efectuadas en los subprocesos administrativos
incluyendo la planeación, solicitud, ejecución y generación de reportes.

Requisitos: git (https://git-scm.com), tortoise git (https://tortoisegit.org) y visual studio code (https://code.visualstudio.com).
En el menú de inicio de windows, buscar Power shell, y ejecutarlo como administrador
capturar el comando:
    Set-ExecutionPolicy Unrestricted
    presiona Enter y cuando te pregunte por la opción a elegir, presiona la tecla S y nuevamente Enter

Extensiones para vscode:
 - Python y Pylance de microsoft, Intellij IDEA Keybindings
 
Cómo ejecutar el proyecto:
Abrir la terminal, estando en el directorio actual, ejecutar:
  virtualenv venv
  o bien: venv venv
Cerrar la terminal y abrir una nueva para que automáticamente abra la terminal en el entorno virtual venv
posteriormente ejecutar:
  python.exe -m pip install --upgrade pip

  pip install -r .\requirements.txt

  uvicorn main:app --reload

#Configurar acceso remoto a servidor postgresql14 en Windows
1. abrir el archivo postgresql.conf desde C:\Program Files\PostgreSQL\14\data\postgresql.conf
2. busca y descomenta la línea: listen_addresses = '*', si no tiene "*" entonces agregarlo
3. Busca y descomenta la lína: password_encryption = scram-sha-256, el método de cifrado puede variar con la versión (md5 o sha-256)
4. abrir el archivo pg_hba.conf desde C:\Program Files\PostgreSQL\14\data\pg_hba.conf
5. casi al final del archivo en la seccion IPV4 Local conections agregar la siguiente línea: 
    host    all          sisuts          0.0.0.0/0		        scram-sha-256
6. guardar ambos archivos y reiniciar el servicio de postgres desde el administrador de servicios de windows.
7. habilitar el puerto usado por postgres en el firewall o deshabilitar este último.