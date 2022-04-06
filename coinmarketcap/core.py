#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import tempfile
from typing import Optional

import requests_cache


class Market(object):

    __PRO_V1_BASE_URL = "https://pro-api.coinmarketcap.com/v1/"
    __PRO_V2_BASE_URL = "https://pro-api.coinmarketcap.com/v2/"
    __TEST_V1_BASE_URL = "https://sandbox-api.coinmarketcap.com/v1/"
    __TEST_V2_BASE_URL = "https://sandbox-api.coinmarketcap.com/v2/"
    _session = None
    __DEFAULT_TIMEOUT = 30
    __TEMPDIR_CACHE = True

    def __init__(
        self,
        api_key: Optional[str] = None,
        request_timeout=__DEFAULT_TIMEOUT,
        tempdir_cache=__TEMPDIR_CACHE,
    ):
        if not api_key:
            api_key = "secret"
            self.v1_base_url = self.__TEST_V1_BASE_URL
            self.v2_base_url = self.__TEST_V2_BASE_URL
        else:
            self.v1_base_url = self.__PRO_V1_BASE_URL
            self.v2_base_url = self.__PRO_V2_BASE_URL
        self.api_key = api_key
        self.request_timeout = request_timeout
        self.cache_filename = "coinmarketcap_cache"
        self.cache_name = (
            os.path.join(tempfile.gettempdir(), self.cache_filename)
            if tempdir_cache
            else self.cache_filename
        )

    @property
    def session(self):
        if not self._session:
            self._session = requests_cache.CachedSession(
                cache_name=self.cache_name, backend="sqlite", expire_after=120
            )
            self._session.headers.update(
                {"Accepts": "application/json", "X-CMC_PRO_API_KEY": self.api_key}
            )
        return self._session

    def __request(self, endpoint, params):
        response_object = self.session.get(
            endpoint, params=params, timeout=self.request_timeout
        )

        try:
            response = json.loads(response_object.text)

            if isinstance(response, list) and response_object.status_code == 200:
                response = [
                    dict(item, **{"cached": response_object.from_cache})
                    for item in response
                ]
            if isinstance(response, dict) and response_object.status_code == 200:
                response["cached"] = response_object.from_cache

        except Exception as e:
            return e

        return response