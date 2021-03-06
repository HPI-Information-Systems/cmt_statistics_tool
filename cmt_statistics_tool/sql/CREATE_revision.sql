CREATE TABLE revision (
	id SERIAL NOT NULL, 
	title TEXT NOT NULL, 
	abstract TEXT NOT NULL, 
	track_name TEXT NOT NULL, 
	primary_subject_area TEXT NOT NULL, 
	secondary_subject_areas TEXT NOT NULL, 
	conflicts INTEGER NOT NULL, 
	assigned INTEGER NOT NULL, 
	completed FLOAT NOT NULL, 
	bids INTEGER NOT NULL, 
	discussion VARCHAR(100) NOT NULL, 
	status VARCHAR(100) NOT NULL, 
	embargo_agreement TEXT NOT NULL, 
	conflict_agreement TEXT NOT NULL, 
	category TEXT NOT NULL, 
	authors_agreement TEXT NOT NULL, 
	availability TEXT NOT NULL, 
	submission_id INTEGER, 
	primary_author_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id), 
	FOREIGN KEY(submission_id) REFERENCES submission (id), 
	FOREIGN KEY(primary_author_id) REFERENCES people (id)
)
