# python-http-openpgp-api-tools
A wrapper to python-requests to support openpgp encapsulation, and corresponding server-side proxy code

## Introduction

This repository contains tools and modules that implement the client and
server side of an OpenPGP-encapsulated HTTP API methodology.

The code is insecure, and is a proof of concept that I expect someone might
find useful. It is released for the benefit of the open source and security communities.

When I say it is insecure... don't get me wrong, this is quite useful and relatively secure, and takes measures to read passphrases using different methods, etc. I mean it has NOT been pentested, but it was written with (attempted) security in mind.

## Installation

pip3 install openpgp-requests

## TL;DR I wanna code!

Client: https://github.com/buanzo/python-http-openpgp-api-tools/blob/a5b0eaf4fe100a877537ab264219485f11cfe4f2/python-requests-openpgp-api/openpgpapi.py#L238

Server Config: https://github.com/buanzo/python-http-openpgp-api-tools/blob/master/python-flask-restful-openpgp-proxy/httpbin_proxy.conf

Cheers.
Buanzo.
