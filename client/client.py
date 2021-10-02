import os

from loguru import logger
from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol


class EchoProtocol(Protocol):
    def __init__(self):
        super(EchoProtocol, self).__init__()
        self._count = 0

    def send(self):
        self._count += 1
        message = f'Hello there! [{self._count}]'
        logger.info(f'Sending message: \"{message}\"')

        self.transport.write(message.encode('utf8'))

    def dataReceived(self, data: bytes):
        data_s = data.decode('utf-8')
        logger.info(f'Server echo: {data_s}')


def loop_send(proto: EchoProtocol) -> Deferred:
    lc = task.LoopingCall(proto.send)
    return lc.start(1.0)


if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

    endpoint = TCP4ClientEndpoint(reactor,
                                  os.environ['SERVER_ADDR'],
                                  int(os.environ['SERVER_PORT']))
    d = connectProtocol(endpoint, EchoProtocol())
    d.addCallback(loop_send)
    reactor.run()
