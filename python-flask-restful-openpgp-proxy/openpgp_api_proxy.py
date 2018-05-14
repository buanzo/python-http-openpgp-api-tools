#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

import os
import sys
import signal
import argparse

from pprint import pprint
from flask import Flask, request
from flask_restful import Api, Resource

from app.cleartext import ClearTextHandler
from app.openpgp_handler import PGPDecoderHandler
from app.flask_encoder import openpgp_repr_func

from app.config import Config
from app.util import to_bool, obtain_passphrase

VERSION = '0.1-insecure-alpha'

#
# SIGHUP signal handler for configuration reload
#


def reload_configuration(signum, frame):
    print("\033[0;34m<SIG> SIGHUP received: reloading configuration file.\n")
    print("Some parameters need restart to be applied.\n\033[0;37m\n")
    Config.reloadConfigFile()

#
# API Routing
#


if __name__ == '__main__':
    defc = '{}/openpgp_api_proxy.conf'.format(os.getcwd())
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        default=defc,
                        help="Config file path ({})".format(defc))
    parser.add_argument("--version",
                        help="Show version and paths",
                        action="store_true")
    parser.add_argument("-D", "--dump",
                        help="Dumps configuration",
                        action="store_true")
    args = parser.parse_args()

    Config.loadConfigFile(filename=args.config)
    cfg = Config.read()
    if args.version:
        print("Version: {}".format(VERSION))
        print("Config file: {}".format(args.config))

    if args.dump:
        pprint(cfg)

    if args.dump or args.version:
        sys.exit(0)

    proxy_app = Flask(__name__)
    api = Api(proxy_app, default_mediatype=cfg['content-type'])
    api.representations[cfg['content-type']] = openpgp_repr_func
    api.add_resource(PGPDecoderHandler, cfg['openpgp-handler-path'],)
    api.add_resource(ClearTextHandler, cfg['clear-handler-path'],)

    # Finally, setup signal handler before entering main loop
    signal.signal(signal.SIGHUP, reload_configuration)
    # TODO: FIX: rework config reload implementation (flask parameters, etc)

    proxy_app.run(host=cfg['host'], port=int(cfg['port']),
                  debug=to_bool(cfg['debug']))
