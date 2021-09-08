CREATE TABLE submission_seniormetareview (
	submission_id INTEGER NOT NULL, 
	reviewer_id INTEGER NOT NULL, 
	PRIMARY KEY (submission_id, reviewer_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (id), 
	FOREIGN KEY(reviewer_id) REFERENCES people (id)
)
