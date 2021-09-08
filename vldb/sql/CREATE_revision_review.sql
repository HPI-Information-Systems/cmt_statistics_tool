CREATE TABLE revision_review (
	recommendation TEXT NOT NULL, 
	revision_addressed TEXT NOT NULL, 
	justification TEXT NOT NULL, 
	comments_authors TEXT NOT NULL, 
	confidential_comments TEXT NOT NULL, 
	revision_id INTEGER NOT NULL, 
	reviewer_id INTEGER NOT NULL, 
	PRIMARY KEY (revision_id, reviewer_id), 
	FOREIGN KEY(revision_id) REFERENCES revision (id), 
	FOREIGN KEY(reviewer_id) REFERENCES people (id)
)
