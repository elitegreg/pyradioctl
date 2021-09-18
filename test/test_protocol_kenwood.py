from radioctl.protocol.kenwood.protocol import (
    ModeHandler, Protocol, RxToggleHandler, RxVfoToggleHandler,
    TxToggleHandler, TxVfoToggleHandler, VfoHandler)
from radioctl.msgbus import *
from radioctl.protocol import factory

import asyncio
import socket
import unittest
import unittest.mock


class ProtocolWrapper(Protocol):
    _send = unittest.mock.MagicMock()

    def __init__(self, *args, **kwargs):
        ProtocolWrapper._send.reset_mock()
        super().__init__(*args, **kwargs)


class ProtocolTest(unittest.TestCase):
    DEFINITION = dict(protocol_config={
        'vfo_0': {
            'get': 'FA;',
            'set': 'FA{freq:011d};',
            'response': 'FA(?P<freq>\\d{11});',
        },
        'vfo_1': {
            'get': 'FB;',
            'set': 'FB{freq:011d};',
            'response': 'FB(?P<freq>\\d{11});',
        },
        'mode_0': {
            'get': 'MD;',
            'set': 'MD{mode:d};',
            'response': 'MD(?P<mode>\\d);',
        },
        'mode_1': {
            'get': 'MD$;',
            'set': 'MD${mode:d};',
            'response': 'MD\\$(?P<mode>\\d);',
        },
        'rx_vfo': {
            'get': 'FR;',
            'response': 'FR(?P<index>[01]);',
            'set': 'FR{index:d};',
        },
        'tx_vfo': {
            'get': 'FT;',
            'response': 'FT(?P<index>[01]);',
            'set': 'FT{index:d};',
        },
        'rx': {
            'response': 'RX;',
            'set': 'RX;',
        },
        'tx': {
            'response': 'TX;',
            'set': 'TX;',
        },
    })

    def setUp(self):
        self.msgbus = MsgBus()
        self.protocol = ProtocolWrapper('Elecraft', None, self.msgbus, self.DEFINITION)
        self.vfo_callbacks = unittest.mock.MagicMock()
        self.vfo_handler0 = self.protocol._handlers['FA']
        self.vfo_handler1 = self.protocol._handlers['FB']
        self.mode_callbacks = unittest.mock.MagicMock()
        self.mode_handler0 = self.protocol._handlers['MD']
        self.mode_handler1 = self.protocol._handlers['MD$']
        self.rx_vfo_callbacks = unittest.mock.MagicMock()
        self.rx_vfo_handler = self.protocol._handlers['FR']
        self.tx_vfo_callbacks = unittest.mock.MagicMock()
        self.tx_vfo_handler = self.protocol._handlers['FT']
        self.rx_callbacks = unittest.mock.MagicMock()
        self.rx_handler = self.protocol._handlers['RX']
        self.tx_callbacks = unittest.mock.MagicMock()
        self.tx_handler = self.protocol._handlers['TX']
        self.msgbus[MsgType.VFO_FREQUENCY_RESULT].connect(self.vfo_callbacks)
        self.msgbus[MsgType.VFO_MODE_RESULT].connect(self.mode_callbacks)
        self.msgbus[MsgType.RX_VFO_RESULT].connect(self.rx_vfo_callbacks)
        self.msgbus[MsgType.TX_VFO_RESULT].connect(self.tx_vfo_callbacks)
        self.msgbus[MsgType.RECEIVE_RESULT].connect(self.rx_callbacks)
        self.msgbus[MsgType.TRANSMIT_RESULT].connect(self.tx_callbacks)

    def test_protocol_registration(self):
        self.assertEquals(factory._all_protocols['Kenwood'], Protocol)

    def test_vfo_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_SET](2, 3573000)
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_SET](0, 3573000)
        self.protocol._send.assert_called_once_with('FA00003573000;')
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_SET](1, 7074000)
        self.protocol._send.assert_called_with('FB00007074000;')

    def test_vfo_handler_get(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_QUERY](2)
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_QUERY](0)
        self.protocol._send.assert_called_once_with('FA;')
        self.protocol._msgbus[MsgType.VFO_FREQUENCY_QUERY](1)
        self.protocol._send.assert_called_with('FB;')

    def test_vfo_handler_response(self):
        self.vfo_callbacks.assert_not_called()
        self.vfo_handler0('FA00003573000;')
        self.vfo_handler0('FA00014074000;')
        self.vfo_handler0('FAABC03573000;')
        self.vfo_handler1('FB00003573000;')
        self.vfo_handler1('FB00014074000;')
        self.vfo_handler1('FBABC03573000;')
        self.assertEquals(4, self.vfo_callbacks.call_count)
        self.assertEquals((0, 3573000), self.vfo_callbacks.call_args_list[0].args)
        self.assertEquals((0, 14074000), self.vfo_callbacks.call_args_list[1].args)
        self.assertEquals((1, 3573000), self.vfo_callbacks.call_args_list[2].args)
        self.assertEquals((1, 14074000), self.vfo_callbacks.call_args_list[3].args)

    def test_mode_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_MODE_SET](2, "CW")
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_MODE_SET](0, "CW")
        self.protocol._send.assert_called_once_with('MD3;')
        self.protocol._msgbus[MsgType.VFO_MODE_SET](1, "PKTUSB")
        self.protocol._send.assert_called_with('MD$6;')

    def test_mode_handler_get(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_MODE_QUERY](2)
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.VFO_MODE_QUERY](0)
        self.protocol._send.assert_called_once_with('MD;')
        self.protocol._msgbus[MsgType.VFO_MODE_QUERY](1)
        self.protocol._send.assert_called_with('MD$;')

    def test_mode_handler_response(self):
        self.mode_callbacks.assert_not_called()
        self.mode_handler0('MD1;')
        self.mode_handler0('MD2;')
        self.mode_handler0('MDX;')
        self.mode_handler1('MD$1;')
        self.mode_handler1('MD$2;')
        self.mode_handler1('MD$X;')
        self.assertEquals(4, self.mode_callbacks.call_count)
        self.assertEquals((0, "LSB"), self.mode_callbacks.call_args_list[0].args)
        self.assertEquals((0, "USB"), self.mode_callbacks.call_args_list[1].args)
        self.assertEquals((1, "LSB"), self.mode_callbacks.call_args_list[2].args)
        self.assertEquals((1, "USB"), self.mode_callbacks.call_args_list[3].args)

    def test_rx_vfo_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.RX_VFO_SET](0)
        self.protocol._send.assert_called_once_with('FR0;')
        self.protocol._msgbus[MsgType.RX_VFO_SET](1)
        self.protocol._send.assert_called_with('FR1;')

    def test_rx_vfo_handler_get(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.RX_VFO_QUERY]()
        self.protocol._send.assert_called_once_with('FR;')

    def test_rx_vfo_handler_response(self):
        self.rx_vfo_callbacks.assert_not_called()
        self.rx_vfo_handler('FR0;')
        self.rx_vfo_handler('FR1;')
        self.rx_vfo_handler('FRX;')
        self.assertEquals(2, self.rx_vfo_callbacks.call_count)
        self.assertEquals((0,), self.rx_vfo_callbacks.call_args_list[0].args)
        self.assertEquals((1,), self.rx_vfo_callbacks.call_args_list[1].args)

    def test_tx_vfo_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.TX_VFO_SET](0)
        self.protocol._send.assert_called_once_with('FT0;')
        self.protocol._msgbus[MsgType.TX_VFO_SET](1)
        self.protocol._send.assert_called_with('FT1;')

    def test_tx_vfo_handler_get(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.TX_VFO_QUERY]()
        self.protocol._send.assert_called_once_with('FT;')

    def test_tx_vfo_handler_response(self):
        self.tx_vfo_callbacks.assert_not_called()
        self.tx_vfo_handler('FT0;')
        self.tx_vfo_handler('FT1;')
        self.tx_vfo_handler('FTX;')
        self.assertEquals(2, self.tx_vfo_callbacks.call_count)
        self.assertEquals((0,), self.tx_vfo_callbacks.call_args_list[0].args)
        self.assertEquals((1,), self.tx_vfo_callbacks.call_args_list[1].args)

    def test_rx_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.RECEIVE_SET]()
        self.protocol._send.assert_called_once_with('RX;')

    def test_rx_handler_response(self):
        self.rx_callbacks.assert_not_called()
        self.rx_handler('RX;')
        self.assertEquals(1, self.rx_callbacks.call_count)
        self.assertEquals(tuple(), self.rx_callbacks.call_args_list[0].args)

    def test_tx_handler_set(self):
        self.protocol._send.assert_not_called()
        self.protocol._msgbus[MsgType.TRANSMIT_SET]()
        self.protocol._send.assert_called_once_with('TX;')

    def test_tx_handler_response(self):
        self.tx_callbacks.assert_not_called()
        self.tx_handler('TX;')
        self.assertEquals(1, self.tx_callbacks.call_count)
        self.assertEquals(tuple(), self.tx_callbacks.call_args_list[0].args)

    def test_protocol_open(self):
        self.vfo_callbacks.assert_not_called()
        self.rx_vfo_callbacks.assert_not_called()
        self.tx_vfo_callbacks.assert_not_called()
        (cat_sock, rig_sock) = socket.socketpair()
        rig_sock.send(b'FA00003500000;FB00007100000;FR0;FT1;')
        rig_sock.close()
        loop = asyncio.get_event_loop()
        task = loop.create_task(asyncio.open_connection(sock=cat_sock))
        loop.run_until_complete(task)
        (reader, writer) = task.result()
        task = self.protocol.open(loop, reader, writer)
        loop.run_until_complete(task)
        self.assertEquals(2, self.vfo_callbacks.call_count)
        self.assertEquals((0, 3500000), self.vfo_callbacks.call_args_list[0].args)
        self.assertEquals((1, 7100000), self.vfo_callbacks.call_args_list[1].args)
        self.assertEquals(1, self.rx_vfo_callbacks.call_count)
        self.assertEquals((0,), self.rx_vfo_callbacks.call_args_list[0].args)
        self.assertEquals(1, self.tx_vfo_callbacks.call_count)
        self.assertEquals((1,), self.tx_vfo_callbacks.call_args_list[0].args)
