import boto3
from botocore.exceptions import ClientError
import os
import logging


class SQSClient:
    """ An abstraction over the AWS SQS api, allowing for simple consumption of SQS """

    def __init__(self, endpoint_url, region='us-east-1'):

        session = boto3.session.Session()
        self.sqs = session.client(
            'sqs',
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY', 'test'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_KEY', 'test'),
            aws_session_token=os.environ.get('AWS_SESSION_TOKEN', 'test')
        )

    def get_aprox_number_messages(self, queue_url):
        return self.sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages'])

    def get_queue_by_name(self, name):
        return self.sqs.get_queue_url(QueueName=name)['QueueUrl']

    def list_queues(self):
        response = self.sqs.list_queues()
        print response
        return response['QueueUrls']

    def create_queue(self, name):
        """ Create Queue in SQS, returning the QueueURL """
        response = self.sqs.create_queue(
            QueueName=name,
            Attributes={
                'DelaySeconds': '60',
                'MessageRetentionPeriod': '86400'
            }
        )
        print("QueueCreated -> %s" % response)
        queue_url = response['QueueUrl']
        return queue_url

    def delete_queue(self, queue_url):
        """ Delete the queue, given the following URL """
        response = self.sqs.delete_queue(QueueUrl=queue_url)
        print("Deleted Queue -> %s" % queue_url)
        return ("Queue at URL {0} deleted").format(queue_url)

    def send_message(self, queue_url, id, table, type):
        print "--------------------"
        print queue_url
        print "--------------------"
        print id
        print "--------------------"
        print table
        print "--------------------"
        print type
        print "--------------------"
        response = self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(id),
            MessageAttributes={
                'Table': {
                    'StringValue': table,
                    'DataType': 'String'
                },
                "Type": {
                    'StringValue': type,
                    'DataType': 'String'
                }
            }
        )
        msg_id = response['MessageId']
        print("Message ID -> %s" % msg_id)
        return "msg_id"

    def consume_next_message(self, queue_url):
        response = self.sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[""],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=4
        )
        message = response['Messages'][0]  # we only wnat the first message.
        print("Message -> %s" % message)
        return message

    def delete_message(self, queue_url, receipt_handle):
        """ delete Message from Queue given receipt_handle """
        try:
            self.sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                print("Queue does not exist, nothing to do")
            else:
                print("Unexpected error: %s" % e)
                raise

        return "deleted :  {0}".format(receipt_handle)
