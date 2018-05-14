#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

from flask_restful import Resource, request, reqparse
from app.config import Config


class ClearTextHandler(Resource):
    VALID_CLEAR_COMMANDS = ('identity',)

    def __init__(self):
        self.parser = reqparse.RequestParser()
        vc = ', '.join(self.VALID_CLEAR_COMMANDS)
        help_msg = 'Invalid command. These are ok: {}'.format(vc)
        self.parser.add_argument('cmd',
                                 help=help_msg,
                                 required=True,
                                 choices=self.VALID_CLEAR_COMMANDS)

    def get(self):
        args = self.parser.parse_args()
        cmd = args['cmd']
        if cmd == 'identity':
            ret = {'identity': Config.read()['fingerprint']}
        return(ret)


if __name__ == '__main__':
    pass
