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
INSERT INTO rutas VALUES(2,'RUTA 2', 'Mercado centro, Hotel Arenas, Deportiva, Servifacil, Pemex, Universidad Tecnologica de la Selva, Hospital de Segundo Nivel');
INSERT INTO rutas VALUES(3,'RUTA 3', 'Mercado centro,  Parque central,  Hotel zepeda, Secundaria Merie Curie, INE ocosingo, ADO, Barrio San Sebastian.');
INSERT INTO rutas VALUES(4,'RUTA 4', 'Mercado centro, Modatelas ocosingo, Hotel Arenas, Cruz Roja, Caballo Negro, Bodega Aurrera, Las Vegas 2');
INSERT INTO rutas VALUES(5,'RUTA 5', 'Mercado centro, Modatelas ocosingo, Hotel Arenas,Deportiva, Panteon Municipal, Internacional, CNO, Niño Fundado');
INSERT INTO rutas VALUES(6,'RUTA 6', 'Mercado centro,  Unidad Deportiva, Hospital Rural de Ocosingo, Cuatro Esquinas , Taqueria El Plebe, El Naranjo');
INSERT INTO rutas VALUES(7,'RUTA 7', 'Ferretería el Paisano, Colegio Universitario Versalles, Farmacia del Ahorro, Restaurante Caballo Negro , Carnitas Maite, Dulceria París, Telcel Ocosingo, Moto Galeria, Filtros y Lubricantes Mariscal, Materiales Del Mercado, La Sibalteca, Pemex, Nissan Zero Emission');
INSERT INTO rutas VALUES(8,'RUTA 8', 'Mercado centro, Biblioteca Publica, Tienda Milano, Importaciones Super Remate, Heco Tours, Farmacia Yireh, Tacos Torres, Telesecundari Jose Vasconcelos,Terapia de Sanacion');
INSERT INTO rutas VALUES(9,'RUTA 9', 'Mercado centro, Elektra, Casa De Huespedes, Hospital, Aceros del Grijalva, Iglesia Petecostal');
INSERT INTO rutas VALUES(10,'RUTA 10', 'Mercado centro, Pedal de Oro Chiapas, Hotel Arenas, Area Verdes, Telesecundaria, Magisterial');
INSERT INTO rutas VALUES(11,'RUTA 11', 'Mercado centro, Agroveterinaria Victoria, Escuela Primaria Felipe Carrillo Puerto, Hotel Posada San Luis, Secundaria Merie Curie, INE ocosingo, ADO, Soluciones integrales en Sistemas, La casa de las llantas, Barrio Primavera');


SELECT setval ('rutas_id_seq', 10,true);

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

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088679, 16.908655);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088629, 16.908642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088516, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088436, 16.908590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088310, 16.908567);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.088128, 16.908531);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087750, 16.908449);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087624, 16.908426);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084538, 16.907716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084500, 16.907706);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084489, 16.907688);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084485, 16.907676);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084472, 16.907631);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084386, 16.907364);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084226, 16.906917);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.084006, 16.906332);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.083791, 16.905747);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.083657, 16.905424);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.083630, 16.905342);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.083421, 16.904367);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082901, 16.901757);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082906, 16.901738);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082970, 16.901720);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082267, 16.900930);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082144, 16.900830);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.082109, 16.900803);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.081974, 16.900744);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.081070, 16.900464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.080461, 16.900219);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.080415, 16.900186);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.080139, 16.899947);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.079082, 16.898895);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.079031, 16.898874);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.077817, 16.898277);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.075383, 16.896952);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.073441, 16.896087);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.073298, 16.896050);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.073161, 16.896058);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.072198, 16.895932);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.071417, 16.895992);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.070351, 16.896343);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.070221, 16.896360);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.069761, 16.896390);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.067907, 16.896301);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.067450, 16.896373);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066893, 16.896743);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066712, 16.897035);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066546, 16.897636);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066424, 16.897775);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066338, 16.897824);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.066248, 16.897851);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.064904, 16.897776);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 2, -92.063864, 16.897487);


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
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084656, 16.907746);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.084591, 16.908060);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.085559, 16.908300);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.086243, 16.908475);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087142, 16.908688);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087762, 16.908852);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.087821, 16.908942);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088148, 16.909882);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.088918, 16.909582);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.089505, 16.909366);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.089899, 16.909212);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.090258, 16.909060);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.090700, 16.909974);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.091131, 16.910774);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.091458, 16.911405);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.091887, 16.912085);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.092469, 16.913083);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.093051, 16.914202);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.093837, 16.915788);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.094459, 16.916866);

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.094472, 16.916916);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.094477, 16.917020);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.094555, 16.917284);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.092314, 16.918061);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 4, -92.092256, 16.918078);


