export PGPASSWORD=dummy

start-db:
	docker-compose up -d --build db
	
start-listener:
	docker-compose up --build listener

start: start-db start-listener

run-updates:
	PGPASSWORD=dummy psql -h localhost -p 5432 -U dummy  -d ddb -f ./scripts/update.sql

run-inserts:
	PGPASSWORD=dummy psql -h localhost -p 5432 -U dummy  -d ddb -f ./scripts/insert.sql

test: setup-db run-inserts run-updates

stop:
	docker-compose down --remove-orphans