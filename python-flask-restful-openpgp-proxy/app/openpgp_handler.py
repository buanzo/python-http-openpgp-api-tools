#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

import sys
import json

from pprint import pprint
from flask_restful import Resource, request
from app.config import Config
from app.crypto import CryptoTools as CT
from app.proxy import proxy_request


class PGPDecoderHandler(Resource):
    def post(self):
        # Here we do all the decryption, verifications
        # and replacements: headers, etc, etc.
        # It doesn't make sense to use before_request to do this
        # because this is a PROXY to an actual RESTful API.
        ret = CT.decrypt_request(request=request)
        real_request = ret['decrypted_request']
        openpgp_data = ret['openpgp_data']
        ret = proxy_request(client_ip=request.remote_addr,
                            real_request=real_request,
                            openpgp_data=openpgp_data)
        # TODO: figure out what to do with proxy_request response object
        # TODO: in terms of openpgp-api protocol
        recipient = openpgp_data['signature_fingerprint']
        openpgp_response = CT.encrypt_response(response=ret,
                                               recipient=recipient)
        return(openpgp_response)


if __name__ == '__main__':
    pass
