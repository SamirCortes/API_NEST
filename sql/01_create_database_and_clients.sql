-- Database and table creation script for API Nest
-- Database: api_nest
-- Table: clients

CREATE DATABASE IF NOT EXISTS `api_nest`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `api_nest`;

CREATE TABLE IF NOT EXISTS `clients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `names` varchar(100) NOT NULL,
  `surnames` varchar(100) NOT NULL,
  `age` int NULL,
  `created_at` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  `status` tinyint NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
