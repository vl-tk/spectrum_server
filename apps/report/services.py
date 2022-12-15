import difflib
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd
from eav.models import Attribute
from transliterate import translit
from utils.logger import ilogger


class ReportBuilder:

    def __init__(self, data):
        self.data = data
