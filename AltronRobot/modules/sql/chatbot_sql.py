import threading

from sqlalchemy import Column, String
from AltronRobot.modules.sql import BASE, SESSION


class AltChats(BASE):
    __tablename__ = "alt_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


AltChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_alt(chat_id):
    try:
        chat = SESSION.query(AltChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_alt(chat_id):
    with INSERTION_LOCK:
        altchat = SESSION.query(AltChats).get(str(chat_id))
        if not altchat:
            altchat = AltChats(str(chat_id))
        SESSION.add(altchat)
        SESSION.commit()


def rem_alt(chat_id):
    with INSERTION_LOCK:
        altchat = SESSION.query(AltChats).get(str(chat_id))
        if altchat:
            SESSION.delete(altchat)
        SESSION.commit()


def get_all_alt_chats():
    try:
        return SESSION.query(AltChats.chat_id).all()
    finally:
        SESSION.close()
