
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


class Handler():
    def __init__(self):
        self.future = None

    def process_message(self, message):
        print(">>> Just logging messages message: {}".format(message))

        if self.future:
            # Resolve the read_message() future if we have one
            self.future.set_result(message)
            # And clear it once it's resolved
            self.future = None

    # Reads the next message from the stream
    async def read_message(self):
        loop = asyncio.get_running_loop()
        self.future = loop.create_future()
        return await self.future

    # Waits for a spesific message and ignores others
    async def wait_for(self, expected_message):
        while True:
            msg = await self.read_message()
            if msg == expected_message:
                return msg
            print(">>> unrelated message: {} but wanted: {}".format(msg, expected_message))

    async def main(self):
        print("Print first message")
        msg = await self.read_message()
        print("first_message {}".format(msg))

        print("Sleeping")
        await asyncio.sleep(2)

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


