-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         10.4.24-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.0.0.6468
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Volcando estructura para tabla comidasbd.password_resets
CREATE TABLE IF NOT EXISTS `password_resets` (
  `email` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  KEY `password_resets_email_index` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Volcando datos para la tabla comidasbd.password_resets: ~0 rows (aproximadamente)

-- Volcando estructura para tabla comidasbd.platillo
CREATE TABLE IF NOT EXISTS `platillo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_restaurant` int(11) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `categoria` varchar(255) NOT NULL,
  `status` enum('DISPONIBLE','NO DISPONIBLE') NOT NULL DEFAULT 'DISPONIBLE',
  PRIMARY KEY (`id`),
  KEY `id_restaurant` (`id_restaurant`),
  CONSTRAINT `platillo_ibfk_1` FOREIGN KEY (`id_restaurant`) REFERENCES `restaurant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Volcando datos para la tabla comidasbd.platillo: ~0 rows (aproximadamente)

-- Volcando estructura para tabla comidasbd.restaurant
CREATE TABLE IF NOT EXISTS `restaurant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `razon_social` varchar(255) NOT NULL,
  `nombre_contacto` varchar(255) NOT NULL,
  `clabe` varchar(255) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `telefono` char(10) NOT NULL,
  `email` varchar(255) NOT NULL,
  `facebook` varchar(255) NOT NULL,
  `twitter` varchar(255) NOT NULL,
  `instagram` varchar(255) NOT NULL,
  `logotipo` varchar(255) NOT NULL,
  `status` enum('ABIERTO','CERRADO') NOT NULL DEFAULT 'CERRADO',
  `ubicacion_lat` varchar(255) NOT NULL,
  `ubicacion_long` varchar(255) NOT NULL,
  `verificado` enum('SOLICITUD','APROBADO','RECHAZADO') NOT NULL DEFAULT 'SOLICITUD',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `email` (`email`),
  CONSTRAINT `restaurant_ibfk_1` FOREIGN KEY (`email`) REFERENCES `users` (`email`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

-- Volcando datos para la tabla comidasbd.restaurant: ~6 rows (aproximadamente)
INSERT INTO `restaurant` (`id`, `razon_social`, `nombre_contacto`, `clabe`, `direccion`, `telefono`, `email`, `facebook`, `twitter`, `instagram`, `logotipo`, `status`, `ubicacion_lat`, `ubicacion_long`, `verificado`, `created_at`, `updated_at`, `deleted_at`) VALUES
	(1, 'Comidas Toñitas', 'Mario', '9876543', 'Sexta Poniente Norte', '9897651432', 'ramon.bonachea@email.com', 'Toñita', 'Ninguno', 'Ninguno', 'no', 'CERRADO', '17.171047038617488', '92.33461453753803', 'APROBADO', '2022-09-11 22:59:02', '2022-09-11 22:59:06', '2022-09-11 22:59:08'),
	(2, 'Comidas Mack', 'Carlos', '12384759', 'Septima Poniente Norte', '9568474589', 'r.bonachea@email.com', 'Mack', 'Ninguno', 'Ninguno', 'no', 'CERRADO', '17.171047038617489', '92.33461453753804', 'APROBADO', '2022-09-11 23:08:02', '2022-09-11 23:04:26', '2022-09-11 23:04:27'),
	(3, 'Fonda Marinos', 'Henry ', '1487524', 'Cuarta Poniente Sur', '5847589412', 'r.bonachea21@email.com', 'Marinos', 'Ninguno', 'Ninguno', 'no', 'CERRADO', '17.171047038617488', '92.33461453753803', 'APROBADO', '2022-09-11 23:12:02', '2022-09-11 23:10:43', '2022-09-11 23:10:44'),
	(4, 'Fonda Florinda', 'Florinda', '1457256', 'Sexta Oriente Sur', '5784674516', 'r.fondaflorinda21@email.com', 'Flori', 'Ninguno', 'Ninguno', 'No', 'CERRADO', '17.171047038617488', '92.33461453753801', 'RECHAZADO', '2022-09-11 23:26:00', '2022-09-11 23:25:17', '2022-09-11 23:25:19'),
	(5, 'El Buen Gusto', 'Cornelio', '1452687', 'Sexta Oriente Norte', '4757157594', 'r.fonda444421@email.com', 'Buen Gusto', 'Ninguno', 'Ninguno', 'no', 'CERRADO', '17.171047038617488', '92.33461453753801', 'SOLICITUD', '2022-09-11 23:29:14', '2022-09-11 23:29:15', '2022-09-11 23:29:16'),
	(6, 'Palapa del Gato ', 'Pablo ', '7547854', 'Quinta Oriente Sur', '4813297548', 'r.restauran321@email.com', 'Palapa', 'Ninguno', 'Ninguno', 'no', 'CERRADO', '17.171047038617488', '92.33461453753801', 'RECHAZADO', '2022-09-11 23:30:56', '2022-09-11 23:30:57', '2022-09-11 23:30:57');

-- Volcando estructura para tabla comidasbd.users
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `remember_token` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_unique` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4;

-- Volcando datos para la tabla comidasbd.users: ~6 rows (aproximadamente)
INSERT INTO `users` (`id`, `email`, `password`, `remember_token`, `created_at`, `updated_at`) VALUES
	(1, 'ramon.bonachea@email.com', '123456', NULL, '2022-09-12 04:16:06', '2022-09-12 04:16:06'),
	(2, 'r.bonachea@email.com', '123454', NULL, '2022-09-12 04:16:11', '2022-09-12 04:16:12'),
	(3, 'r.bonachea21@email.com', '1234542', NULL, '2022-09-12 04:16:17', '2022-09-12 04:16:17'),
	(4, 'r.fonda444421@email.com', '123451', NULL, '2022-09-12 04:16:20', '2022-09-12 04:16:20'),
	(5, 'r.restauran321@email.com', '123458', NULL, '2022-09-12 04:16:11', '2022-09-12 04:16:12'),
	(6, 'r.fondaflorinda21@email.com', '145789', NULL, '2022-09-12 04:17:56', '2022-09-12 04:17:56');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
