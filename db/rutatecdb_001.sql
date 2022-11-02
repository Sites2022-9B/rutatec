CREATE TABLE IF NOT EXISTS "settings" (
	"id" SERIAL NOT NULL,
	"campo" VARCHAR(50) NOT NULL,
	"valor" TEXT NOT NULL,
	"user_id" INT,
	PRIMARY KEY("id")
);

INSERT INTO "settings" (campo, valor,user_id) VALUES('environments','{"DEV - Desarrollo": {"imagen": "13_20220812143214275571.PNG", "activo": "true", "url": "http://localhost:8000"}}',0);

CREATE TABLE IF NOT EXISTS controlversionbd(
	id SERIAL NOT NULL, 
	archivo_tecnico VARCHAR (100) NOT NULL, 
	fechaejecucion timestamp NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS pages (
	id SERIAL NOT NULL,
	nombre VARCHAR(50),
	url VARCHAR(50),
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS usuario (
	id SERIAL NOT NULL,
	nombre VARCHAR (50),
	Apellidos VARCHAR (50),
	correo VARCHAR (50),
	contra VARCHAR (300),
	"isEncrypted"	BOOLEAN,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS rutas (
	id SERIAL NOT NULL,
	nombre VARCHAR (30),
	descripcion VARCHAR (500),
	PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS rutguardadas (
	id SERIAL NOT NULL,
	user_id INT NOT NULL,
	rutas_id INT NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT rutguardadas_user_id_fkey 
	FOREIGN KEY (user_id) REFERENCES usuario (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
	CONSTRAINT rutguardadas_rutas_id_fkey 
	FOREIGN KEY (rutas_id)REFERENCES rutas (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS puntrutas (
	id SERIAL NOT NULL,
	rutas_id INT NOT NULL,
	longitud VARCHAR (30),
	latitud VARCHAR (30),
	PRIMARY KEY (id),
	CONSTRAINT puntrutas_rutas_id_fkey 
	FOREIGN KEY (rutas_id)REFERENCES rutas (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS historial (
	id SERIAL NOT NULL,
	user_id INT NOT NULL,
	rutas_id INT NOT NULL,
	fecha DATE,
	PRIMARY KEY (id),
	CONSTRAINT historial_rutas_id_fkey 
	FOREIGN KEY (rutas_id)REFERENCES rutas (id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
	CONSTRAINT rutguardadas_user_id_fkey 
	FOREIGN KEY (user_id) REFERENCES usuario (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS municipio (
	id SERIAL NOT NULL,
	nombre VARCHAR (30),
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS terminales (
	id SERIAL NOT NULL,
	munic_id INT NOT NULL,
	nombre VARCHAR(50),
	longitud VARCHAR (100),
	latitud VARCHAR (100),
	PRIMARY KEY(id),
	CONSTRAINT terminales_munic_id_fkey 
	FOREIGN KEY (munic_id) REFERENCES municipio (id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS "userreset" (
	"id"	SERIAL NOT NULL,
	"email"	VARCHAR(100) NOT NULL,
	"referencia"	VARCHAR(100) NOT NULL,
	"fechaini"	timestamp NOT NULL,
	"fechafin"	timestamp,
	"confirmacion"	BOOLEAN,
	"activado"	BOOLEAN,
	PRIMARY KEY("id")
);

CREATE INDEX IF NOT EXISTS ix_userreset_id ON "userreset" ("id");
CREATE INDEX IF NOT EXISTS ix_userreset_referencia ON "userreset" ("referencia");


insert into "usuario" values (1,'Pablo','Ruiz', 'pablo@gmail.com', '1234',false);
--Usuarios de Unidades Responsables
insert into "usuario" values (2,'Henry','Lopez', 'henry@gmail.com', '1234',false);
insert into "usuario" values (3,'Eduardo','Gutierrez', 'quique@gmail.com', '1234',false);
SELECT setval ('usuario_id_seq', 3, true);

INSERT INTO rutas VALUES(1,'RUTA1', 'ISJISJNCSIJNSICJNSICJSNIENCISE');
INSERT INTO rutas VALUES(2,'RUTA2', 'ISJISJNCSIJNSICJNSICJSNIENCISE');
INSERT INTO rutas VALUES(3,'RUTA3', 'ISJISJNCSIJNSICJNSICJSNIENCISE');
INSERT INTO rutas VALUES(4,'RUTA4', 'ISJISJNCSIJNSICJNSICJSNIENCISE');
INSERT INTO rutas VALUES(5,'RUTA5', 'ISJISJNCSIJNSICJNSICJSNIENCISE');
SELECT setval ('rutas_id_seq',5,true);

SELECT setval ('usuario_id_seq', 3, true);

INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 2, '25/10/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 3, '25/10/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 4, '25/10/2022');

-- Coordenadas de la RUTA 1
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.107379, 16.911392);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106655, 16.910853);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106601, 16.910771);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106574, 16.910637);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106445, 16.910191);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106381, 16.910052);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106365, 16.909893);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106311, 16.909857);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.106134, 16.910052);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.105871, 16.910288);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.105560, 16.910642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.104648, 16.911653);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.104369, 16.911961);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.102884, 16.911638);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.102798, 16.911725);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.102690, 16.912105);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.102454, 16.912115);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100255, 16.913711);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099756, 16.914035);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099702, 16.913994);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099621, 16.913993);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098903, 16.913055);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098849, 16.912813);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098839, 16.912629);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098849, 16.912526);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098887, 16.912408);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098946, 16.912249);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099241, 16.911915);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099496, 16.911725);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099823, 16.911466);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099992, 16.911304);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100113, 16.911083);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100183, 16.910873);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100212, 16.910670);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100209, 16.910437);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100207, 16.910428);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.100161, 16.910210);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099976, 16.909590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099756, 16.909174);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099375, 16.908794);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.099080, 16.908502);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098748, 16.908127);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.098447, 16.907532);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.096516, 16.908071);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.095084, 16.908430);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093265, 16.909087);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.091296, 16.909739);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.090840, 16.908867);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES (2, -92.105914, 16.912515);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES (2, -92.105184, 16.912977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES (2, -92.105093, 16.912972);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES (2, -92.104648, 16.912463);