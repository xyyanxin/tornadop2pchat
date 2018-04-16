#coding:utf-8
""""
Program: chat
Description: 
Author: XY - mailyanxin@gmail.com
Date: 2018-04-14 03:39:27
Last modified: 2018-04-14 10:59:57
Python release: 3.5.2
"""

import os
import json
import logging

import tornado.web
from tornado import gen

from tornado.options import parse_command_line
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.concurrent import Future

define('server_host', default='0.0.0.0', help='server host')
define('server_port', default=8000, help='server port')
define('mysql_host', default='localhost', help='mysql host')
define('mysql_pwd', default='dddd', help='mysql password')
define('debug', default=True, help='debug')


class MessageBuffer(object):
    def __init__(self):

        '''
        used as global
        {'who': a,'wait_who': b, 'future': Future}
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

        # 2.信息发给相关的future
        waiter = [i for i in self.waiters
                if i['wait_who'] == from_user_id and i['who'] == target_user_id]
        if len(waiter) == 1:
            waiter[0].set_result(messages)
            logging.info('sending to listeners %r', self.waiter)
        elif len(waiter) == 0:
            logging.info('nobody listen')
        else:
            logging.info('error')




    def wait_for_message(self,who,wait_who,cursor):
        result_future = Future()
        if cursor:
            new_data = ''
            # 从mysql中找消息
            if new_data:
                result_future.set_result(new_data)
                return result_future

        foo_dict = {
                    'who':who,
                    'wait_who': wait_who,
                    'future': result_future,
                    }
        self.waiters.append(foo_dict)
        return result_future




global_message_buffer = MessageBuffer()



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', messages= user_message_buffer.cache)


class MessageNewHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body.decode('utf-8')
        params = json.loads(data)

        global_message_buffer.new_messages(
                from_user_id = params['from_user_id'],
                target_user_id = params['target_user_id'],
                data = params['data'],
                )

        ret = {
                'errcode': 0,
                'errmsg': 'ok',
                }
        self.write(ret)

class MessageUpdateHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        data = self.request.body.decode('utf-8')
        params = json.loads(data)

        self.future = global_message_buffer.wait_for_message(
                who = params['from_user_id'],
                wait_who = params['target_user_id'],
                cursor=params.get('cursor',None),
                )
        message = yield self.future
        if self.request.connection.stream.closed():
            self.write('closed')
        self.write(message)


def create_app():
    settings = {
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            'debug': options.debug,
            }

    handler_dispatch = [
            (r"/", MainHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/update", MessageUpdateHandler),
            ]

    app = tornado.web.Application(handler_dispatch, **settings)
    return app

def main():
    parse_command_line()
    app = create_app()
    server = HTTPServer(app)
    server.bind(options.server_port,address=options.server_host)
    server.start(1)
    IOLoop.current().start()

if __name__ == '__main__':
    main()

