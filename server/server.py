import time

import msgpack
import numpy as np
from loguru import logger
from msgpack import Unpacker
from numpy import typing as npt
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Factory, Protocol, connectionDone
from twisted.python import failure


def _sieve(target_n: int) -> npt.NDArray:
    assert 1 < target_n
    candidates = np.ones(shape=(target_n + 1,), dtype=bool)

    i = 2
    while i <= np.sqrt(target_n):
        if candidates[i]:
            j = np.square(i)
            while j <= target_n:
                candidates[j] = False
                j += i
        i += 1

    return candidates.nonzero()[0]


class ErastosthenesServer(Protocol):
    def __init__(self,
                 client: IAddress):
        super(ErastosthenesServer, self).__init__()
        self._caddr = client.host
        self._cport = client.port
        self._unpacker = Unpacker()
        logger.info(f'Started server process for client '
                    f'{self._caddr}:{self._cport}.')

    def connectionLost(self, reason: failure.Failure = connectionDone):
        logger.info(f'Shutting down server for client '
                    f'{self._caddr}:{self._cport}.')
        super(ErastosthenesServer, self).connectionLost(reason=reason)

    def dataReceived(self, data: bytes):
        self._unpacker.feed(data)
        for target_n in self._unpacker:
            logger.info(f'{self._caddr}:{self._cport}: '
                        f'Request for all primes between 2 and {target_n}...')
            init_proc = time.monotonic()
            primes = _sieve(target_n)
            end_proc = time.monotonic()
            proc_time = end_proc - init_proc

            logger.debug(f'{self._caddr}:{self._cport}: '
                         f'Answer: {primes}')
            logger.info(f'Processing time: {proc_time}s')
            logger.info(f'{self._caddr}:{self._cport}: '
                        f'Returning answer to client...')
            msgpack.pack(primes.tolist(), stream=self.transport)


class ErastosthenesFactory(Factory):
    def buildProtocol(self, addr: IAddress) -> ErastosthenesServer:
        return ErastosthenesServer(addr)


if __name__ == '__main__':
    # TODO: determine what to parameterize
    endpoint = TCP4ServerEndpoint(reactor, 5000)
    d = endpoint.listen(ErastosthenesFactory())
    d.addCallback(lambda e: logger.info('Started server at 0.0.0.0:5000.'))
    reactor.run()
