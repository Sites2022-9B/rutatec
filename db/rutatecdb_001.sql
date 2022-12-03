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
INSERT INTO rutas VALUES(1,'RUTA 1', 'Barrio Benito Juárez, Mercado centro, Ganadera, Deportiva, Magisterial');
INSERT INTO rutas VALUES(2,'RUTA 2', 'Mercado centro, Agroveterinaria Victoria, Escuela Primaria Felipe Carrillo Puerto, Hotel Posada San Luis, Secundaria Merie Curie, INE ocosingo, ADO, Soluciones integrales en Sistemas, La casa de las llantas, Barrio Primavera');
INSERT INTO rutas VALUES(3,'RUTA 3', 'Mercado centro,  Parque central,  Hotel zepeda, Secundaria Merie Curie, INE ocosingo, ADO, Barrio San Sebastian.');
INSERT INTO rutas VALUES(4,'RUTA 4', 'Mercado centro, Modatelas ocosingo, Hotel Arenas, RAMFESA construcciones, Ferretería Cruz, Unidad deportiva, Casa pequeñeses international, Servifácil, AutoTech de la Selva, PEMEX Servicio Solorzano López, Universidad Tecnológica de la Selva, Hospital de 2do Nivel ocosingo');
INSERT INTO rutas VALUES(5,'RUTA 5', 'Mercado centro, Modatelas ocosingo, Hotel Arenas, RAMFESA construcciones, Ferretería Cruz, Unidad deportiva, Casa pequeñeses international, ANTARIX ocosingo, Modelorama, Hospital Rural ocosingo, Las cuatro esquinas, PRO salud, La Ganadera, Hotel imperial');
INSERT INTO rutas VALUES(6,'RUTA 6', 'Mercado centro, Modatelas Ocosingo, Abarrotes El Girasol, Hotel Arenas, Papeleria El Triángulo, Cruz Roja Mexicana, Willys 1 Ocosingo, Caballo negro, Soriana Express, Mi Bodega Aurrera, Materiales El Pacífico, ISSSTE, Hacienda La Ilusión, Parque central, Hotel Imperial');
SELECT setval ('rutas_id_seq', 6,true);

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

-- Coordenadas de la RUTA 4 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088679, 16.908655);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088629, 16.908642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088516, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088436, 16.908590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088310, 16.908567);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088128, 16.908531);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087750, 16.908449);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087624, 16.908426);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084538, 16.907716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084500, 16.907706);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084489, 16.907688);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084485, 16.907676);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084472, 16.907631);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084386, 16.907364);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084226, 16.906917);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084006, 16.906332);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.083791, 16.905747);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.083657, 16.905424);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.083630, 16.905342);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.083421, 16.904367);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082901, 16.901757);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082906, 16.901738);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082970, 16.901720);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082267, 16.900930);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082144, 16.900830);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.082109, 16.900803);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.081974, 16.900744);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.081070, 16.900464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.080461, 16.900219);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.080415, 16.900186);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.080139, 16.899947);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.079082, 16.898895);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.079031, 16.898874);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.077817, 16.898277);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.075383, 16.896952);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.073441, 16.896087);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.073298, 16.896050);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.073161, 16.896058);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.072198, 16.895932);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.071417, 16.895992);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.070351, 16.896343);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.070221, 16.896360);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.069761, 16.896390);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.067907, 16.896301);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.067450, 16.896373);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066893, 16.896743);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066712, 16.897035);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066546, 16.897636);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066424, 16.897775);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066338, 16.897824);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.066248, 16.897851);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.064904, 16.897776);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.063864, 16.897487);

-- Coordenadas de la RUTA 5 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088679, 16.908655);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088629, 16.908642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088516, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088436, 16.908590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088310, 16.908567);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088128, 16.908531);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087750, 16.908449);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087624, 16.908426);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084538, 16.907716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084500, 16.907706);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084489, 16.907688);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084485, 16.907676);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084472, 16.907631);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084386, 16.907364);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084226, 16.906917);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084006, 16.906332);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083791, 16.905747);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083657, 16.905424);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083630, 16.905342);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083421, 16.904367);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.082901, 16.901757);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083028, 16.901722);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083342, 16.901947);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083782, 16.902073);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084227, 16.902065);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084396, 16.902057);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084785, 16.901813);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085083, 16.901708);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085509, 16.901616);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086027, 16.901518);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086606, 16.901431);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087100, 16.901351);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087540, 16.901289);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087693, 16.901304);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088036, 16.901484);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088412, 16.901751);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088712, 16.901879);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088886, 16.901912);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089575, 16.901935);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090018, 16.901943);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090544, 16.901925);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090997, 16.901897);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091241, 16.901953);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091507, 16.902081);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091813, 16.902253);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092025, 16.902511);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092199, 16.902816);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092282, 16.903028);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092517, 16.903676);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092613, 16.903940);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092873, 16.904656);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.093031, 16.905128);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092653, 16.905277);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.092194, 16.905444);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091692, 16.905634);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090992, 16.905911);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090565, 16.906085);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090228, 16.906219);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090450, 16.906488);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090858, 16.907027);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091205, 16.907472);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091378, 16.907696);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091557, 16.907955);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090992, 16.908138);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090407, 16.908343);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090009, 16.908521);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089966, 16.908436);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089800, 16.908472);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089427, 16.908564);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089447, 16.908640);

-- Coordenadas de la RUTA 6 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088679, 16.908655);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088629, 16.908642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088516, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088436, 16.908590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088310, 16.908567);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088128, 16.908531);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087750, 16.908449);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087624, 16.908426);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084656, 16.907746);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084591, 16.908060);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085559, 16.908300);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086243, 16.908475);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087142, 16.908688);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087762, 16.908852);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087821, 16.908942);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088148, 16.909882);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088918, 16.909582);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089505, 16.909366);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089899, 16.909212);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.090258, 16.909060);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.090700, 16.909974);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091131, 16.910774);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091458, 16.911405);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091887, 16.912085);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.092469, 16.913083);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.093051, 16.914202);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.093837, 16.915788);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.094459, 16.916866);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.094566, 16.916904);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.095032, 16.916777);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.096098, 16.916419);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.096920, 16.916140);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098066, 16.915699);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098163, 16.915654);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098231, 16.915603);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098966, 16.914728);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099602, 16.914161);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099691, 16.914174);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099761, 16.914146);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099769, 16.914054);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099715, 16.914005);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099605, 16.913967);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098905, 16.913025);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098867, 16.912912);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098847, 16.912789);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098868, 16.912478);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098920, 16.912332);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099019, 16.912155);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099816, 16.911478);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099998, 16.911286);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100162, 16.910945);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100216, 16.910614);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100161, 16.910206);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099944, 16.909472);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099741, 16.909158);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099741, 16.909158);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098645, 16.907952);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098441, 16.907513);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.097188, 16.907883);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.096475, 16.908088);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.095717, 16.908264);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.095072, 16.908439);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.094337, 16.908683);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.094205, 16.908233);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.094032, 16.907780);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.093824, 16.907190);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.092987, 16.907477);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091614, 16.907932);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.090815, 16.908204);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.090004, 16.908517);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089961, 16.908432);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089519, 16.908539);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089491, 16.908633);
