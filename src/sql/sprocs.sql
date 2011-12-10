DROP FUNCTION IF EXISTS getavailable(date, date);
DROP FUNCTION IF EXISTS getavailability(integer, date, date);
DROP FUNCTION IF EXISTS updateavailability(integer, date, integer);
DROP FUNCTION IF EXISTS assignhost(integer, date);
DROP FUNCTION IF EXISTS gethosts(date, date);
DROP FUNCTION IF EXISTS getreportable();
DROP FUNCTION IF EXISTS getselectable();
DROP FUNCTION IF EXISTS updatehosts(date, integer);
DROP FUNCTION IF EXISTS updateuser(character varying, character varying, character varying, character varying, character varying, boolean);
DROP FUNCTION IF EXISTS auditchange(integer, character varying, character varying, character varying, character varying, boolean);
DROP FUNCTION IF EXISTS getuser(character varying);
DROP FUNCTION IF EXISTS getchangedusers(date, date);
DROP TYPE IF EXISTS usertype;
CREATE TYPE usertype as (
  id integer,
  tlgid character varying,
  username character varying,
  firstname character varying,
  lastname character varying,
  email character varying,
  isadmin boolean
);
ALTER TYPE usertype OWNER to "www-data";
DROP TYPE IF EXISTS availableuser;
CREATE TYPE availableuser as (
  id integer,
  tlgid character varying,
  username character varying,
  firstname character varying,
  lastname character varying,
  email character varying,
  isadmin boolean,
  day date, 
  status integer, 
  assigned boolean
);
ALTER TYPE availableuser OWNER to "www-data";
DROP TYPE IF EXISTS statustype;
CREATE TYPE statustype as (
  id integer,
  name character varying,
  reportable boolean
);
ALTER TYPE statustype OWNER TO "www-data";
DROP TYPE IF EXISTS hosttype;
CREATE TYPE hosttype as (
  id integer,
  "day" date,
  hosts integer
);
ALTER TYPE hosttype OWNER TO "www-data";
DROP TYPE IF EXISTS availabletype;
CREATE TYPE availabletype as (
  id integer,
  "day" date,
  status integer,
  assigned boolean,
  userid integer
);
ALTER TYPE availabletype OWNER TO "www-data";
DROP TYPE IF EXISTS usersnapshot;
CREATE TYPE usersnapshot as (
  tlgid character varying,
  username character varying,
  firstname character varying,
  lastname character varying,
  email character varying,
  active boolean,
  old_username character varying,
  old_firstname character varying,
  old_lastname character varying,
  old_email character varying,
  old_active character varying,
  instantofupdate timestamp with time zone
);


--assigns hosts to a given day
CREATE OR REPLACE FUNCTION assignhost(p_userid integer, p_date date)
  RETURNS boolean AS
$BODY$
DECLARE
    v_cnt integer;
BEGIN
    SELECT COUNT(id) INTO v_cnt FROM users WHERE id = p_userid;
    IF v_cnt = 0 THEN
        RETURN FALSE;
    END IF;
    SELECT COUNT(id) INTO v_cnt FROM availability WHERE ((userid = p_userid) AND (day = p_date));
    IF v_cnt = 0 THEN
        INSERT INTO availability (userid, day, assigned) VALUES (p_userid, p_date, TRUE);
    ELSE
        UPDATE availability SET assigned = TRUE WHERE ((userid = p_userid) AND (day = p_date));
    END IF;
    RETURN TRUE;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION assignhost(integer, date) OWNER TO "www-data";



--gets how available a user is for a given date range
CREATE OR REPLACE FUNCTION getavailability(p_userid integer, p_first date, p_next date)
    RETURNS SETOF availabletype AS
$BODY$
DECLARE
    v_rec availabletype%rowtype;
BEGIN
    FOR v_rec IN  SELECT id, day, status, assigned, userid FROM availability WHERE userid = p_userid AND day >= p_first AND day < p_next LOOP
        RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
    LANGUAGE 'plpgsql' VOLATILE
    COST 100
    ROWS 1000;
ALTER FUNCTION getavailability(integer, date, date) OWNER TO "www-data";


--returns all of the users available during a given window
CREATE OR REPLACE FUNCTION getavailable(p_first date, p_next date)
  RETURNS SETOF availableuser AS
$BODY$
DECLARE
    v_rec availableuser%rowtype;
BEGIN
    FOR v_rec IN 
    SELECT
        users.id, 
        users.tlgid,
        users.username, 
        users.firstname, 
        users.lastname, 
        users.email, 
        users.isadmin,
        availability.day, 
        availability.status, 
        availability.assigned 
    FROM 
        availability, users 
    WHERE 
        ((users.id = availability.userid)
        AND (day >= p_first AND day < p_next) 
        AND (status != '3' OR assigned = TRUE))
    ORDER BY users.firstname
    LOOP
    RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION getavailable(date, date) OWNER TO "www-data";



