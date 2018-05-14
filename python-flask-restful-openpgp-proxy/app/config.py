#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>
import json


class Config():
    ERR_MSG_NOT_INITIALIZED = {'not_initialized':
                               'please use loadConfigFile()'}
    DEFAULT_SETTINGS = {'content-type': 'application/openpgp-api',
                        'openpgp-handler-path': '/',
                        'clear-handler-path': '/clear',
                        'host': '127.0.0.1',
                        'port': 5080,
                        'debug': 0}
    CONFIG_SETTINGS = {}
    initialized = False

    @classmethod
    def read(cls):
        # Python 3.5+ only. Very cool merging of dicts.
        # http://treyhunner.com/2016/02/how-to-merge-dictionaries-in-python/
        if cls.initialized:
            return({**cls.DEFAULT_SETTINGS, **cls.CONFIG_SETTINGS})
        else:
            return(cls.ERR_MSG_NOT_INITIALIZED)

    @classmethod
    def loadConfigFile(cls, filename):
        with open(filename, 'r') as fp:
            js = json.loads(fp.read())
        cls.filename = filename
        cls.CONFIG_SETTINGS = js
        cls.initialized = True

    @classmethod
    def reloadConfigFile(cls):
        if cls.initialized:
            cls.loadConfigFile(filename=cls.filename)
        else:
            return(cls.ERR_MSG_NOT_INITIALIZED)


if __name__ == '__main__':
    from pprint import pprint
    Config.loadConfigFile(filename='config_sample.json')
    pprint(Config.read())
