import pika
import logging
import locale
import json
from datetime import datetime
import time
from rabbitclient import RabbitClient

class RabbitConsumer(RabbitClient):
    '''
    Generic Consumer::standard usage is to
    1. override action() method
    2. override openCallback() method with queue declaration and
    2. call run() with parameter (frequency) which will pause and attempt to run the action() method every x seconds and
       push messages into the queue.
    '''



    def __init__(self, config=None):
        RabbitClient.__init__(self, config)

    def run(self):
        # lets get this rolling
        self.connect()
        try:
            self._connection.ioloop.start()
        except KeyboardInterrupt:
            self._logger.info("Keyboard Interrupt - closing loop")
            self._connection.close()
            self._connection.ioloop.start()


    def run_action(self):
        self._logger.info("run_action::Consuming Message")
        self._channel.basic_consume(self.on_message,queue=self._destinationQ)
        #self._channel.start_consuming()


    def on_message(self, ch, method, properties, body):
        '''
        override this method with the action your publisher should take to consume messages for the queue.
        '''
        self._logger.info('*** running on_message ***')
        print " [x] Received %s" % (body)
        ch.basic_ack(delivery_tag=method.delivery_tag)





if __name__ == '__main__':
    consumer = RabbitConsumer()
    consumer.run()

__author__ = 'Warren Chang :: https://github.com/changzone/rabbitclient'
