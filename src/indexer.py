#!/usr/bin/python -u

import os, time, sys
import boto3


# sys.stdout = unbuffered

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

    def run(self):
        # if the number of messages from the db is less than 100, wait
        # until we have enough messages to send to ES.
        # But if 5 seconds are elapsed since the last message, then send
        # to ES whatever we have.
        while 1:
            docs_summary = self.get_messages()
            self.get_full_records_from_db(docs_summary=docs_summary)

    def get_full_records_from_db(self, docs_summary=None):

        if docs_summary is None:
            docs_summary = []

        for doc in docs_summary:
            print "select * from {} where uid = {}".format(doc['table'], doc['id'])

    def get_messages(self):

            # time.sleep(2)
            messages = self.queue.receive_messages(
                AttributeNames=["title", "type"],
                MaxNumberOfMessages=10,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=2
            )
            docs_summary = []
            for message in messages:
                psql_table = message.message_attributes['Table']['StringValue']
                psql_op = message.message_attributes['Type']['StringValue']
                item_id = message.body
                # print "table: {}".format(psql_table)
                # print "original op {}".format(psql_op)
                # print "primary key {}".format(item_id)
                docs_summary.append({"table": psql_table, "id": item_id, "op": psql_op})
                message.delete()

            return docs_summary


def main():
    print "ok"
    i = Indexer()
    print "done"
    i.run()


if __name__ == '__main__':
    main()
