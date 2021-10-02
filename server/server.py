from loguru import logger
from twisted.internet.protocol import Protocol


class EchoServer(Protocol):
    def dataReceived(self, data: bytes):
        data_s = data.decode('utf-8')
        logger.info(f'Echoing back data: {data_s}')
        self.transport.write(data)


if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.internet.endpoints import TCP4ServerEndpoint
    from twisted.internet.protocol import Factory

    # TODO: determine what to parameterize
    endpoint = TCP4ServerEndpoint(reactor, 5000)
    endpoint.listen(Factory.forProtocol(EchoServer))
    reactor.run()
