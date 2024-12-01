# utils/database.py

import os
import discord
from pymongo import MongoClient
from utils.config import cfg
from utils.log import logger

class Database:
    def __init__(self):
        self.client = MongoClient(cfg.database_user, cfg.database_pass)
        self.db = self.client[cfg.database_name]
        self.collection = self.db[cfg.database_collection_name]

db = Database()