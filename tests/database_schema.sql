CREATE TABLE rings (
	ring_id INTEGER NOT NULL, 
	address VARCHAR NOT NULL, 
	PRIMARY KEY (ring_id), 
	UNIQUE (address)
)

CREATE TABLE syncs (
	sync_id INTEGER NOT NULL, 
	comment VARCHAR, 
	ring_id INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	PRIMARY KEY (sync_id), 
	FOREIGN KEY(ring_id) REFERENCES rings (ring_id)
)

CREATE TABLE heart_rates (
	heart_rate_id INTEGER NOT NULL, 
	reading INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	ring_id INTEGER NOT NULL, 
	sync_id INTEGER NOT NULL, 
	PRIMARY KEY (heart_rate_id), 
	UNIQUE (ring_id, timestamp), 
	FOREIGN KEY(ring_id) REFERENCES rings (ring_id), 
	FOREIGN KEY(sync_id) REFERENCES syncs (sync_id)
)

CREATE TABLE sport_details (
	sport_detail_id INTEGER NOT NULL, 
	calories INTEGER NOT NULL, 
	steps INTEGER NOT NULL, 
	distance INTEGER NOT NULL, 
	timestamp DATETIME NOT NULL, 
	ring_id INTEGER NOT NULL, 
	sync_id INTEGER NOT NULL, 
	PRIMARY KEY (sport_detail_id), 
	UNIQUE (ring_id, timestamp), 
	FOREIGN KEY(ring_id) REFERENCES rings (ring_id), 
	FOREIGN KEY(sync_id) REFERENCES syncs (sync_id)
)