#!/usr/bin/python -u

import os
import boto3
import psycopg2
from psycopg2 import extras
from psycopg2 import extensions
from elasticsearch.helpers import parallel_bulk
from elasticsearch import Elasticsearch
from elasticsearch.connection.http_requests import RequestsHttpConnection


class Indexer(object):
    """
    Check the queue, get the id and table name
    from the SQS queue, select the data from
    postgres, serialize it, and upserts it
    to Elasticsearch
    """

    def __init__(self):
        sqs = boto3.resource(
            'sqs',
            region_name='us-east-1',
            endpoint_url=os.environ['SQS_ENDPOINT'],
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY', 'test'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY', 'test'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN', 'test'))
        self.queue = sqs.get_queue_by_name(QueueName=os.environ['QUEUE_NAME'])

        self.elasticsearch = Elasticsearch(
            hosts=[os.environ['ES_NODE_MASTER']],
            connection_class=RequestsHttpConnection
        )

    def run(self):
        while 1:
            # docs summary only contains the IDs
            docs_summary = self.get_messages()
            try:
                parallel_bulk(
                    client=self.elasticsearch,
                    actions=self.get_full_records_from_db(docs_summary=docs_summary),
                    chunk_size=os.environ['ES_CHUNK_SIZE']
                )
            except ValueError, ex:
                print "Nothing to upload"
                pass
            except Exception, ex:
                raise ex

    def get_full_records_from_db(self, docs_summary=None):

        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASS')
        dbname = os.getenv('POSTGRES_DBNAME')
        port = os.getenv('POSTGRES_PORT')
        host = os.getenv('POSTGRES_HOST')

        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=int(port))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        dir_curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if docs_summary is None:
            docs_summary = []

        for doc in docs_summary:
            dir_curs.execute("select * from {} where uid = {}".format(doc['table'], doc['id']))
            record = dir_curs.fetchone()
            print "Record to upsert found {} ".format(record)
            yield {
                '_op_type': 'index',
                '_index': os.environ['ES_INDEX_NAME'],
                '_type': os.environ['ES_DOCUMENT_NAME'],
                '_id': record['uid'],
                '_source': dict(record)
            }

    def get_messages(self):

        messages = self.queue.receive_messages(
            AttributeNames=["title", "type"],
            MaxNumberOfMessages=10,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=2,
            WaitTimeSeconds=2
        )
        docs_summary = []
        for message in messages:
            psql_table = message.message_attributes['Table']['StringValue']
            psql_op = message.message_attributes['Type']['StringValue']
            item_id = message.body
            docs_summary.append({"table": psql_table, "id": item_id, "op": psql_op})
            message.delete()

        return docs_summary


def main():
    i = Indexer()
    i.run()


if __name__ == '__main__':
    main()
