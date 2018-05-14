#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>
import json
import requests

from app.config import Config


def proxy_request(client_ip=None, real_request=None, openpgp_data=None):
    if real_request is None or openpgp_data is None or client_ip is None:
        return(None)
    # TODO: validation should be up to the app?
    cfg = Config.read()
    b_url = cfg['backend_url']
    b_port = cfg['backend_port']
    b_base = cfg['backend_base']
    uri = '{}:{}{}'.format(b_url, b_port, b_base)
    url = '{}{}'.format(uri, real_request['url'])

    # We will add OpenPGP-data as json string in
    # this header:
    HEADER = 'X-OpenPGP-Data-JSON-string'
    real_request['headers'][HEADER] = json.dumps(openpgp_data)
    real_request['X-forwarded-for'] = client_ip
    r = requests.request(method=real_request['method'],
                         url=url,
                         data=real_request['data'],
                         headers=real_request['headers'],
                         params=real_request['params'])
    return(r)


if __name__ == '__main__':
    pass
