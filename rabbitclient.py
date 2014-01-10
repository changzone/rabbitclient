import pika
import logging
import locale
import json

class RabbitClient(object):
    '''
    RabbitClient is the base level class that handles rabbit exceptions, connections and logging.  Subsequent
    consumer/publishers will sublcass RabbitClient and implement the necessary functions.
    '''
    _LOG_FORMAT = ('%(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(levelname) -10s %(message)s')
    _logger=None
    _config=None
    _connection=None

    _destinationQ='testq'
    _exchange=None
    _channel=None
    _routingkey=''
    _exchangeName=''
    _exchangeType=''

    def __init__(self, configfile=None):
        if (configfile == None):
            configfile = './defaultConfig.json'

        locale.setlocale(locale.LC_ALL, 'en_US')
        logger = logging.getLogger(self.__class__.__name__)

        #load config file
        try:
            with open(configfile) as conffile:
                self._config = json.load(conffile)
        except IOError as e:
            raise IOError("Error::" + str(self.__class__.__name__) + " unable to load config file: " + file + " with error : " + str(e.message))

        self._destinationQ=self._config['queue']
        self._exchangeName=self._config['exchange_name']
        self._exchangeType=self._config['exchange_type']
        self._routingkey = self._config['routing_key']

        # setup logger
        logfile = logging.FileHandler(self._config.get('logfile'))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logfile.setFormatter(formatter)
        logger.addHandler(logfile)
        logger.setLevel(self._config['loglevel'])
        self._logger = logger
        self._logger.info(str(self.__class__.__name__) + " Class initialized with configuration : ")
        self._logger.info(str(self._config))

        # we'll do connection instantiation somewhere else.

    def connect(self, onOpenCallback=None, onCloseCallback=None, closeIOLoopOnDisconnect=True):
        '''
        The assumption that each client has but one connection
        '''
        if (onOpenCallback == None):
            onOpenCallback = self._defaultOpenCallback
        if (onCloseCallback == None):
            onCloseCallback = self._defaultCloseCallback

        self._logger.info("Connecting to %s", self._config['broker_url'])

        self._connection=pika.SelectConnection(pika.URLParameters(str(self._config['broker_url'])),on_open_callback=onOpenCallback,
                                     on_open_error_callback=self._connectionErrorHandler,
                                     on_close_callback=onCloseCallback, stop_ioloop_on_close=closeIOLoopOnDisconnect)
    def close(self):
        self._logger.info("Closing connection %s", self._config['q_host'])
        self._connection.close()

    def _defaultOpenCallback(self, connection):
        self._logger.info("RabbitPublisher::Connection Opened")
        self._channel = self._connection.channel(on_open_callback=self.on_open_channel_callback)

    def on_open_channel_callback(self, channel):
        self._logger.info("RabbitPublisher::Channel Opened!")
        #declare exchange
        self._channel.exchange_declare(callback=self.on_exchange_declareok, exchange=self._exchangeName, exchange_type=self._exchangeType, durable=True)


    def on_exchange_declareok(self,frame):
        self._logger.info("Exchange %s Declared",self._exchangeName)
        self._channel.queue_declare(self.on_queue_declareok, self._destinationQ, durable=True)

    def on_queue_declareok(self, frame):
        self._logger.info("Queue %s declared",self._destinationQ)
        self._channel.queue_bind(self.on_bindok, self._destinationQ, self._exchangeName, self._routingkey)

    def on_bindok(self, bind):
        self._logger.info("Queue %s is bound on %s.", self._destinationQ, self._exchangeName)
        self.run_action()

    def _defaultCloseCallback(self):
        self._logger.info("Connection Closed!")

    def _connectionErrorHandler(self, error):
        self._logger.error("Error with Connection! " + str(error))

if __name__ == '__main__':
    client = RabbitClient()
    client.connect()



__author__ = 'Warren Chang :: https://github.com/changzone/rabbitclient'
