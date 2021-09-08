CREATE TABLE revision_people (
	relation_type peoplepaperrelation NOT NULL, 
	revision_id INTEGER NOT NULL, 
	people_id INTEGER NOT NULL, 
	position INTEGER NOT NULL, 
	PRIMARY KEY (relation_type, revision_id, people_id), 
	FOREIGN KEY(revision_id) REFERENCES revision (id), 
	FOREIGN KEY(people_id) REFERENCES people (id)
)
