# utils/logger.py

import datetime
import os

class Logger:
    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40
    }

    def __init__(self, level='INFO'):
        self.level = self.LEVELS.get(level, 20)
        self.current_date = None
        self.log_file = None
        self._update_log_file()
        self.info("Logger initiated")
    
    def _update_log_file(self):
        log_date = datetime.datetime.now().strftime('%Y%m%d')
        if log_date != self.current_date:
            self.current_date = log_date
            log_directory = './logs'
            os.makedirs(log_directory, exist_ok=True)
            self.log_file = os.path.join(log_directory, f"omega.{log_date}.log")
    
    def _log_to_file(self, message):
        self._update_log_file()
        with open(self.log_file, 'a') as file:
            file.write(message + '\n')

    def log(self, message, level='INFO'):
        if self.LEVELS[level] >= self.level:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp} {level}: {message}"
            print(log_message)
            self._log_to_file(log_message)

    def debug(self, message):
        self.log(message, 'DEBUG')

    def info(self, message):
        self.log(message, 'INFO')
    
    def warning(self, message):
        self.log(message, 'WARNING')
    
    def error(self, message):
        self.log(message, 'ERROR')

logger = Logger()