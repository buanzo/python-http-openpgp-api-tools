#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

import os
from app.config import Config


def to_bool(value):
    if str(value).lower() in ("y", "yes", "true",  "1", "please", "42"):
        return True
    if str(value).lower() in ("n",  "no", "false", "0", "khaaaan", ""):
        return False
    raise Exception('Could not convert "{}" to boolean.'.format(str(value)))


def obtain_passphrase():
    VALID_METHODS = ('config', 'environment', 'file',)
    cfg = Config.read()
    method = None
    source = None
    passphrase = None
    if 'passphrase_method' not in cfg:
        raise ValueError
    if 'passphrase_source' not in cfg:
        raise ValueError
    method = cfg['passphrase_method']
    source = cfg['passphrase_source']
    if method not in VALID_METHODS:
        v = ', '.join(VALID_METHODS)
        print("Invalid passphrase_method. Must be one of {}".format(v))
        raise ValueError
    if method == 'config':
        if source not in cfg:
            print('Missing required configuration key "{}"'.format(source))
            raise ValueError
        passphrase = cfg[source]
    elif method == 'environment':
        if source not in os.environ:
            print('Missing required environment variable "{}"'.format(source))
        passphrase = os.environ[source]
    elif method == 'file':
        try:
            with open(source) as fp:
                passphrase = fp.read().strip()
        except Exception:
            print('Cannot read passphrase file source "{}"'.format(source))
    return(passphrase)


if __name__ == '__main__':
    pass
