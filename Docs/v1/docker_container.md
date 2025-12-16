# Docker Container

## PostgreSQL

```bash
docker run --name promptvault-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=promptvault -p 5432:5432 -d postgres
```

This will make postgres running at :
host: localhost
port: 5432
user: postgres
password: postgres
database: promptvault

To stop the container, run:
docker stop promptvault-db


Test Connection : 
psql -h localhost -U postgres -d promptvault