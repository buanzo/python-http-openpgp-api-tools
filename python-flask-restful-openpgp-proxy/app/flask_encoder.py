#!/usr/bin/env python3
from flask import make_response
from app.crypto import CryptoTools as CT


def openpgp_repr_func(data, code, headers):
    resp = make_response(str(data))
    resp.headers.extend(headers or {})
    return(resp)


if __name__ == '__main__':
    pass
