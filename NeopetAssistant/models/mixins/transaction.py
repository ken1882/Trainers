import _G
import utils
import json
from datetime import datetime, timedelta

TRANSACTION_HISTORY_DIR = 'transaction_history'

class NeoItem:
    def __init__(self, id, name, quantity):
        self.id       = id
        self.name     = name
        self.quantity = quantity

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "quantity": self.quantity
        }

class Transaction:
    def __init__(self, spents:list[NeoItem], gains:list[NeoItem], message:str, timestamp=None, **kwargs):
        self.items_spent  = spents
        self.items_gained = gains
        self.message      = message
        self.timestamp    = timestamp or datetime.now()
        self.kwargs       = kwargs
        return self

    def log(self, disable_json_output=False):
        log_str = f"Transaction Log: {self.timestamp}\n"
        log_str += f"Message: {self.message}\n"
        log_str += f"Items Spent: {'None' if not self.items_spent else ''}\n"
        for item in self.items_spent:
            log_str += f"\t{item.name} x{item.quantity}\n"
        log_str += f"Items Gained: {'None' if not self.items_gained else ''}\n"
        for item in self.items_gained:
            log_str += f"\t{item.name} x{item.quantity}\n"
        _G.log_info(log_str)
        if not disable_json_output:
            filename = f"{TRANSACTION_HISTORY_DIR}/{self.timestamp.strftime('%Y-%m-%d')}.json"
            with open(filename, 'a') as f:
                f.write(json.dumps(self.to_dict()))
                f.write('\n')
        return self

    def __str__(self):
        return f"<Transaction: {self.to_dict()}>"

    def to_dict(self):
        return {
            "timestamp": self.timestamp.timestamp(),
            "message": self.message,
            "items_spent": [item.to_dict() for item in self.items_spent],
            "items_gained": [item.to_dict() for item in self.items_gained],
            **self.kwargs
        }