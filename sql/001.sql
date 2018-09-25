
DROP TRIGGER IF EXISTS tr_request_update_notify ON films;

DROP TABLE IF EXISTS films;


CREATE TABLE films (
	  uid 		SERIAL PRIMARY KEY,
    title       varchar(125),
    kind        varchar(125)
);

CREATE OR REPLACE FUNCTION request_update_notify() RETURNS trigger as $$
BEGIN
  PERFORM pg_notify('film_events', json_build_object('table', TG_TABLE_NAME, 'id', NEW.uid, 'type', TG_OP)::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER tr_request_update_notify AFTER UPDATE or INSERT ON films FOR EACH ROW EXECUTE PROCEDURE request_update_notify();


