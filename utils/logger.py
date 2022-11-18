import logging
from logging.handlers import RotatingFileHandler

ilogger = logging.getLogger('importer')
ilogger.setLevel(logging.INFO)
ilogger.propagate = False

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
ilogger.addHandler(ch)

fh = RotatingFileHandler("logs/importer.log", maxBytes=50000, backupCount=8)
fh.setFormatter(formatter)
ilogger.addHandler(fh)


sqllogger = logging.getLogger('sql')
sqllogger.setLevel(logging.INFO)
sqllogger.propagate = False

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
sqllogger.addHandler(ch)

fh = RotatingFileHandler("logs/sql.log", maxBytes=50000, backupCount=8)
fh.setFormatter(formatter)
sqllogger.addHandler(fh)
