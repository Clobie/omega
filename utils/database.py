# utils/database.py

import os
import discord
from pymongo import MongoClient
from utils.config import cfg
from utils.log import logger

class Database:
    def __init__(self):
        self.client = MongoClient(cfg.DATABASE_USER, cfg.DATABASE_PASS)
        self.db = self.client[cfg.DATABASE_NAME]
        self.collection = self.db[cfg.DATABASE_COLLECTION_NAME]

db = Database()