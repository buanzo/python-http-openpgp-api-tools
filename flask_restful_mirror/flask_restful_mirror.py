#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>


from pprint import pprint
from flask import Flask, request
from flask_restful import Api, Resource


class MirrorHandler(Resource):
    def get(self, base):
        print("***** GET={}".format(base))
        pprint(request.headers)
        try:
            js = request.get_json(force=True)
        except Exception:
            js = {}
        finally:
            pprint(js)
        return({'method': 'GET', 'base': base})

    def post(self, base):
        print("***** POST={}".format(base))
        pprint(request.headers)
        try:
            js = request.get_json(force=True)
        except Exception:
            js = {}
        finally:
            pprint(js)
        print("REQUEST.headers = {}".format(request.headers))
        return({'method': 'POST', 'base': base})

    def put(self, base):
        print("***** PUT={}".format(base))
        pprint(request.headers)
        try:
            js = request.get_json(force=True)
        except Exception:
            js = {}
        finally:
            pprint(js)
        return({'method': 'PUT', 'base': base})


mirror_app = Flask(__name__)
api = Api(mirror_app)

#
# API Routing
#

api.add_resource(MirrorHandler, '/<base>')


if __name__ == '__main__':
    mirror_app.run(host='127.0.0.1', debug=True, port=5081)
    # Remember to cleanup here [dbClose(), etc, etc]
