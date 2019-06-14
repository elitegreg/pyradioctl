import contextlib
import enum
import io
import operator
import sys
import time
import traceback


class LogLevel(enum.Enum):
    FATAL = 0
    ERROR = 1
    WARN  = 2
    INFO  = 3
    DEBUG = 4
    TRACE = 5

    def __comparison__(self, rhs, op):
        return type(self) is type(rhs) and op(self.value, rhs.value)

    def __le__(self, rhs):
        return self.__comparison__(rhs, op=operator.le)

    def __lt__(self, rhs):
        return self.__comparison__(rhs, op=operator.lt)

    def __eq__(self, rhs):
        return self.__comparison__(rhs, op=operator.eq)

    def __ne__(self, rhs):
        return self.__comparison__(rhs, op=operator.ne)

    def __gt__(self, rhs):
        return self.__comparison__(rhs, op=operator.gt)

    def __ge__(self, rhs):
        return self.__comparison__(rhs, op=operator.ge)

    def __repr__(self):
        return 'LogLevel.{}={}'.format(self.name, self.value)

    def __str__(self):
        return self.name


def log_level_from_string(s):
    if s.upper() == 'FATAL':
        return LogLevel.FATAL
    if s.upper() == 'ERROR':
        return LogLevel.ERROR
    if s.upper() == 'WARN':
        return LogLevel.WARN
    if s.upper() == 'INFO':
        return LogLevel.INFO
    if s.upper() == 'DEBUG':
        return LogLevel.DEBUG
    if s.upper() == 'TRACE':
        return LogLevel.TRACE
    raise RuntimeError('Invalid log level')


_log_file = sys.stdout
@contextlib.contextmanager
def initialize(self, filename=None, fp=None):
    global _log_file
    if filename and fp:
        raise RuntimeError('Filename and fp cannot be specified at the same time!')
    elif filename:
        _log_file = open(filename, 'a')
    elif fp:
        _log_file = fp
    else:
        _log_file = sys.stdout
    yield
    _log_file.close()


class Logger:
    def __init__(self, name):
        self.__name = name
        self.__log_level = LogLevel.INFO

    def setLevel(self, lvl):
        if type(lvl) == type(''):
            lvl = LogLevel[lvl]
        self.__log_level = lvl

    def log(self, level, msg, *args, **kwargs):
        if self.__log_level >= level:
            self._format_and_output(level, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        return self.log(LogLevel.FATAL, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.log(LogLevel.ERROR, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        return self.log(LogLevel.WARN, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.log(LogLevel.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.log(LogLevel.DEBUG, msg, *args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        if __debug__:
            return self.log(LogLevel.TRACE, msg, *args, **kwargs)
        return None

    def exception(self, msg, log_level=LogLevel.ERROR, *args, **kwargs):
        sio = io.StringIO()
        sio.write(msg)
        sio.write('\n')
        traceback.print_exception(*sys.exc_info(), file=sio)
        s = sio.getvalue()
        sio.close()
        self.log(log_level, s, *args, **kwargs)


class _NewStyleLogger(Logger):
    def __init__(self, name):
        super().__init__(name)

    def _format_and_output(self, level, msg, *args, **kwargs):
        tm = time.time()
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tm))
        ts += '%03f' % (tm % 1)
        msg = msg.format(*args, **kwargs)
        print("{} [{}] - {}".format(ts, str(level), msg), file=_log_file)


class _OldStyleLogger(Logger):
    def __init__(self, name):
        super().__init__(name)

    def _format_and_output(self, level, msg, *args, **kwargs):
        tm = time.time()
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tm))
        ts += '%03f' % (tm % 1)
        msg = msg % args % kwargs
        print("{} [{}] - {}".format(ts, str(level), msg), file=_log_file)


_all_loggers = {}
def getLogger(name, loggertype=_OldStyleLogger):
    try:
        return _all_loggers[name]
    except KeyError:
        logger = loggertype(name)
        _all_loggers[name] = logger
        return logger
    
_default_logger = getLogger('default', _NewStyleLogger)
log = _default_logger.log
fatal = _default_logger.fatal
error = _default_logger.error
warn = _default_logger.warn
info = _default_logger.info
debug = _default_logger.debug
trace = _default_logger.trace
exception = _default_logger.exception

FATAL = LogLevel.FATAL
ERROR = LogLevel.ERROR
WARN  = LogLevel.WARN
INFO  = LogLevel.INFO
DEBUG = LogLevel.DEBUG
TRACE = LogLevel.TRACE

