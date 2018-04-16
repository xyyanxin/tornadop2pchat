import time
import uuid
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Text, Float

from sqlalchemy.orm import sessionmaker

Base = declarative_base()
sqlalchemy_url = 'mysql+pymysql://dbu:dddd@localhost/chat?charset=utf8mb4'
engine = create_engine(sqlalchemy_url)
DBsession = sessionmaker(bind=engine)
session = DBsession()


class MixinModel(object):

    @classmethod
    def create(cls,**params):
        instance = cls(**params)
        session.add(instance)
        session.commit()
        print(instance.id)
        return instance

    def to_dict(self,keys_list=None):
        if keys_list is None:
            keys_list = [i.name for i in self.__table__.columns]
        ret_dict = {}
        for k in keys_list:
            value = getattr(self, k)
            ret_dict[k] = value
        return ret_dict


class UserModel(Base,MixinModel):
    __tablename__ = 'user_model'
    id = Column(String(20), primary_key=True)

class MessageModel(Base,MixinModel):
    __tablename__ = 'message_model'
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(Integer ,nullable=False)
    target_user_id = Column(Integer,nullable=False)
    message_type = Column(String(16),nullable=False)
    message_text = Column(Text)             # can be text sound vido
    message_url = Column(String(52))
    remark = Column(String(52))
    dt_create = Column(Float, default=lambda: time.time())




if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = DBsession()
    session.add(MessageModel(from_user_id=1,target_user_id=2,message_type='tset'))
    #session.add(MessageModel(from_user_id=2,target_user_id=2,message_type='tset'))
    #session.add(MessageModel(from_user_id=3,target_user_id=2,message_type='tset'))
    #UserModel.create(id=40)
    session.commit()
    session.close()
