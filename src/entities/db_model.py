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
    session_id = CharField(null=True)
    user_message = TextField(null=True)
    assistant_message = TextField(null=True)
    model_used = CharField(null=True)
    prompt_version_id = CharField(null=True)
    rating = IntegerField(null=True)
    feedback = CharField(null=True)
    action = CharField(null=True)

    def save(self, *args, **kwargs):
        return super(Chat, self).save(*args, **kwargs)

class Prompt(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(null=True)
    base_prompt = CharField(null=True)
    current_prompt = CharField(null=True)
    version_number = IntegerField(null=True)
    calibrated_prompts = JSONField(null=True)

    def save(self, *args, **kwargs):
        return super(Prompt, self).save(*args, **kwargs)

def db_init():
    db = SqliteDatabase('prompt-calibrate.db')
    db_proxy.initialize(db)
    db.connect()
    db.create_tables([User, Session, Chat, Prompt])
    return db