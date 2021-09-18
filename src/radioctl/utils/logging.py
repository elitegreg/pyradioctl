import logging

class BraceStyleLogRecord(logging.LogRecord):
    def getMessage(self):
        """
        Return the message for this LogRecord.

        Return the message for this LogRecord after merging any user-supplied
        arguments with the message.
        """
        msg = str(self.msg)
        if self.args:
            msg = msg.format(*self.args)
        return msg


class BraceStyleLogger(logging.Logger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """
        A factory method which can be overridden in subclasses to create
        specialized LogRecords.
        """
        rv = BraceStyleLogRecord(name, level, fn, lno, msg, args, exc_info,
                                 func, sinfo)
        if extra is not None:
            for key in extra:
                if (key in ["message", "asctime"]) or (key in rv.__dict__):
                    raise KeyError("Attempt to overwrite %r in LogRecord" % key)
                rv.__dict__[key] = extra[key]
        return rv


def getLogger(logger_name):
    klass = logging.getLoggerClass()

    try:
        logging.setLoggerClass(BraceStyleLogger)
        return logging.getLogger(logger_name)
    finally:
        logging.setLoggerClass(klass)


def configure_logging(log_level):
    logging.basicConfig(
        format='{asctime}.{msecs:.0f} {name} [{levelname}] - {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{',
        level=log_level)
