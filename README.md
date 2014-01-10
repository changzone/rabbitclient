rabbitclient
============

This is the common basic rabbitmq connection library to be used by anyone looking to create a publisher or consumer in python.
Usage
Publisher:
  Create your publishing class extending RabbitPublisher:
    ex.
    class MyPublisher(RabbitPublisher):

    # you only need to implement 2 methods
        def __init__(self, config=None):
            RabbitPublisher.__init__(self,config)

        def action(self):
            self._logger.info("DemoPublisher::publishing message")
            message = {'datetime':str(datetime.now())}
            return json.dumps(message)

    __init__ is to initialize, this should be standard.
    action is the method that actually does the work you want and its return should be a JSON string representation
           of the data you want to publish into the queue.


Consumer:
  Create your consumer class extending RabbitConsumer
  ex.
  class MyConsumer(RabbitConsumer):
    You only need to implement 1 methods


    def on_message(self, ch, method, properties, body):
        '''
        override this method with the action your publisher should take to consume messages for the queue.
        '''
        self._logger.info('*** running on_message ***')
        print " [x] Received %s" % (body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    in on_message, make sure to acknowledge the message after you process what you need to process.
