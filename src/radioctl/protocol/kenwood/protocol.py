from .dialects import create_dialect
from ..factory import register_protocol
from ..morse_task import MorseTask

from radioctl.msgbus import MsgType
from radioctl.utils import logging

import functools
import re
import weakref

_logger = logging.getLogger('kenwood')

__ALL__ = ['Protocol']


class Handler:
    def __init__(self, protocol, handler_cfg):
        # TODO self._send_method = weakref.proxy(protocol._send)
        self._send_method = protocol._send
        self._cmd = ''
        self._get_cmd = ''
        self._set_cmd = ''
        self._response_re = None
        self._parse_params(handler_cfg)

    def __call__(self, msg):
        assert(self._response_re)
        assert(self._response_signal)
        match = self._response_re.match(msg)
        if match:
            self._response(match)
        else:
            _logger.warn('Could not parse: {}', msg)

    def _parse_params(self, handler_cfg):
        if 'get' in handler_cfg:
            self._get_cmd = handler_cfg['get']
        if 'set' in handler_cfg:
            self._set_cmd = handler_cfg['set']
        if 'response' in handler_cfg:
            resp = handler_cfg['response']
            self._cmd = resp[0:2]
            if resp[2] == '\\' and resp[3] == '$':
                self._cmd += '$'
            self._response_re = re.compile(resp)

    def _response(self, match):
        self._response_signal()

    def _set_value(self, *args, **kwargs):
        self._send_method(self._set_cmd)

    def _get_value(self):
        self._send_method(self._get_cmd)


class VfoHandler(Handler):
    def __init__(self, protocol, handler_cfg, index):
        super().__init__(protocol, handler_cfg)
        self._index = index
        self._response_signal = protocol._msgbus[MsgType.VFO_FREQUENCY_RESULT]
        protocol._msgbus[MsgType.VFO_FREQUENCY_SET].connect(self._set_frequency)
        protocol._msgbus[MsgType.VFO_FREQUENCY_QUERY].connect(self._get_frequency)

    def _response(self, match):
        self._response_signal(self._index, int(match.group('freq')))

    def _set_frequency(self, index, frequency):
        if index == self._index:
            self._send_method(self._set_cmd.format(freq=frequency))

    def _get_frequency(self, index):
        if index == self._index:
            self._send_method(self._get_cmd)


class ModeHandler(Handler):
    def __init__(self, protocol, handler_cfg, index):
        super().__init__(protocol, handler_cfg)
        self._index = index
        self._dialect = protocol._dialect
        self._response_signal = protocol._msgbus[MsgType.VFO_MODE_RESULT]
        if self._set_cmd:
            protocol._msgbus[MsgType.VFO_MODE_SET].connect(self._set_mode)
        if self._get_cmd:
            protocol._msgbus[MsgType.VFO_MODE_QUERY].connect(self._get_mode)

    def _response(self, match):
        self._response_signal(self._index,
                              self._dialect.mode_from_rig(match.group('mode')))

    def _set_mode(self, index, mode):
        if index == self._index:
            self._send_method(self._set_cmd.format(mode=self._dialect.mode_to_rig(mode)))

    def _get_mode(self, index):
        if index == self._index:
            self._send_method(self._get_cmd)


class VfoToggleHandler(Handler):
    def __init__(self, set_signal, query_signal, result_signal, protocol, handler_cfg):
        super().__init__(protocol, handler_cfg)
        self._response_signal = protocol._msgbus[result_signal]
        if self._set_cmd:
            protocol._msgbus[set_signal].connect(self._set_value)
        if self._get_cmd:
            protocol._msgbus[query_signal].connect(self._get_value)

    def _response(self, match):
        self._response_signal(int(match.group('index')))

    def _set_value(self, index):
        self._send_method(self._set_cmd.format(index=index))


RxVfoToggleHandler = functools.partial(VfoToggleHandler,
                                       MsgType.RX_VFO_SET,
                                       MsgType.RX_VFO_QUERY,
                                       MsgType.RX_VFO_RESULT)

TxVfoToggleHandler = functools.partial(VfoToggleHandler,
                                       MsgType.TX_VFO_SET,
                                       MsgType.TX_VFO_QUERY,
                                       MsgType.TX_VFO_RESULT)


