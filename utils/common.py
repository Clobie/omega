# utils/common.py

import random
import re
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

common = Common()