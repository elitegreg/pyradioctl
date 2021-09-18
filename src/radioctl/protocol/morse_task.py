from radioctl.msgbus import MsgType
from radioctl.utils import logging

import weakref


_logger = logging.getLogger('MorseTask')


class MorseTask:
    def __init__(self, msgbus, send_method, cancel_method, data_len_limit):
        self._task = None
        self._data_len_limit = data_len_limit
        self._buf = []
        self._buf_space_available = asyncio.Event()
        self._buf_space_available.set()
        self._send_method = weakref.proxy(send_method)
        self._cancel_method = weakref.proxy(cancel_method)
        msgbus[MsgType.KEYER_BUFFER_AVAILABLE].connect(self._buffer_available)
        msgbus[MsgType.KEYER_BUFFER_FULL].connect(self._buffer_full)

    def send_morse(self, buf):
        maxlen = self._data_len_limit
        while len(buf) > 0:
            if len(self._buf) > 0 and (len(self._buf[-1]) + len(buf)) <= maxlen:
                self._buf[-1] += buf
            else:
                self._buf.append(buf[0:maxlen])
            buf = buf[maxlen:]
        if not self._task or self._task.done():
            self._task = \
                asyncio.create_task(self._morse_sender(), name='Morse Sender')

    def cancel_morse(self):
        if self._task:
            self._task.cancel()
        self._cancel_method()
        del self._buf[:]
        self._buf_space_available.set()

    async def _morse_sender(self):
        try:
            _logger.debug('Starting Morse Sender...')

            while len(self._buf):
                _logger.debug('Morse string remaining: %s', self._buf)
                if not self._buf_space_available.is_set():
                    _logger.debug('Waiting for rig to report buffer available')
                    await self._buf_space_available.wait()
                self._buf_space_available.clear()
                buf = self._buf.pop(0)
                self._send_method(buf)
        except asyncio.CancelledError:
            pass
        _logger.debug('Morse Sender Complete')

    def _buffer_available(self):
        self._buf_space_available.set()

    def _buffer_full(self):
        self._buf_space_available.clear()