-- Coordenadas de la RUTA 5 (Lng - Lat)

INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088626, 16.908638);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088403, 16.908587);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087622, 16.908405);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086823, 16.908223);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085691, 16.907964);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085133, 16.907833);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084468, 16.907707);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084449, 16.907571);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084312, 16.907168);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084012, 16.906344);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083661, 16.905418);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083621, 16.905313);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083412, 16.904381);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083099, 16.902896);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.082935, 16.902147);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.082897, 16.901903);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.082890, 16.901727);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.082973, 16.901699);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083314, 16.901938);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083593, 16.902028);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.083990, 16.902077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084390, 16.902051);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.084819, 16.901799);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085079, 16.901702);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.085961, 16.901535);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.086285, 16.901483);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087540, 16.901293);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087693, 16.901308);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.087985, 16.901459);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088436, 16.901764);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.088787, 16.901901);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.089484, 16.901934);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.090543, 16.901919);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091039, 16.901873);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.091946, 16.901565);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.093735, 16.900918);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.095004, 16.900402);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.096973, 16.899632);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.097134, 16.899609);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.096954, 16.900906);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.096890, 16.901871);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.096906, 16.901979);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.096967, 16.902135);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.098486, 16.901527);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.100651, 16.900708);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.100841, 16.901126);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 5, -92.101413, 16.903711);



-- Coordenadas de la RUTA 6 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088626, 16.908638);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088403, 16.908587);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087622, 16.908405);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086823, 16.908223);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085691, 16.907964);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085133, 16.907833);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084468, 16.907707);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084449, 16.907571);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084312, 16.907168);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084012, 16.906344);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083661, 16.905418);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083621, 16.905313);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083412, 16.904381);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083099, 16.902896);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.082935, 16.902147);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.082897, 16.901903);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.082890, 16.901727);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.082973, 16.901699);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083314, 16.901938);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083593, 16.902028);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.083990, 16.902077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084390, 16.902051);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.084819, 16.901799);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085079, 16.901702);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.085961, 16.901535);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.086285, 16.901483);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087540, 16.901293);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087693, 16.901308);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.087985, 16.901459);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088436, 16.901764);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.088787, 16.901901);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.089484, 16.901934);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.090543, 16.901919);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091039, 16.901873);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.091946, 16.901565);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.093735, 16.900918);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.095004, 16.900402);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.096973, 16.899632);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.097134, 16.899609);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.097288, 16.898982);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.097650, 16.898504);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.098860, 16.897585);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099010, 16.897428);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099077, 16.897490);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099200, 16.897708);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099299, 16.897718);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099350, 16.897680);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.099657, 16.897498);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100132, 16.897344);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100457, 16.897323);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.100814, 16.897906);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.101643, 16.897506);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.102147, 16.898363);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 6, -92.102571, 16.899156);

-- Coordenadas de la RUTA 7 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.089396, 16.908569);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.089165, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.088762, 16.907361);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.089343, 16.907113);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.090070, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.090766, 16.910102);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.091445, 16.911406);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.091886, 16.912098);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.092471, 16.913078);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.093045, 16.914202);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.093834, 16.915785);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.094454, 16.916873);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.094518, 16.916891);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.094566, 16.916896);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.094620, 16.916899);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.095808, 16.916499);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.097391, 16.915960);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.098129, 16.915680);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.098180, 16.915642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.098695, 16.915031);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.099600, 16.914149);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.099641, 16.914166);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.099673, 16.914173);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.099704, 16.914173);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.099752, 16.914163);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.100499, 16.915201);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.101208, 16.916668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.101793, 16.917746);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.102121, 16.918138);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.103883, 16.919988);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.104890, 16.921058);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 7, -92.104952, 16.921009);