-- returns the number of hosts required for each day during a given date range
CREATE OR REPLACE FUNCTION gethosts(p_first date, p_next date)
  RETURNS SETOF hosttype AS
$BODY$
DECLARE
    v_rec hosttype%rowtype;
BEGIN

    FOR v_rec IN SELECT id, day, hosts FROM hosts WHERE (day >= p_first AND day < p_next) LOOP
        RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION gethosts(date, date) OWNER TO "www-data";



-- returns which statuses are reportable
CREATE OR REPLACE FUNCTION getreportable()
  RETURNS SETOF statustype AS
$BODY$
DECLARE
    v_rec statustype%rowtype;
BEGIN
    FOR v_rec IN SELECT id, name, reportable FROM status WHERE reportable = TRUE LOOP
        RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION getreportable() OWNER TO "www-data";


-- returns which statuses are selectable
CREATE OR REPLACE FUNCTION getselectable()
  RETURNS SETOF statustype AS
$BODY$
DECLARE
    v_rec statustype%rowtype;
BEGIN
    FOR v_rec IN SELECT id, name, reportable FROM status LOOP
        RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION getselectable() OWNER TO "www-data";


-- updates how available (or not) a particular user is for a particular day
CREATE OR REPLACE FUNCTION updateavailability(p_userid integer, p_date date, p_status integer)
  RETURNS boolean AS
$BODY$
DECLARE
    v_cnt integer;
BEGIN
    SELECT COUNT(id) INTO v_cnt FROM users WHERE id = p_userid;
    IF v_cnt = 0 THEN
        RETURN FALSE;
    END IF;
    SELECT COUNT(id) INTO v_cnt FROM availability WHERE ((userid = p_userid) AND (day = p_date));
    IF v_cnt = 0 THEN
        INSERT INTO availability (userid, day, status) VALUES (p_userid, p_date, p_status);
    ELSE
        UPDATE availability SET status = p_status WHERE ((userid = p_userid) AND (day = p_date));
    END IF;
    RETURN TRUE;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION updateavailability(integer, date, integer) OWNER TO "www-data";


-- updates the number of hosts required for a particular day
CREATE OR REPLACE FUNCTION updatehosts(p_date date, p_hosts integer)
  RETURNS boolean AS
$BODY$
DECLARE
    v_cnt integer;
BEGIN
    SELECT COUNT(id) INTO v_cnt FROM hosts WHERE day = p_date;
    IF v_cnt = 0 THEN
        INSERT INTO hosts (day, hosts) VALUES (p_date, p_hosts);
    ELSE
        UPDATE hosts SET hosts = p_hosts WHERE day = p_date;
    END IF;
    RETURN TRUE;
END;
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION updatehosts(date, integer) OWNER TO "www-data";


-- updates a user (used for shadowing from track shadow)
CREATE OR REPLACE FUNCTION updateuser(p_tlgid character varying, p_username character varying, p_firstname character varying, p_lastname character varying, p_email character varying, p_isactive boolean)
  RETURNS boolean AS
$BODY$
DECLARE
    v_username character varying;
    v_firstname character varying;
    v_lastname character varying;
    v_email character varying;
    v_isactive boolean;
    
    v_cnt integer;
    v_id integer;
    v_oldusername character varying;
    v_oldfirstname character varying;
    v_oldlastname character varying;
    v_oldemail character varying;
    v_oldactive boolean;
