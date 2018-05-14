#!/usr/bin/env python3
import sys
import gnupg
import json
import requests
import responses
import datetime

from pprint import pprint

class CryptoTools():
    def __init__(self, homedir=None, verify=False, sign=True,
                 my_fingerprint=None, passphrase=None, recv_keys=False,
                 keyserver='hkp://pgp.mit.edu'):
        self.homedir = homedir
        self.verify = verify
        self.sign = sign
        self._gpg = gnupg.GPG(homedir=self.homedir)
        self._gpg.keyserver = keyserver
        self.passphrase = passphrase
        self.public_keys = self._gpg.list_keys()
        self.recv_keys = recv_keys
        self.my_fingerprint = my_fingerprint

    def decrypt(self, msg=None):
        if msg is None:
            raise(ValueError)
        ret = self._gpg.decrypt(msg, always_trust=True,
                                passphrase=self.passphrase)

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

        return({'decrypted_response': str(ret),
                'openpgp_data': odata})

    def encrypt(self, msg=None, recipient=None):
        if msg is None:
            raise(ValueError)
        if recipient is None:
            raise(ValueError)
        if self.validate_recipient(recipient) is False:
            raise(ValueError)
        kwargs = {}
        if self.my_fingerprint is not None and self.passphrase is not None:
            kwargs['default_key'] = self.my_fingerprint
            kwargs['passphrase'] = self.passphrase  # TODO: securify
        e = self._gpg.encrypt(msg, recipient, **kwargs)
        return(e)

    def validate_recipient(self, recipient):
        pks = self._gpg.list_keys()
        found = False
        for key in pks:
            if key['fingerprint'] == recipient:
                found = True
                break
        if self.recv_keys is True and found is False:
            print("Getting key {} from {}".format(recipient,
                                                  self._gpg.keyserver))
            x = self._gpg.recv_keys(recipient)
            if recipient in x.fingerprints:
                found = True
        return(found)


class OpenPGPApiRequest():
    CONTENT_TYPE = 'application/openpgp-api'
    USER_AGENT = 'python-openpgp-api-request/0.1'

    def __init__(self, server='localhost', port=5080, endpoint='/',
                 recipient=None, sign=False, homedir=None,
                 verify=False, ssl=False, auto_recv_keys=True,
                 my_fingerprint=None, passphrase=None):
        # FIX/RFC: should I self.session = requests.session() or something
        # like it?  maybe it's own method...
        self.method = 'POST'
        if ssl:
            self.protocol = 'https'
            self.verify = verify
        else:
            self.protocol = 'http'
            self.verify = None
        self.server = server
        self.port = port
        if endpoint.startswith('/'):
            self.endpoint = endpoint
        else:
            self.endpoint = '/{}'.format(endpoint)
        self.target = '{}://{}:{}{}'.format(self.protocol,
                                            self.server,
                                            self.port,
                                            self.endpoint)

        if recipient is None:
            self.get_server_identity()
        else:
            self.recipient = recipient
        self.sign = sign

        self.crypto = CryptoTools(homedir=homedir,
                                  recv_keys=auto_recv_keys,
                                  my_fingerprint=my_fingerprint,
                                  passphrase=passphrase)

    def get_server_identity(self):
        cr = self._clear_request(cmd='identity')
        if 'identity' in cr:
            # TODO: VALIDATE
            self.recipient = cr['identity']
        else:
            self.recipient = None

    def get_server_trust(self):
        cr = self._signed_request(cmd='trust')
        pprint(cr)

    def head(self, url=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='GET',
                                 url=url,
                                 params=params, **kwargs)
        return(r)
        # TODO: extract path, params, then pgpapi-ize and send

    def get(self, url=None, params=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='GET',
                                 url=url,
                                 params=params, **kwargs)
        return(r)

    def post(self, url=None, data=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='POST',
                                 url=url,
                                 data=data, **kwargs)
        return(r)

    def put(self, url=None, data=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='PUT', url=url, data=data, **kwargs)
        return(r)

    def patch(self, url=None, data=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='PATCH', url=url, data=data, **kwargs)
        return(r)

    def delete(self, url=None, **kwargs):
        if url is None:
            return(None)
        r = self._pgpapi_request(method='DELETE', url=url, **kwargs)
        return(r)

    def _clear_request(self, cmd=None):
        if cmd is None:
            raise(ValueError)
        url = '{}clear'.format(self.target)
        r = requests.get(url, params={'cmd': cmd})
        return(r.json())

    def _pgpapi_request(self, method=None, url=None,
                        params=None, data=None, **kwargs):

        if self.recipient is None:
            raise(ValueError)  # TODO: create custom exception

        # encrypted_data must include all things that should not be visible:
        # headers, data/params, real api url, method, etc

        # add content-type: application/openpgp-api
        # Now we need to build encrypted_data. We are encapsulating, depending
        # on method: url, params/data, headers, etc.
        capsule = {}
        try:
            isonow = datetime.datetime.utcnow().isoformat()
            capsule['request_utc_datetime'] = isonow
            capsule['method'] = method
            capsule['url'] = url
            capsule['params'] = json.dumps(params)
            capsule['data'] = json.dumps(data)
            capsule['headers'] = kwargs['headers']
            del(kwargs['headers'])
        except Exception:
            pass
        json_capsule = json.dumps(capsule)
        encrypted_data = str(self.crypto.encrypt(msg=json_capsule,
                                                 recipient=self.recipient))
        local_headers = {'Content-Type': OpenPGPApiRequest.CONTENT_TYPE,
                         'User-Agent': OpenPGPApiRequest.USER_AGENT,
                         'Accept': self.CONTENT_TYPE, }
        r = requests.request(method=self.method, url=self.target,
                             data=encrypted_data,
                             stream=False,
                             headers=local_headers,
                             verify=self.verify, **kwargs)
        # TODO: implement decrypt_response(r)
        dr = self.crypto.decrypt(r.content)
        decrypted = json.loads(dr['decrypted_response'])
        odata = dr['openpgp_data']
        body = json.loads(decrypted['content'])
        status = decrypted['status']
        headers = json.loads(decrypted['headers'])
        HEADER = 'X-OpenPGP-Data-JSON-string'
        headers[HEADER] = json.dumps(odata)
        resp = responses.Response(method=method,
                                  url=url,
                                  body=body,
                                  status=status,
                                  content_type=headers['Content-Type'],
                                  headers=headers)
        resp.body = resp.body.decode('utf-8')
        return(resp)
        # TODO: add self.sign check to encrypted_data

# TODO: add headers, cookies, auth, timeout, proxies, verify
# http://docs.python-requests.org/en/master/api/

# Encryption: https://pythonhosted.org/gnupg/gnupg.html


def test_openpgp_api_server():
    # This is a test method, hardcoded and horrible
    fpr = 'AFINGERPRINTHERE'
    h = '/path/to/keyring/folder/containing/that/fpr'
    x = OpenPGPApiRequest(homedir=h,
                          my_fingerprint=fpr,
                          passphrase='the_passphrase')
    z = x.get(url='get', headers={'X-extra-header': 'wow'})
    print(z.body)
    z = x.get(url='tuvieja',
              headers={'X-header': 'X-value-get'})
    print(z.body)
    z = x.post(url='tuotravieja',
               headers={'X-header': 'X-value-post'},
               data={'data': 'dataaaaa en post'})
    print(z.body)
    z = x.put(url='cuac',
              headers={'X-header': 'X-value-put'},
              data={'data': 'dataaaaa en put'})
    print(z.body)


if __name__ == '__main__':
    test_openpgp_api_server()
