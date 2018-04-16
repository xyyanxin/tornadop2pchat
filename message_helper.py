#coding:utf-8
""""
Program: tornadop2pserver
Description: 
Author: XY - mailyanxin@gmail.com
Date: 2018-04-16 02:36:45
Last modified: 2018-04-16 09:34:15
Python release: 3.5.2
"""

import time
import logging
from tornado.concurrent import Future
from mysql_helper import MessageModel
from mysql_helper import UserModel
from mysql_helper import DBsession

class MessageBuffer(object):
    def __init__(self):
        '''
        used as global
        {'wait_from_user_id': a,'wait_target_user_id': b, 'future': Future}
        {'from_user_id': a,'target_user_id': b, 'data': message}
        '''
        self.waiters = []

    def new_messages(self,from_user_id,data,target_user_id):
        # 1.存消息
        foo_dict = {
                'from_user_id': from_user_id,
                'target_user_id': target_user_id,
                'message_type': data['message_type'],
                'message_text': data['message_text'],
                'dt_create': time.time(),
                }
        ret = MessageModel.create(**foo_dict)
        logging.info('消息存储成功')

        # 2.信息发给相关的future
        waiters = [i for i in self.waiters
                if i['wait_target_user_id'] == from_user_id and i['wait_from_user_id'] == target_user_id]
        if len(waiters) == 1:
            result_list = [{
                    'message_type': ret.message_type,
                    'message_text': ret.message_text,
                    'cursor': ret.id,
                    }]
            waiters[0]['future'].set_result(result_list)
            logging.info('sending to online listeners')
        elif len(waiters) == 0:
            logging.info('but nobody online listen')
        else:
            logging.info('error')
            logging.info(self.waiters)

        # 3.future clear
        self.refresh_waiters(
                wait_from_user_id = target_user_id,
                wait_target_user_id = from_user_id,
                )

        return ret

    def wait_for_message(self,wait_from_user_id,wait_target_user_id,cursor):

        # waiter 列表清空
        self.refresh_waiters(wait_from_user_id,wait_target_user_id)
        # 查新数据
        session = DBsession()
        new_data = session.query(MessageModel.message_type,MessageModel.message_text,MessageModel.message_url,MessageModel.id)\
                .filter(MessageModel.from_user_id==wait_target_user_id)\
                .filter(MessageModel.target_user_id==wait_from_user_id)
        if cursor:
            new_data = new_data.filter(MessageModel.id > cursor)\
                    .order_by(MessageModel.id.desc())\
                    .all()
        else:
            new_data = new_data.order_by(MessageModel.id.desc())\
                    .all()
        session.close()

        ret_data = [{'message_type': i.message_type, 'message_text': i.message_text,'cursor': i.id} for i in new_data]
        # if future then set result 
        result_future = Future()
        if ret_data:
            result_future.set_result(ret_data)
            return result_future
        # else add future
        foo_dict = {
                    'wait_from_user_id':wait_from_user_id,
                    'wait_target_user_id': wait_target_user_id,
                    'future': result_future,
                    }
        self.waiters.append(foo_dict)
        return result_future

    def refresh_waiters(self,wait_from_user_id,wait_target_user_id):
        self.waiters = [i for i in self.waiters
                        if not
                    (i['wait_target_user_id'] == wait_target_user_id and i['wait_from_user_id'] == wait_from_user_id)]
