# utils/credit.py

import os
import discord
from utils.config import cfg
from utils.log import logger
from utils.status import status
from utils.common import common
from utils.database import db

class Credit:
    def __init__(self):
        pass

    def init_user(self, user_id):
        query_user = (
            "INSERT INTO discord_users (user_id, credits) "
            "VALUES (%s, 0) "
            "ON CONFLICT (user_id) DO NOTHING"
        )
        formatted_user_query = query_user % user_id
        logger.info(formatted_user_query)
        db.run_script(formatted_user_query)

    def get_credits(self, user_id):
        query = (
            "SELECT credits FROM discord_users WHERE user_id = %s;"
        )
        formatted_query = query % (user_id)
        result = db.run_script(formatted_query)
        if not result:
            self.init_user(user_id)
        return result[0][0] if result else 0
    
    def give_credits(self, user_from, user_to, amount):
        if amount <= 0:
            return False
        from_credits = self.get_credits(user_from)
        to_credits = self.get_credits(user_to)

        if from_credits is None or to_credits is None:
            return False
        
        if from_credits < amount:
            return False

        query = (
            "WITH deducted AS ("
            "    UPDATE discord_users "
            "    SET credits = credits - %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            "), "
            "added AS ("
            "    UPDATE discord_users "
            "    SET credits = credits + %s "
            "    WHERE user_id = %s "
            "    RETURNING credits "
            ") "
            "SELECT (SELECT credits FROM deducted) AS from_credits, "
            "       (SELECT credits FROM added) AS to_credits;"
        )
        formatted_query = query % ((amount, user_from, amount, user_to))
        db.run_script(formatted_query)
        return True
    
    def gift_credits(self, user_to, amount):
        if amount <= 0:
            return False
        to_credits = self.get_credits(user_to)
        if to_credits is None:
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits + %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, user_to)
        new_credits = db.run_script(formatted_query)
        return new_credits is not None
    
    def take_credits(self, user_from, amount):
        if amount <= 0:
            return False
        from_credits = self.get_credits(user_from)
        if from_credits is None or from_credits < amount:
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits - %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, user_from)
        new_credits = db.run_script(formatted_query)
        return new_credits is not None

credit = Credit()