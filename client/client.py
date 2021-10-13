import os
import time
from collections import deque
from pathlib import Path

import msgpack
import numpy as np
import pandas as pd
from loguru import logger
from msgpack import Unpacker
from twisted.application.internet import ClientService
from twisted.internet import reactor
from twisted.internet.endpoints import clientFromString
from twisted.internet.interfaces import IAddress
from twisted.internet.posixbase import PosixReactorBase
from twisted.internet.protocol import Factory, Protocol, connectionDone
from twisted.python import failure

reactor: PosixReactorBase = reactor


class ErastosthenesClient(Protocol):
    _results_path = Path('./benchmark.client.csv')

    def __init__(self, server_addr: str, server_port: int, target_n: int):
        super(ErastosthenesClient, self).__init__()
        logger.info(f'Client connected to {server_addr}:{server_port}, '
                    f'target N = {target_n}.')
        self._saddr = server_addr
        self._sport = server_port
        self._target_n = target_n
        self._unpacker = Unpacker(use_list=False)
        self._latest_send = -1

        self._benchmark_results = deque()

    def connectionMade(self):
        reactor.callLater(callable=self.send, delay=0)

    def connectionLost(self, reason: failure.Failure = connectionDone):
        logger.info(f'Closing connection to {self._saddr}:{self._sport}...')
        logger.info(f'Saving benchmark results to {self._results_path}.')

        df = pd.DataFrame(data=self._benchmark_results)
        df.to_csv(self._results_path, index=True)

        super(ErastosthenesClient, self).connectionLost()

    def send(self):
        logger.info(f'Sending request for all primes between '
                    f'2 and {self._target_n} to {self._saddr}:{self._sport}...')

        self._latest_send = time.monotonic()
        msgpack.pack(self._target_n, stream=self.transport)

    def dataReceived(self, data: bytes):
        rtt = time.monotonic() - self._latest_send
        self._unpacker.feed(data)
        for result in self._unpacker:
            result = np.array(result, dtype=int)
            logger.info(f'Got result from {self._saddr}:{self._sport}.')
            logger.info(f'{result}')

            self._benchmark_results.append(
                {
                    'server'  : f'{self._saddr}:{self._sport}',
                    'target_n': self._target_n,
                    'rtt'     : rtt
                }
            )

            reactor.callLater(callable=self.send, delay=0)


if __name__ == '__main__':
    server_addr = os.environ.get('SERVER_ADDR', 'localhost')
    server_port = int(os.environ.get('SERVER_PORT', 5000))

    logger.info(f'Initializing client for {server_addr}:{server_port}.')

    endpoint = clientFromString(reactor, f'tcp:{server_addr}:{server_port}')


    class _Fact(Factory):
        def buildProtocol(self, addr: IAddress) -> ErastosthenesClient:
            return ErastosthenesClient(server_addr, server_port,
                                       target_n=int(1e6))


    service = ClientService(endpoint, _Fact())
    service.startService()
    reactor.run()
