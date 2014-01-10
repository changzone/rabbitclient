import pika
import logging
import locale
import json
from datetime import datetime
import time
import random

from rabbitclient import RabbitClient

class RabbitPublisher(RabbitClient):
    '''
    Generic Publisher::standard usage is to
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
        freq = self._config['frequency']
        while True:
            message_body = self.action()
            self._logger.info("run_action::Publishing Message")
            self._channel.basic_publish(exchange=self._exchangeName, routing_key=str(random.randint), body=message_body)
            time.sleep(freq)


    def action(self):
        '''
        override this method with the action your publisher should take to generate messages for the queue.
        '''
        self._logger.info('*** running action ***')
        pass



if __name__ == '__main__':
    publisher = RabbitPublisher()
    publisher.run()

__author__ = 'Warren Chang :: https://github.com/changzone/rabbitclient'