class ToggleHandler(Handler):
    def __init__(self, set_signal, query_signal, result_signal, protocol, handler_cfg):
        super().__init__(protocol, handler_cfg)
        self._response_signal = protocol._msgbus[result_signal]
        if self._set_cmd:
            protocol._msgbus[set_signal].connect(self._set_value)
        if self._get_cmd:
            protocol._msgbus[query_signal].connect(self._get_value)


RxToggleHandler = functools.partial(ToggleHandler,
                                    MsgType.RECEIVE_SET,
                                    MsgType.RECEIVE_QUERY,
                                    MsgType.RECEIVE_RESULT)


TxToggleHandler = functools.partial(ToggleHandler,
                                    MsgType.TRANSMIT_SET,
                                    MsgType.TRANSMIT_QUERY,
                                    MsgType.TRANSMIT_RESULT)


class KeyerSpeedHandler(Handler):
    def __init__(self, protocol, handler_cfg):
        super().__init__(protocol, handler_cfg)
        self._response_signal = protocol._msgbus[MsgType.KEYER_SPEED_RESULT]
        protocol._msgbus[MsgType.KEYER_SPEED_SET].connect(self._set_value)
        protocol._msgbus[MsgType.KEYER_SPEED_QUERY].connect(self._get_value)
        self._min, self._max = handler_cfg['range'].split('-', 1)

    def _response(self, match):
        self._response_signal(int(match.group('speed')))

    def _set_value(self, speed):
        speed = max(speed, self._min)
        speed = min(speed, self._max)
        self._send_method(self._set_cmd.format(speed=speed))


class CatCWHandler:
    def __init__(self, protocol, handler_cfg):
        # TODO self._send_method = weakref.proxy(protocol._send)
        self._send_method = protocol._send
        self._cancel_method = functools.partial(self._send_method, handler_cfg['cancel'])
        self._send_cmd = handler_cfg['send']


class Protocol:
    def __init__(self, dialect, cfg, msgbus, rig_def):
        self._msgbus = msgbus
        self._dialect = create_dialect(cfg, dialect)
        self._startup = ''
        self._handlers = {}
        self._no_response_handlers = []
        self._create_handlers(rig_def['protocol_config'])

    @property
    def msgbus(self):
        return self._msgbus

    def open(self, loop, reader, writer):
        self._reader = reader
        self._writer = writer
        self._send(self._startup)
        if hasattr(self._dialect, "startup_commands"):
            self._send(self._dialect.startup_commands)
        return loop.create_task(self.reader_task(), name='Reader Task')

    async def reader_task(self):
        handlers = self._handlers
        try:
            while True:
                pkt = await self._reader.readuntil(b';')
                msg = pkt.decode()
                _logger.debug('Received: {}', msg)
                if len(msg) < 3:
                    _logger.warn('Message too short: {}', msg)
                    continue
                if msg[2] == '$':
                    cmd = msg[0:3]
                else:
                    cmd = msg[0:2]
                try:
                    handler = handlers[cmd]
                    handler(msg)
                except KeyError:
                    _logger.debug('No handler for: {}', msg)
        except EOFError:
            _logger.info('Terminating reader task')

    def _send(self, data):
        _logger.debug('Sending: {}', data)
        self._writer.write(data.encode())

    def _register_handler(self, handler):
        if handler._cmd:
            self._handlers[handler._cmd] = handler
        else:
            self._no_response_handlers.append(handler)

    def _create_handlers(self, protocol_def):
        for (name, item) in protocol_def.items():
            if name == 'startup':
                self._startup = item
                continue
            elif name.startswith('vfo_'):
                index = int(name.split('_', 1)[1])
                handler = VfoHandler(self, item, index)
            elif name.startswith('mode_'):
                index = int(name.split('_', 1)[1])
                handler = ModeHandler(self, item, index)
            elif name == 'rx_vfo':
                handler = RxVfoToggleHandler(self, item)
            elif name == 'tx_vfo':
                handler = TxVfoToggleHandler(self, item)
            elif name == 'rx':
                handler = RxToggleHandler(self, item)
            elif name == 'tx':
                handler = TxToggleHandler(self, item)
            elif name == 'keyer_speed':
                handler = KeyerSpeedHandler(self, item)
            elif name == 'cw':
                mode = item['mode']
                if mode.lower() == 'cat':
                    pass
                    #handler = CatCWHandler(self, item)
                else:
                    raise RuntimeError(f'Unknown cw handler mode: {mode}')
            else:
                _logger.info("Handler {} not supported", name)
                continue

            self._register_handler(handler)


register_protocol('Kenwood', Protocol)
