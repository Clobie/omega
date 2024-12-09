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
        init_credits = cfg.NEW_USER_CREDITS
        query_user = (
            "INSERT INTO discord_users (user_id, credits) "
            "VALUES (%s, %s) "
            "ON CONFLICT (user_id) DO NOTHING"
        )
        formatted_user_query = query_user % (user_id, init_credits)
        logger.info(formatted_user_query)
        db.run_script(formatted_user_query)
        return init_credits

    def convert_cost_to_credits(self, cost):
        if cost < 0:
            return 1
        credits_per_cent = 10
        credits = cost * 100 * credits_per_cent
        return max(1, round(credits))

    def get_user_credits(self, user_id):
        query = (
            "SELECT credits FROM discord_users WHERE user_id = %s;"
        )
        formatted_query = query % (user_id)
        result = db.run_script(formatted_query)
        if not result:
            return self.init_user(user_id)
        
        credit_value = round(result[0][0], 2)
        if credit_value.is_integer():
            return int(credit_value)
        return credit_value
    
    def get_server_credits(self, server_id):
        query = (
            "SELECT credits FROM discord_servers WHERE server_id = %s;"
        )
        formatted_query = query % (server_id)
        result = db.run_script(formatted_query)
        if not result:
            self.init_user(server_id)
            return 0
        credit_value = result[0][0]
        return int(round(credit_value, 2)) if round(credit_value, 2) == round(credit_value) else round(credit_value, 2)

    def user_spend(self, user_id, amount):
        from_credits = self.get_user_credits(user_id)
        if from_credits is None or from_credits < amount:
            return False
        query = (
            "UPDATE discord_users "
            "SET credits = credits - %s "
            "WHERE user_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, user_id)
        new_credits = db.run_script(formatted_query)
        return new_credits is not None
    
    def server_spend(self, server_id, amount):
        from_credits = self.get_server_credits(server_id)
        if from_credits is None or from_credits < amount:
            return False
        query = (
            "UPDATE discord_servers "
            "SET credits = credits - %s "
            "WHERE server_id = %s "
            "RETURNING credits;"
        )
        formatted_query = query % (amount, server_id)
        new_credits = db.run_script(formatted_query)
        return new_credits is not None
    
    def get_leaderboard(self, total=None):
        if total is None:
            total = 10
        else:
            total = total if total <= 25 else 10
        query = (
            f"SELECT user_id, credits FROM discord_users ORDER BY credits DESC LIMIT {total};"
        )
        result = db.run_script(query)
        leaderboard_str = "\n".join([
            f"<@{user_id}>: {int(round(credits, 2)) if round(credits, 2) == round(credits) else round(credits, 2)} credits" 
            for user_id, credits in result
        ])
        return leaderboard_str
    
    def give_user_credits(self, user_from, user_to, amount):
        if amount <= 0:
            return False
        from_credits = self.get_user_credits(user_from)
        to_credits = self.get_user_credits(user_to)

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
    
    def gift_user_credits(self, user_to, amount):
        if amount <= 0:
            return False
        to_credits = self.get_user_credits(user_to)
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
    
    def take_user_credits(self, user_from, amount):
        if amount <= 0:
            return False
        from_credits = self.get_user_credits(user_from)
        if from_credits is None:
            return False
        if from_credits < amount:
            amount = from_credits
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