create table if not exists "t_rawfits" (
	"id"	TEXT,
	"obs_time"	NUMERIC,
	"ccd_num"	NUMERIC,
	"type"	TEXT,
	"path"	TEXT,
	PRIMARY KEY("id")
);
