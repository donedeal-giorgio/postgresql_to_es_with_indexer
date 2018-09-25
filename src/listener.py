import select
import psycopg2
import psycopg2.extensions
import os
from sqs_client import SQSClient

user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASS')
dbname = os.getenv('POSTGRES_DBNAME')
port = os.getenv('POSTGRES_PORT')
host = os.getenv('POSTGRES_HOST')
stream = os.getenv('SUBSCRIBE_NOTIFICATION')


# def send_message(table, uid):


class Listener(object):

    def __init__(self):
        self.queue_name = os.environ['QUEUE_NAME']
        self.sqs_client = SQSClient(os.environ['SQS_ENDPOINT'])
        self.queue_url = self.sqs_client.get_queue_by_name(name=self.queue_name)

    def notify(self, table, id, type):
        print "Sending message for {} and id {} to queue {}".format(table, id, self.queue_url)
        self.sqs_client.send_message(table=table, id=id, queue_url=self.queue_url, type=type)

    def run(self):
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=int(port))
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        curs = conn.cursor()
        curs.execute("LISTEN {};".format(stream))

        print("Waiting for notifications on channel {}".format(stream))

        while 1:
            if select.select([conn], [], [], 5) == ([], [], []):
                print "Timeout"
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print "Got NOTIFY:{} {} {}".format(notify.pid, notify.channel, notify.payload)
                    db_event = eval(notify.payload)
                    self.notify(table=db_event['table'], id=db_event['id'], type=db_event['type'])


def main():
    listener = Listener()
    listener.run()


if __name__ == '__main__':
    main()
