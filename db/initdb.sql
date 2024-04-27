CREATE DATABASE IF NOT EXISTS bambu;

USE bambu;

CREATE TABLE IF NOT EXISTS users (
	id	INTEGER (50) NOT NULL AUTO_INCREMENT,
	name	VARCHAR(40) NOT NULL,
	email	VARCHAR(40) NOT NULL,
	password VARCHAR(300) NOT NULL,
	PRIMARY KEY(id),
	UNIQUE(name),
	UNIQUE(email)
);

CREATE TABLE IF NOT EXISTS keys_tokens (
	id INTEGER (50) NOT NULL AUTO_INCREMENT,
	user_id	INTEGER,
	NCBI_API_KEY VARCHAR(200),
	X_ELS_APIKey VARCHAR(200),
	X_ELS_Insttoken	VARCHAR(200),
	GeminiAI VARCHAR(200),
	PRIMARY KEY(id),
	FOREIGN KEY(user_id) REFERENCES users(id),
);

CREATE TABLE IF NOT EXISTS results (
	id INTEGER(50) NOT NULL AUTO_INCREMENT,
	user_id	INTEGER,
	status VARCHAR(20),
	celery_id VARCHAR(100) NOT NULL,
	job_name VARCHAR(100),
	used_queries VARCHAR(4096),
	result_json json,
	created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(user_id) REFERENCES users(id),
	PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS flashtext_models (
	id INTEGER(50) NOT NULL AUTO_INCREMENT,
	user_id	INTEGER,
	name VARCHAR(64) NOT NULL,
	type VARCHAR(24),
	path VARCHAR(255),
	created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(user_id) REFERENCES users(id),
	PRIMARY KEY(id),
	UNIQUE(name),
	UNIQUE(path)
);
CREATE TABLE IF NOT EXISTS tokens_password (
	id INTEGER (50) NOT NULL AUTO_INCREMENT,
	user_id	INTEGER,
	token VARCHAR(64) NOT NULL,
	link VARCHAR(90) NOT NULL,
	created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	UNIQUE(token),
	PRIMARY KEY(id),
	FOREIGN KEY(user_id) REFERENCES users(id)
);


INSERT INTO users (id, name, email, password)
VALUES
	(1, 'admin', 'admin', '******');

INSERT INTO flashtext_models (id, user_id, name, type, path, created_date)
VALUES
	(1, 1, 'Human', 'GENE_OR_GENE_PRODUCT', 'data/flashtext_models/default_models/genes_human.pickle', CURRENT_TIMESTAMP),
	(2, 1, 'Danio rerio', 'GENE_OR_GENE_PRODUCT', 'data/flashtext_models/default_models/genes_danio_rerio.pickle', CURRENT_TIMESTAMP);
