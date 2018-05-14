#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>
import gnupg
import json
import sys

from app.config import Config
from app.util import obtain_passphrase as passphrase


class CryptoTools():
    _initialized = False

    @classmethod
    def get_homedir(cls):
        return(Config.read()['keyring_location'])

    @classmethod
    def get_gpg(cls):
        gpg = gnupg.GPG(homedir=cls.get_homedir())
        return(gpg)

    @classmethod
    def encrypt_response(cls, response=None, recipient=None):

        if response is None or recipient is None:
            return(None)

        gpg = cls.get_gpg()

        capsule = {}
        capsule['headers'] = json.dumps(dict(response.headers))
        capsule['cookies'] = json.dumps(dict(response.cookies))
        capsule['content'] = json.dumps(response.content.decode('utf-8'))
        capsule['status'] = response.status_code
        json_capsule = json.dumps(capsule)

        kwargs = {}
        kwargs['default_key'] = Config.read()['fingerprint']
        kwargs['passphrase'] = passphrase()

        msg = json_capsule
        encrypted_data = gpg.encrypt(msg, recipient, **kwargs)
        return(str(encrypted_data))

    @classmethod
    def decrypt_request(cls, request=None):
        if request is None:
            return(None)
        gpg = cls.get_gpg()
        ret = gpg.decrypt(request.data,
                          always_trust=True,
                          passphrase=passphrase())
        # TODO: should we create a Request object?
        retObj = json.loads(str(ret))
        if 'params' in retObj.keys():
            retObj['params'] = json.loads(retObj['params'])
        if 'data' in retObj.keys():
            retObj['data'] = json.loads(retObj['data'])

        # This dictionary holds OpenPGP information obtained off
        # the openpgp-api POST request body. It will get appended
        # to a header, in json.dumps() format, for the origins
        # to use.
        odata = {}
        odata['signature_fingerprint'] = ret.fingerprint
        odata['signature_pubkey_fingerprint'] = ret.pubkey_fingerprint
        odata['signature_keyid'] = ret.key_id
        odata['creation_date'] = ret.creation_date
        odata['timestamp'] = ret.timestamp
        odata['sig_timestamp'] = ret.sig_timestamp
        odata['username'] = ret.username
        odata['expire_timestamp'] = ret.expire_timestamp
        odata['trust_level'] = ret.trust_level
        odata['trust_text'] = ret.trust_text
        odata['notations'] = ret.notations

        return({'decrypted_request': retObj,
                'openpgp_data': odata})


if __name__ == '__main__':
    pass
