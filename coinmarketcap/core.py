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

    def cryptocurrency_listings_latest(
        self,
        start: int = 1,
        limit: int = 100,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        market_cap_min: Optional[int] = None,
        market_cap_max: Optional[int] = None,
        volume_24h_min: Optional[int] = None,
        volume_24h_max: Optional[int] = None,
        circulating_supply_min: Optional[int] = None,
        circulating_supply_max: Optional[int] = None,
        percent_change_24h_min: Optional[int] = None,
        percent_change_24h_max: Optional[int] = None,
        convert: Optional[str] = None,
        convert_id: Optional[str] = None,
        sort: str = "market_cap",
        sort_dir: str = "desc",
        cryptocurrency_type: str = "all",
        tag: str = "all",
        aux: str = "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply",
    ):
        """
        Returns a paginated list of all active cryptocurrencies with latest market data.

	Parameters
	----------
        start : int (Default: 1)
		Optionally offset the start (1-based index) of the paginated list of items to return.
		>=1
        limit : int (Default: 100)
		Optionally specify the number of results to return.
		Use this parameter and the "start" parameter to determine your own pagination size.
		[1..5000]
        price_min : Optional[int] (Default: None)
		Optionally specify a threshold of minimum USD price to filter results by.
		[0..100000000000000000]
        price_max : Optional[int] (Default: None)
		Optionally specify a threshold of maximum USD price to filter results by.
		[0..100000000000000000]
        market_cap_min : Optional[int] (Default: None)
		Optionally specify a threshold of minimum market cap to filter results by.
		[0..100000000000000000]
        market_cap_max : Optional[int] (Default: None)
		Optionally specify a threshold of maximum market cap to filter results by.
		[0..100000000000000000]
        volume_24h_min : Optional[int] (Default: None)
		Optionally specify a threshold of minimum 24 hour USD volume to filter results by.
		[0..100000000000000000]
        volume_24h_max : Optional[int] (Default: None)
		Optionally specify a threshold of maximum 24 hour USD volume to filter results by.
		[0..100000000000000000]
        circulating_supply_min : Optional[int] (Default: None)
		Optionally specify a threshold of minimum circulating supply to filter results by.
		[0..100000000000000000]
        circulating_supply_max : Optional[int] (Default: None)
		Optionally specify a threshold of maximum circulating supply to filter results by.
		[0..100000000000000000]
        percent_change_24h_min : Optional[int] (Default: None)
		Optionally specify a threshold of minimum 24 hour percent change to filter results by.
		>=-100
        percent_change_24h_max : Optional[int] (Default: None)
		Optionally specify a threshold of maximum 24 hour percent change to filter results by.
		>=-100
        convert : Optional[str] (Default: None)
		Optionally calculate market quotes in up to 120 currencies at once by passing
		a comma-separated list of cryptocurrency or fiat currency symbols.
		Each additional convert option beyond the first requires an additional call credit.
		A list of supported fiat options can be found here. Each conversion is returned in its own "quote" object.
        convert_id : Optional[str] (Default: None)
		Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
		This option is identical to convert outside of ID format.
		Ex: convert_id=1,2781 would replace convert=BTC,USD in your query.
		This parameter cannot be used when convert is used.
        sort : str (Default: "market_cap")
		What field to sort the list of cryptocurrencies by.
		{"name", "symbol", "date_added", "market_cap", "market_cap_strict", "price",
		 "circulating_supply", "total_supply", "max_supply", "num_market_pairs", "volume_24h", "percent_change_1h",
		 "percent_change_24h", "percent_change_7d", "market_cap_by_total_supply_strict", "volume_7d", "volume_30d"}
        sort_dir : str (Default: "desc")
		The direction in which to order cryptocurrencies against the specified sort.
		{"asc", "desc"}
        cryptocurrency_type : str (Default: "all")
		The type of cryptocurrency to include.
		{"all", "coins", "tokens"}
        tag : str (Default: "all")
		The tag of cryptocurrency to include.
		{"all", "defi", "filesharing"}
        aux : str (Default: "num_market_pairs,cmc_rank,date_added,tags,platform,max_supply,circulating_supply,total_supply")
		Optionally specify a comma-separated list of supplemental data fields to return.

	Returns
	-------
        Server response as dictionary.
        """
        params = {}
        params.update({"start": start})
        params.update({"limit": limit})
        params.update({"sort": sort})
        params.update({"sort_dir": sort_dir})
        params.update({"cryptocurrency_type": cryptocurrency_type})
        params.update({"tag": tag})
        params.update({"aux": aux})
        if price_min:
            params.update({"price_min": price_min})
        if price_max:
            params.update({"price_max": price_max})
        if market_cap_min:
            params.update({"market_cap_min": market_cap_min})
        if market_cap_max:
            params.update({"market_cap_max": market_cap_max})
        if volume_24h_min:
            params.update({"volume_24h_min": volume_24h_min})
        if volume_24h_max:
            params.update({"volume_24h_max": volume_24h_max})
        if circulating_supply_min:
            params.update({"circulating_supply_min": circulating_supply_min})
        if circulating_supply_max:
            params.update({"circulating_supply_max": circulating_supply_max})
        if percent_change_24h_min:
            params.update({"percent_change_24h_min": percent_change_24h_min})
        if percent_change_24h_max:
            params.update({"percent_change_24h_max": percent_change_24h_max})
        if convert:
            params.update({"convert": convert})
        if convert_id:
            params.update({"convert_id": convert_id})
        response = self.__request(
            self.v1_base_url + "cryptocurrency/listings/latest", params=params
        )
        return response

    def global_metrics_quotes_latest(
        self,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        convert: Optional[str] = None,
        convert_id: Optional[str] = None,
        # aux: str = "num_market_pairs,traffic_score,rank,exchange_score,liquidity_score,effective_liquidity_24h", # The API docs say this should work but it complains in the response ¯\_(ツ)_/¯
    ):
        """
        Fetch the latest aggregate market data for 1 or more exchanges.
        Use the "convert" option to return market values in multiple fiat and cryptocurrency conversions in the same call.

        Parameters
        ----------
        id : Optional[str] (Default: None)
                One or more comma-separated CoinMarketCap exchange IDs. Example: "1,2"
        slug : Optional[str] (Default: None)
                Alternatively, pass a comma-separated list of exchange "slugs" (URL friendly all
                lowercase shorthand version of name with spaces replaced with hyphens).
                Example: "binance,gdax". At least one "id" or "slug" is required.
        convert : Optional[str] (Default: None)
                By default market quotes are returned in USD.
                Optionally calculate market quotes in up to 3 other fiat currencies
                or cryptocurrencies.
        convert_id : Optional[str] (Default: None)
                Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                This option is identical to convert outside of ID format.
                Ex: convert_id=1,2781 would replace convert=BTC,USD in your query.
                This parameter cannot be used when convert is used.
        #THIS SHOULD WORK BUT DOES NOT aux : str (Default: "num_market_pairs,traffic_score,rank,exchange_score,liquidity_score,effective_liquidity_24h")
        #        Optionally specify a comma-separated list of supplemental data fields to return.

        Returns
        -------
        Server response as dictionary.
        """
        params = {}
        # params.update({"aux": aux})
        if id:
            params.update({"id": id})
        if slug:
            params.update({"slug": slug})
        if convert:
            params.update({"convert": convert})
        if convert_id:
            params.update({"convert_id": convert_id})
        response = self.__request(
            self.v1_base_url + "global-metrics/quotes/latest", params
        )
        return response

    def global_metrics_quotes_historical(
        self,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: int = 10,
        interval: str = "1d",
        convert: Optional[str] = None,
        convert_id: Optional[str] = None,
        aux: str = "btc_dominance,active_cryptocurrencies,active_exchanges,active_market_pairs,total_volume_24h,total_volume_24h_reported,altcoin_market_cap,altcoin_volume_24h,altcoin_volume_24h_reported",
    ):
        """
        Fetch an interval of historical global cryptocurrency market metrics based on time and interval parameters.

        Parameters
        ----------
        time_start : Optional[str] (Default: None)
                Timestamp (Unix or ISO 8601) to start returning quotes for.
                Optional, if not passed, we'll return quotes calculated in
                reverse from "time_end".
        time_end : Optional[str] (Default: None)
                Timestamp (Unix or ISO 8601) to stop returning quotes for (inclusive).
                Optional, if not passed, we'll default to the current time.
                If no "time_start" is passed, we return quotes in reverse order
                starting from this time.
        count : int (Default: 10)
                The number of interval periods to return results for.
                Optional, required if both "time_start" and "time_end" aren't supplied.
                The default is 10 items. The current query limit is 10000.
        interval : str (Default "1d")
                Interval of time to return data points for.
                {"hourly", "daily", "weekly", "monthly", "yearly",
                 "5m", "10m", "15m", "30m", "45m",
                 "1h", "2h", "3h", "4h", "6h", "12h",
                 "1d", "2d", "3d", "7d", "14d", "15d", "30d", "60d", "90d", "365d"}
        convert : Optional[str] (Default: None)
                By default market quotes are returned in USD.
                Optionally calculate market quotes in up to 3 other fiat currencies
                or cryptocurrencies.
        convert_id : Optional[str] (Default: None)
                Optionally calculate market quotes by CoinMarketCap ID instead of symbol.
                This option is identical to convert outside of ID format.
                Ex: convert_id=1,2781 would replace convert=BTC,USD in your query.
                This parameter cannot be used when convert is used.
        aux : str (Default: "btc_dominance,active_cryptocurrencies,active_exchanges,active_market_pairs,total_volume_24h,total_volume_24h_reported,altcoin_market_cap,altcoin_volume_24h,altcoin_volume_24h_reported")
                Optionally specify a comma-separated list of supplemental data fields to return

        Returns
        -------
        Server response as dictionary.

        Notes
        -----
        - A historic quote for every "interval" period between your "time_start" and "time_end" will be returned.
        - If a "time_start" is not supplied, the "interval" will be applied in reverse from "time_end".
        - If "time_end" is not supplied, it defaults to the current time.
        - At each "interval" period, the historic quote that is closest in time to the requested time will be returned.
        - If no historic quotes are available in a given "interval" period up until the next interval period, it will be skipped.
        """
        params = {}
        params.update({"count": count})
        params.update({"interval": interval})
        params.update({"aux": aux})
        if time_start:
            params.update({"time_start": time_start})
        if time_end:
            params.update({"time_end": time_end})
        if convert:
            params.update({"convert": convert})
        if convert_id:
            params.update({"convert_id": convert_id})
        response = self.__request(
            self.v1_base_url + "global-metrics/quotes/historical", params
        )
        return response
