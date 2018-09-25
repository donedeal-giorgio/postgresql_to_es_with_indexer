from sqs_client import SQSClient
import os


def main():
    print('Create Queue')
    queue_name = os.environ.get('QUEUE_NAME')
    sqs_url = os.environ.get('SQS_URL', 'http://localhost:4576')
    print sqs_url
    sqs = SQSClient(sqs_url)
    queue_url = sqs.create_queue(queue_name)
    print("{} created and available at {}".format(queue_name, queue_url))

if __name__ == '__main__':
    main()
