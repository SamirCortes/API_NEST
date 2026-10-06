-- Tablas del taller 3: registro de pagos y su procesamiento asincrono
-- Database: api_nest

CREATE DATABASE IF NOT EXISTS `api_nest`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `api_nest`;

CREATE TABLE IF NOT EXISTS `pagos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `referencia` varchar(100) NOT NULL,
  `valor` decimal(12,2) NOT NULL,
  `medio_pago` varchar(50) NOT NULL,
  `fecha_registro` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `estado` varchar(20) NOT NULL DEFAULT 'REGISTRADO',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `procesamientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pago_id` int NOT NULL,
  `fecha_procesamiento` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `resultado` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_procesamientos_pago_id` (`pago_id`),
  CONSTRAINT `FK_procesamientos_pago` FOREIGN KEY (`pago_id`) REFERENCES `pagos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