BEGIN
    --sanity check variables
    IF ((p_tlgid = '') OR (p_tlgid IS NULL)) THEN
        RETURN FALSE;
    END IF;
    v_username := NULL;
    IF ((p_isactive = TRUE) AND (p_username != '')) THEN
        v_username := LOWER(p_username);
    END IF;
    v_isactive := p_isactive;
    IF v_username IS NULL THEN
        v_isactive := FALSE;
    END IF;
    v_firstname := NULL;
    IF p_firstname != '' THEN
        v_firstname = p_firstname;
    END IF;
    v_lastname := NULL;
    IF p_lastname != '' THEN
        v_lastname = p_lastname;
    END IF;
    v_email := NULL;
    IF p_email != '' THEN
        v_email = p_email;
    END IF;
    
    SELECT COUNT(id) INTO v_cnt FROM users WHERE tlgid = p_tlgid;
    IF v_cnt = 0 THEN  --user doesn't exist
        IF v_isactive THEN  --only add active users - if doesn't have a username then must be inactive
            INSERT INTO users (tlgid, username, firstname, lastname, email, active) VALUES (p_tlgid, v_username, v_firstname, v_lastname, v_email, v_isactive);
        END IF;
    ELSE  --user already exists
        SELECT id, username, firstname, lastname, email, active INTO v_id, v_oldusername, v_oldfirstname, v_oldlastname, v_oldemail, v_oldactive FROM users WHERE tlgid = p_tlgid;
        IF (
                (v_oldusername != v_username) OR (v_oldusername IS NULL AND v_username IS NOT NULL) OR (v_oldusername IS NOT NULL AND v_username IS NULL) OR
                (v_oldactive != v_isactive) OR
                (v_oldfirstname != v_firstname) OR (v_oldfirstname IS NULL AND v_firstname IS NOT NULL) OR (v_oldfirstname IS NOT NULL AND v_firstname IS NULL) OR
                (v_oldlastname != v_lastname) OR (v_oldlastname IS NULL AND v_lastname IS NOT NULL) OR (v_oldlastname IS NOT NULL AND v_lastname IS NULL) OR
                (v_oldemail != v_email) OR (v_oldemail IS NULL AND v_email IS NOT NULL) OR (v_oldemail IS NOT NULL AND v_email IS NULL)
           ) THEN
            PERFORM auditchange(v_id, v_oldusername, v_oldfirstname, v_oldlastname, v_oldemail, v_oldactive);
            UPDATE users SET username = v_username, firstname = v_firstname, lastname = v_lastname, email = v_email, active = v_isactive WHERE tlgid = p_tlgid;
        END IF;
    END IF;
    RETURN TRUE;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
ALTER FUNCTION updateuser(character varying, character varying, character varying, character varying, character varying, boolean) OWNER TO "www-data";


-- audits a change to a user
CREATE OR REPLACE FUNCTION auditchange(p_userid integer, p_username character varying, p_firstname character varying, p_lastname character varying, p_email character varying, p_isactive boolean)
  RETURNS boolean AS
$BODY$
DECLARE
BEGIN
    INSERT INTO user_history(userid, username, firstname, lastname, email, active) VALUES (p_userid, p_username, p_firstname, p_lastname, p_email, p_isactive);
    RETURN TRUE;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
ALTER FUNCTION auditchange(integer, character varying, character varying, character varying, character varying, boolean) OWNER TO "www-data";



-- gets information about a particular user
CREATE OR REPLACE FUNCTION getuser(p_username character varying) 
  RETURNS SETOF usertype AS
$BODY$
DECLARE
    v_cnt integer;
    v_rec usertype%rowtype;
BEGIN
    SELECT COUNT(id) INTO v_cnt FROM users WHERE ((username = LOWER(p_username)) AND (active = 'TRUE'));
    IF v_cnt = 1 THEN
        FOR v_rec IN SELECT id, tlgid, username, firstname, lastname, email, isadmin FROM users WHERE ((username = LOWER(p_username)) AND (active = 'TRUE')) LOOP
            RETURN NEXT v_rec;
        END LOOP;
    END IF;
    RETURN;
END;
$BODY$
    LANGUAGE 'plpgsql' VOLATILE
    COST 100
    ROWS 1000;
ALTER FUNCTION getuser(character varying) OWNER TO "www-data";

--gets the users changed since the last date
CREATE OR REPLACE FUNCTION getchangedusers(p_begin date, p_end date)
  RETURNS SETOF usersnapshot AS
$BODY$
DECLARE
    v_rec usersnapshot%rowtype;
    v_begin date;
    v_end date;
BEGIN
    v_begin := p_begin;
    IF (p_begin IS NULL) THEN
        v_begin := '01/01/2000';
    END IF;
    v_end := p_end;
    IF (p_end IS NULL) THEN
        v_end := '12/31/2200';
    END IF;
    FOR v_rec IN
        SELECT 
            users.tlgid, users.username, users.firstname, users.lastname, users.email, users.active, 
            user_history.username, user_history.firstname, user_history.lastname, user_history.email, 
            user_history.active, user_history.instantofupdate 
        FROM 
            users, user_history 
        WHERE 
            user_history.userid=users.id AND 
            user_history.instantofupdate > v_begin AND
            user_history.instantofupdate < v_end
        ORDER BY 
            users.id
    LOOP
        RETURN NEXT v_rec;
    END LOOP;
    RETURN;
END;
$BODY$
    LANGUAGE 'plpgsql' VOLATILE
    COST 100
    ROWS 1000;
ALTER FUNCTION getchangedusers(date, date) OWNER TO "www-data";




