import uuid

from peewee import *
from playhouse.sqlite_ext import JSONField

db_proxy = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = db_proxy

class User(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField()
    email_id = CharField()
    password = CharField()

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)

class Session(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = CharField()
    session_name = CharField(default="new-chat")

    def save(self, *args, **kwargs):
        return super(Session, self).save(*args, **kwargs)

class Chat(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    session_id = CharField()
    message = JSONField()
    model_used = CharField()
    prompt_version_id = CharField()
    rating = IntegerField()
    feedback = CharField()
    action = CharField()

    def save(self, *args, **kwargs):
        return super(Chat, self).save(*args, **kwargs)

class Prompt(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField()
    base_prompt = CharField()
    current_prompt = CharField()
    version_number = IntegerField()
    calibrated_prompts = JSONField()

    def save(self, *args, **kwargs):
        return super(Prompt, self).save(*args, **kwargs)

def db_init():
    db = SqliteDatabase('prompt-calibrate.db')
    db_proxy.initialize(db)
    db.connect()
    db.create_tables([User, Session, Chat, Prompt])
    return db