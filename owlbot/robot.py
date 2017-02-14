# -*- coding: utf-8 -*-

import requests


def request(method, url, headers={}, data=None):
    result = getattr(requests, method.lower())(url, headers=headers, data=data, stream=True)
    return result
