# postgresql_to_es_with_indexer

Sync Postgresql Inserts, Updates using a combination of psql events and indexer pattern


1. Start the DBs, queue and Elasticsearch(todo)
```bash
docker-compose up -d --build db queue elasticsearch
```

2. Setup the SQS queue
```bash
docker-compose up -d --build sqs-setup
```

3. Run the listener and indexer
```bash
docker-compose up --build listener indexer
```

4. Run some updates and udpates on the postgres db
```bash
make run-inserts
make run-updates
```

5. Check the records in ElasticSearch
```bash
curl localhost:9200/film/_search | jq .
```