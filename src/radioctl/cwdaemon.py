import asyncio
import logging


ESC = '\x1b'


class CWDaemonListenerProtocol(asyncio.Protocol):
    ESC_CMDS = {
        '0' : 'not_implemented', #'reset_to_default_values',
        '2' : 'set_keying_speed',
        '4' : 'abort_message',
        '5' : 'not_implemented', #'exit'
        '7' : 'not_implemented', #'set_weighting',
        'a' : 'not_implemented', #'ptt_keying',
        'b' : 'not_implemented', #'ssb_signal_from',
        'c' : 'not_implemented', #'tune_x_seconds',
        'h' : 'set_data_reply',
    }

    def __init__(self, hamlib_protocol, is_complete):
        self._data_reply = None
        self._hamlib_protocol = hamlib_protocol

    def connection_made(self, transport):
        self._transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        if message.startswith(ESC):
            cmd = message[1]
            data = None

            if len(message) > 2:
                message = message[2:]

            mapped_cmd = self.ESC_CMDS.get(cmd, 'not_implemented')
            func = getattr(self, mapped_cmd)
            assert(func)
            func(cmd, message)
        else:
            self.send_cw(message)
            if self._data_reply:
                self._transport.sendto(self._data_reply.encode(), addr)

    def abort_message(self, cmd, message):
        self._hamlib_protocol.cancel_morse()

    def not_implemented(self, cmd, message):
        logging.warn('Unhandled command %s with data: %s', cmd, message)

    def set_data_reply(self, cmd, message):
        self._data_reply = cmd + message

    def set_keying_speed(self, cmd, message):
        self._hamlib_protocol.morse_speed(message)

    def send_cw(self, message):
        logging.info('Sending: %s', message)
        self._hamlib_protocol.send_morse(message.replace('~', ' '))


class CWDaemonListener:
    async def start(self, hamlib_protocol, loop, bindaddr, port):
        logging.info('Starting CWDaemonListener on %s:%d', bindaddr, port)
        is_complete = loop.create_future()
        transport, protocol = \
            await loop.create_datagram_endpoint(
                lambda: CWDaemonListenerProtocol(hamlib_protocol, is_complete),
                local_addr=(bindaddr, port))
        await is_complete
