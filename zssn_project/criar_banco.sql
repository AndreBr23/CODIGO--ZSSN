-- Script para criar o banco de dados PostgreSQL
-- Execute este comando no PostgreSQL como superusuário

CREATE DATABASE zssn_db;
CREATE USER survival WITH PASSWORD '123456789';
GRANT ALL PRIVILEGES ON DATABASE zssn_db TO survival;

-- Conecte-se ao banco apocalipse_zumbi_db e execute:
GRANT ALL ON SCHEMA public TO survival;
