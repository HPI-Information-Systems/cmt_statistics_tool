CREATE TABLE people (
	id SERIAL NOT NULL, 
	name VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	affiliation VARCHAR NOT NULL, 
	country VARCHAR, 
	PRIMARY KEY (id), 
	UNIQUE (name, email)
)
