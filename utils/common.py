# utils/common.py

import random
import re
import string
from datetime import datetime
from utils.log import logger

class Common:
    def __init__(self):
        self.superscript_mapping = str.maketrans(
            "0123456789abcdefghijklmnopqrstuvwxyz.-",
            "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ˙ˉ"
        )
     
    def chance(self, percent):
        return random.random() < (percent / 100)
     
    def to_superscript(self, text):
        return text.translate(self.superscript_mapping)
    
    def remove_superscript(self, text):
        superscript_pattern = r'[\u00B2\u00B3\u00B9\u1D2C0-\u1D2DF]'
        return re.sub(superscript_pattern, '', text)
    
    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def get_unix_timestamp(date_str, date_format="%Y-%m-%d %H:%M:%S"):
        dt = datetime.strptime(date_str, date_format)
        return int(dt.timestamp())

    def get_unix_interval(timestamp1, timestamp2):
        diff = abs(timestamp1 - timestamp2) / 1000
        if diff <= 300:
            return '5m'
        elif diff <= 3600:
            return 'hourly'
        else:
            return 'daily'
    
common = Common()