-- Coordenadas de la RUTA 8 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.090133, 16.909122);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.090700, 16.908906);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.091382, 16.908683);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.091994, 16.908489);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.092871, 16.908155);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.093778, 16.907852);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.094654, 16.907550);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.095630, 16.907219);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.096651, 16.906885);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.097579, 16.906559);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.097960, 16.906420);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.098443, 16.907523);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.098644, 16.907946);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.098913, 16.908321);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.099318, 16.908721);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.099785, 16.909209);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.099986, 16.909599);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.100155, 16.910207);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.100807, 16.909958);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.101652, 16.909730);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 8, -92.102931, 16.909379);


-- Coordenadas de la RUTA 9 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089396, 16.908569);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089165, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.088762, 16.907361);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089343, 16.907113);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089231, 16.906853);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089220, 16.906776);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089239, 16.906709);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089282, 16.906645);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.090199, 16.906200);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089952, 16.905773);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089544, 16.905267);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.087303, 16.903350);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086740, 16.902888);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086455, 16.902756);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086270, 16.902517);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086149, 16.902366);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086066, 16.902153);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086028, 16.901873);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086025, 16.901547);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086036, 16.901412);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086415, 16.897774);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086452, 16.897647);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086503, 16.897555);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086609, 16.897457);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086684, 16.897419);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.086756, 16.897388);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.088149, 16.897312);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089641, 16.897265);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089627, 16.897136);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.088538, 16.894919);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.088382, 16.894524);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 9, -92.089203, 16.894308);

-- Coordenadas de la RUTA 10 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.089358, 16.908581);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.089132, 16.908641);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088917, 16.908671);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088896, 16.908677);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088854, 16.908681);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088811, 16.908686);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088768, 16.908668);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088679, 16.908655);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088629, 16.908642);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088516, 16.908618);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088436, 16.908590);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088310, 16.908567);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.088128, 16.908531);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087750, 16.908449);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087624, 16.908426);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087873, 16.908464);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087316, 16.908341);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.087147, 16.908303);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.086761, 16.908208);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.086455, 16.908144);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.086185, 16.908077);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.085756, 16.907977);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.085112, 16.907823);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.084726, 16.907754);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.084538, 16.907716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.081738, 16.907106);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.080904, 16.906921);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.080896, 16.906818);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.080858, 16.906710);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.080826, 16.906651);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.079461, 16.905453);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.077999, 16.904213);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.076483, 16.902878);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.076471, 16.902865);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 10, -92.075728, 16.903565);


-- Coordenadas de la RUTA 11 (Lng - Lat)
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090258, 16.908437);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090000, 16.908550);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090247, 16.909125);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090301, 16.909248);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090623, 16.909853);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090633, 16.909935);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090741, 16.910059);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.090891, 16.910377);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.091085, 16.910716);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.091449, 16.911434);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.091900, 16.912112);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.092586, 16.911891);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.093338, 16.911630);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.094276, 16.911322);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.094775, 16.911090);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.094963, 16.911009);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.095177, 16.910921);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.095172, 16.910885);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096127, 16.910234);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096460, 16.910726);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096712, 16.911045);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096779, 16.911019);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096806, 16.910942);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.096860, 16.910890);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.097488, 16.910521);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.098035, 16.910228);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.099800, 16.909227);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.099606, 16.907580);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.102337, 16.906585);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.101645, 16.905465);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.103796, 16.904675);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.104670, 16.904490);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.105066, 16.904336);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.105324, 16.904212);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.106343, 16.903976);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.106569, 16.903915);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.106783, 16.903802);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.107942, 16.906409);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.109393, 16.905693);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.111914, 16.906309);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.112654, 16.906463);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.112912, 16.906422);
INSERT INTO puntrutas(rutas_id, longitud, latitud) VALUES ( 11, -92.113352, 16.906083);
