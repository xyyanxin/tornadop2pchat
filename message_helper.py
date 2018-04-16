#coding:utf-8
""""
Program: tornadop2pserver
Description: 
Author: XY - mailyanxin@gmail.com
Date: 2018-04-16 02:36:45
Last modified: 2018-04-16 03:07:22
Python release: 3.5.2
"""

import logging
from tornado.concurrent import Future

class MessageBuffer(object):
    def __init__(self):
        '''
        used as global
        {'wait_from_user_id': a,'wait_target_user_id': b, 'future': Future}
        {'from_user_id': a,'target_user_id': b, 'data': message}
        '''
        self.waiters = []
        self.caches = []

    def new_messages(self,from_user_id,data,target_user_id):
        # 1.存消息
        foo_dict = {
                'from_user_id': from_user_id,
                'target_user_id': target_user_id,
                'data': data,
                }
        self.caches.append(foo_dict)
        logging.info('消息存储成功')

        # 2.信息发给相关的future
        waiters = [i for i in self.waiters
                if i['wait_target_user_id'] == from_user_id and i['wait_from_user_id'] == target_user_id]
        if len(waiters) == 1:
            waiters[0]['future'].set_result(data)
            logging.info('sending to online listeners %r', self.waiters)
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


    def wait_for_message(self,wait_from_user_id,wait_target_user_id,cursor):

        self.refresh_waiters(wait_from_user_id,wait_target_user_id)

        result_future = Future()
        if cursor:
            new_data = ''
            # 从mysql中找消息
            if new_data:
                result_future.set_result(new_data)
                return result_future

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
