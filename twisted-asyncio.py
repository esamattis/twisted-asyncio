
import asyncio

from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

from twisted.internet import task
from twisted.internet import reactor, asyncioreactor
from twisted.internet.task import react
from twisted.internet.defer import Deferred
from twisted.internet.defer import ensureDeferred
import random


# Simulates binance socket manager.
class RandomMessageSocket():

    # Start calling callback with random messages
    def start_random_message_socket(self, callback):
        self.send_random_message(callback)

    def send_random_message(self, callback):
        messages = list(range(1, 20)) # number from 1-20
        random.shuffle(messages)
        random_message = messages[0]

        callback(random_message)

        # Recursively loop random message sending
        reactor.callLater(0.1, self.send_random_message, callback)


class MessageExpectation():

    def __init__(self, expected_message):
        self.expected_message = expected_message
        loop = asyncio.get_running_loop()
        self.future = loop.create_future()


    def try_fulfill(self, message):
        if self.future.done():
            # already received this message
            return

        if self.expected_message != message:
            # Some other message, not interested
            return

        self.future.set_result(message)

    # Wait until this expectation is fulfilled
    async def wait(self):
        await self.future


class Handler():
    def __init__(self):
        self.expectations = []

    def process_message(self, message):
        print(">>> Just logging messages message: {}".format(message))

        for expectation in self.expectations:
            expectation.try_fulfill(message)


    async def wait_for(self, expected_message):
        # Create expectation that can be fulfilled by the twisted process_message callback
        expectation = MessageExpectation(expected_message)
        self.expectations.append(expectation)
        return await expectation.wait()


    async def main(self):
        print("Sleeping")
        await asyncio.sleep(5)


        print("Waiting for 4")
        await self.wait_for(4)
        print("Got 4!")

        print("Waiting for 3")
        await self.wait_for(3)
        print("Got 3!")

        print("all done!")


@task.react
def twisted_main(reactor):
    handler = Handler()

    rm = RandomMessageSocket()
    rm.start_random_message_socket(handler.process_message)

    # Call the python asyncio future using the twisted reactor
    return Deferred.fromFuture(asyncio.ensure_future(handler.main()))


reactor.run()


