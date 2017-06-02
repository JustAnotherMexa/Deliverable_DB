# Deliverable_DB

Manual de instalación y uso de sistema de citas y pacientes para un consultorio dental
 
Instalación de sistemas
Para el funcionamiento del sistema se debe de contar con los siguientes sistemas instalados en el equipo
PyCharm
Oracle
cx_Oracle
django-tables2
Abrir proyecto
Para adquirir los archivos fuente de la aplicación deben de ser obtenidos de GitHub
Conexión a base de datos
	La conexión a la base de datos se puede realizar de dos maneras. La primera es conectarse a la base de datos ubicada en un servidor de DigitalOcean y la segunda es utilizar una base de datos local.
Servidor
	Para conectarse al servidor de DigitalOcean, el cual es un servidor CentOs es necesario utilizar las siguientes credenciales en el archivo de settings de django:

 
Local
	Para la utilización de una base de datos local, es necesario utilizar el DUMP file proporcionado. Esto generará las tablas, procedimientos y usuarios necesarios para el funcionamiento de la tabla. Para lograr esto se utilizó el wizard de recuperación de Oracle. De igual manera es necesario configurar el archivo de settings.py de la siguiente manera:

 
Servidor local
Una vez configurado el acceso a la base de datos se continúa corriendo el servidor local por medio de PyCharm presionando el botón de play en la parte superior derecha de la pantalla. 

O bien en la terminal ubicada en la parte inferior izquierda

Dar el comando “python manage.py runserver” que mostrara la siguiente salida en la terminal

 
Acceso web
En caso de querer postear la aplicación 
Por default, el servidor de PyCharm corre de forma local bajo el puerto 8000. Se re-direcciona al puerto 80 con el siguiente comando:
Python manage.py runserver 0.0.0.0:80
Lo anterior se realiza con la finalidad de hacer un port-forward al puerto 80 para poder utilizar DDNS y hostear la página en línea.
Navegacion en sitio web
Usuarios
Paciente
Para acceder a una cuenta de paciente es posible generar un usuario nuevo o entrar con las credenciales.
Usuario: carmela
Contraseña: hola1234
El Paciente tiene acceso a las funcionalidades de citas, crear nueva cita y consultar sus citas.
Doctor
	Para tener acceso a los permisos propios de una cuenta de doctor, es necesario crear un usuario nuevo y completar las formas de registro.
Posteriormente, el rol debe ser asignado por una cuenta de administrador, bajo la pestaña de usuarios. En esta pestaña, el administrador selecciona el usuario y el permiso que se desee otorgar.
	Las siguientes credenciales ya cuentan con los permisos de Doctor:
Usuario: afox95
Contraseña: hola1234
 
Administrador
	Para tener permisos de administrador, se proporciona una cuenta default con las siguientes credenciales:
Usuario: jacto
Contraseña: hola1234
	Desde esta interfaz, se pueden asignar los roles de administrador y doctor. Asimismo, el administrador es el único usuario capaz de manejar cuestiones financieras tales como hacer pagos, registrar tipos de cambio.
	De igual forma, solamente el administrador puede agregar tratamientos y materiales a la base de datos.
 
 
 
