--CREATE LANGUAGE plpgsql;
CREATE SEQUENCE class_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE class_id OWNER TO "www-data";
CREATE TABLE class
(
  id integer NOT NULL DEFAULT nextval('class_id'::regclass),
  name character varying(45) NOT NULL ,
  CONSTRAINT class_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE class OWNER to "www-data";
INSERT INTO class (id, name) VALUES (1, 'Candidate Dinner');
INSERT INTO class (id, name) VALUES (2, 'Shadowing Interview');


CREATE SEQUENCE status_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE status_id OWNER TO "www-data";
CREATE TABLE status
(
  id integer NOT NULL DEFAULT nextval('status_id'::regclass),
  "name" character varying(45) NOT NULL,
  reportable boolean NOT NULL DEFAULT true,
  classid integer NOT NULL,
  isunavailable boolean NOT NULL DEFAULT false,
  CONSTRAINT status_pkey PRIMARY KEY (id),
  CONSTRAINT status_classid_fkey FOREIGN KEY (classid)
      REFERENCES "class" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE status OWNER TO "www-data";
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (1, 'Willing to Help', TRUE, 1, FALSE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (2, 'Can Help if Needed', TRUE, 1, FALSE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (3, 'Unavailable', FALSE, 1, TRUE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (4, 'Available AM', TRUE, 2, FALSE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (5, 'Available PM', TRUE, 2, FALSE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (6, 'Available All Day', TRUE, 2, FALSE);
INSERT INTO status (id, name, reportable, classid, isunavailable) VALUES (7, 'Unavailable', FALSE, 2, TRUE);



CREATE SEQUENCE users_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE users_id OWNER TO "www-data";
CREATE TABLE users
(
  id integer NOT NULL DEFAULT nextval('users_id'::regclass),
  tlgid character varying(10) NOT NULL,
  username character varying(20),
  firstname character varying(40),
  lastname character varying(40),
  email character varying(40),
  active boolean NOT NULL DEFAULT FALSE,
  isadmin boolean NOT NULL DEFAULT FALSE,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_username_key UNIQUE (username),
  CONSTRAINT users_tlgid_key UNIQUE (tlgid),
  CONSTRAINT users_check CHECK (((username IS NOT NULL) AND (username != '')) OR (active = false))
)
WITH (
  OIDS=FALSE
);
ALTER TABLE users OWNER TO "www-data";
CREATE INDEX username
  ON users
  USING btree
  (username);


CREATE SEQUENCE user_history_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE user_history_id OWNER TO "www-data";
CREATE TABLE user_history
(
  id integer NOT NULL DEFAULT nextval('user_history_id'::regclass),
  userid integer NOT NULL,
  username character varying(20),
  firstname character varying(40),
  lastname character varying(40),
  email character varying(40),
  active boolean NOT NULL DEFAULT FALSE,
  instantofupdate timestamp with time zone NOT NULL DEFAULT NOW(),
  CONSTRAINT user_history_pkey PRIMARY KEY (id),
  CONSTRAINT user_history_userid_fkey FOREIGN KEY (userid)
      REFERENCES users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE user_history OWNER TO "www-data";
  

  
CREATE SEQUENCE availability_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE availability_id OWNER TO "www-data";
CREATE TABLE availability
(
  id integer NOT NULL DEFAULT nextval('availability_id'::regclass),
  "day" date NOT NULL,
  status integer NOT NULL,
  assigned boolean NOT NULL DEFAULT FALSE,
  userid integer NOT NULL,
  classid integer NOT NULL,
  CONSTRAINT availability_pkey PRIMARY KEY (id),
  CONSTRAINT availability_status_fkey FOREIGN KEY (status)
      REFERENCES status (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT availability_userid_fkey FOREIGN KEY (userid)
      REFERENCES users (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT availability_classid_fkey FOREIGN KEY (classid)
    REFERENCES class (id) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT availability_day_key UNIQUE (day, userid, classid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE availability OWNER TO "www-data";
CREATE INDEX "user"
  ON availability
  USING btree
  (day, userid);


  

CREATE SEQUENCE hosts_id
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
ALTER TABLE hosts_id OWNER TO "www-data";
CREATE TABLE hosts
(
  id integer NOT NULL DEFAULT nextval('hosts_id'::regclass),
  "day" date NOT NULL,
  hosts integer NOT NULL DEFAULT 0,
  CONSTRAINT hosts_pkey PRIMARY KEY (id),
  CONSTRAINT hosts_day_key UNIQUE (day)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE hosts OWNER TO "www-data";


