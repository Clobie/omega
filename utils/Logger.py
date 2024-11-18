# utils/logger.py

class Logger:
    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40
    }

    def __init__(self, level='INFO'):
        self.level = self.LEVELS.get(level, 20)
    
    def log(self, message, level='INFO'):
        if self.LEVELS[level] >= self.level:
            print(f"{level}: {message}")

    def debug(self, message):
        self.log(message, 'DEBUG')

    def info(self, message):
        self.log(message, 'INFO')
    
    def warning(self, message):
        self.log(message, 'WARNING')
    
    def error(self, message):
        self.log(message, 'ERROR')