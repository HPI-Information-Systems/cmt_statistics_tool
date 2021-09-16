CREATE TABLE submission_metareview (
	overall_rating TEXT NOT NULL, 
	summary TEXT NOT NULL, 
	revision_items TEXT NOT NULL, 
	submission_id INTEGER NOT NULL, 
	reviewer_id INTEGER NOT NULL, 
	PRIMARY KEY (submission_id, reviewer_id), 
	FOREIGN KEY(submission_id) REFERENCES submission (id), 
	FOREIGN KEY(reviewer_id) REFERENCES people (id)
)
