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

CREATE TABLE IF NOT EXISTS puntrutas (
	id SERIAL NOT NULL,
	rutas_id INT NOT NULL,
	longitud VARCHAR (30),
	latitud VARCHAR (30),
	PRIMARY KEY (id),
	CONSTRAINT puntrutas_rutas_id_fkey 
	FOREIGN KEY (rutas_id) REFERENCES rutas (id)
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
	CONSTRAINT historial_user_id_fkey 
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

-- Datos de los municipios registrados
INSERT INTO municipio(nombre) VALUES ('Ocosingo');
INSERT INTO municipio(nombre) VALUES ('Yajalón');
INSERT INTO municipio(nombre) VALUES ('San Cristobal');
INSERT INTO municipio(nombre) VALUES ('Tuxtla Gutiérrez');

-- Datos de las terminales conforme a su municipio
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'ADO', -92.099955, 16.909281);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - San cristobal', -92.099759, 16.908794);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - Tonina', -92.089376, 16.908687);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - Oxchuc', -92.098484, 16.907435);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - Bachajón', -92.099884, 16.914542);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - Altamirano', -92.089208, 16.908727);
INSERT INTO terminales (munic_id, nombre, longitud, latitud) VALUES ( 1, 'Ocosingo - Playas', -92.098480, 16.907823);

--Usuarios de Unidades Responsables
insert into "usuario" values (1,'Pablo','Ruiz', 'pablo@gmail.com', 'pablofabian123',false);
insert into "usuario" values (2,'admin','pruebas', 'pablofabianruizconstantino@gmail.com', 'admin123',false);
insert into "usuario" values (3,'Henry','Lopez', 'henry@gmail.com', 'HenryLV28',false);
insert into "usuario" values (4,'Eduardo','Gutierrez', 'quique@gmail.com', 'EduardoG123',false);
SELECT setval ('usuario_id_seq', 4, true);

-- Nombre y descripción de las rutas registradas
INSERT INTO rutas VALUES(1,'RUTA1', 'Barrio Benito Juárez, Mercado centro, Ganadera, Deportiva, Magisterial');
INSERT INTO rutas VALUES(2,'RUTA2', 'Mercado centro, Agroveterinaria Victoria, Escuela Primaria Felipe Carrillo Puerto, Hotel Posada San Luis, Secundaria Merie Curie, INE ocosingo, ADO, Soluciones integrales en Sistemas, La casa de las llantas, Barrio Primavera');
INSERT INTO rutas VALUES(3,'RUTA3', 'Mercado centro,  Parque central,  Hotel zepeda, Secundaria Merie Curie, INE ocosingo, ADO, Barrio San Sebastian.');
SELECT setval ('rutas_id_seq', 3,true);

-- Datos de prueba para la tabla historial
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 2, '21/10/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (2, 3, '23/11/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 1, '25/10/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (3, 2, '26/10/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (1, 3, '29/11/2022');
INSERT INTO historial(user_id, rutas_id, fecha) VALUES (3, 1, '28/11/2022');

-- Coordenadas de la RUTA 1 (Lng - Lat)
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
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.091950, 16.908487);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.094026, 16.907763);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093822, 16.907207);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093814, 16.907158);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093709, 16.906912);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093642, 16.906702);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093516, 16.906370);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093505, 16.906311);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093369, 16.905988);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093288, 16.905775);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093124, 16.905346);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093046, 16.905164);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.093025, 16.905097);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.092598, 16.903886);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.092572, 16.903825);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.092188, 16.902783);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.092094, 16.902608);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.091791, 16.902233);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.091448, 16.902046);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.091268, 16.901969);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.090995, 16.901884);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.090587, 16.901923);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.090000, 16.901938);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.089286, 16.901931);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.088793, 16.901902);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.088506, 16.901805);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.088015, 16.901471);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.087747, 16.901325);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.087607, 16.901297);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.087497, 16.901304);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.086062, 16.901515);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.085740, 16.901584);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.085123, 16.901689);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.084831, 16.901800);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.084434, 16.902013);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.084354, 16.902051);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.083993, 16.902094);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.083722, 16.902068);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.083362, 16.901958);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.083075, 16.901791);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.082233, 16.900900);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.082110, 16.900805);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.080715, 16.900343);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.080426, 16.900197);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 1, -92.079524, 16.900648);

-- Coordenadas de la RUTA 2 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090258, 16.908437);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090000, 16.908550);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090247, 16.909125);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090301, 16.909248);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090623, 16.909853);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090633, 16.909935);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090741, 16.910059);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.090891, 16.910377);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.091085, 16.910716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.091449, 16.911434);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.091900, 16.912112);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.092586, 16.911891);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.093338, 16.911630);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.094276, 16.911322);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.094775, 16.911090);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.094963, 16.911009);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.095177, 16.910921);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.095172, 16.910885);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096127, 16.910234);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096460, 16.910726);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096712, 16.911045);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096779, 16.911019);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096806, 16.910942);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.096860, 16.910890);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.097488, 16.910521);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.098035, 16.910228);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.099800, 16.909227);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.099606, 16.907580);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.102337, 16.906585);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.101645, 16.905465);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.103796, 16.904675);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.104670, 16.904490);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.105066, 16.904336);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.105324, 16.904212);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.106343, 16.903976);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.106569, 16.903915);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.106783, 16.903802);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.107942, 16.906409);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.109393, 16.905693);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.111914, 16.906309);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.112654, 16.906463);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.112912, 16.906422);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.113352, 16.906083);

-- Coordenadas de la RUTA 3 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.090017, 16.909178);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.090262, 16.909075);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.090833, 16.908867);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.091992, 16.908488);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.094033, 16.907762);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.096229, 16.907031);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.096803, 16.908658);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.098633, 16.907960);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.097957, 16.906423);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.097882, 16.906146);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.097850, 16.905946);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.097856, 16.905772);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.098828, 16.905439);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.099134, 16.906291);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.099617, 16.906158);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.100663, 16.905814);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.101634, 16.905454);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.103850, 16.904671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.104676, 16.904507);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.105287, 16.904199);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.106559, 16.903932);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 3, -92.106789, 16.903789);

