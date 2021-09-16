CREATE TABLE submission_people (
	relation_type peoplepaperrelation NOT NULL, 
	submission_id INTEGER NOT NULL, 
	people_id INTEGER NOT NULL, 
	position INTEGER NOT NULL, 
	PRIMARY KEY (relation_type, submission_id, people_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (id), 
	FOREIGN KEY(people_id) REFERENCES people (id)
)
