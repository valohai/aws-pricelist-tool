import fnmatch
import itertools
import json
import os
import time
import logging
from typing import Set

import requests

log = logging.getLogger(__name__)

REGIONS = {
    'ap-northeast-1': 'Asia Pacific (Tokyo)',
    'ap-northeast-2': 'Asia Pacific (Seoul)',
    'ap-northeast-3': 'Asia Pacific (Osaka-Local)',
    'ap-south-1': 'Asia Pacific (Mumbai)',
    'ap-southeast-1': 'Asia Pacific (Singapore)',
    'ap-southeast-2': 'Asia Pacific (Sydney)',
    'ca-central-1': 'Canada (Central)',
    'cn-north-1': 'China (Beijing)',
    'cn-northwest-1': 'China (Ningxia)',
    'eu-central-1': 'EU (Frankfurt)',
    'eu-north-1': 'EU (Stockholm)',
    'eu-west-1': 'EU (Ireland)',
    'eu-west-2': 'EU (London)',
    'eu-west-3': 'EU (Paris)',
    'sa-east-1': 'South America (São Paulo)',
    'us-east-1': 'US East (N. Virginia)',
    'us-east-2': 'US East (Ohio)',
    'us-gov-east-1': 'AWS GovCloud (US-East)',
    'us-gov-west-1': 'AWS GovCloud (US)',
    'us-west-1': 'US West (N. California)',
    'us-west-2': 'US West (Oregon)',
}


def download_or_read_cached_json(url, cache_filename, max_age=86400):
    if os.path.isfile(cache_filename) and (time.time() - os.stat(cache_filename).st_mtime) < max_age:
        log.info(f'Using cached {cache_filename}')
        with open(cache_filename) as infp:
            return json.load(infp)

    log.info(f'Requesting {url}')
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    os.makedirs(os.path.dirname(os.path.realpath(cache_filename)), exist_ok=True)
    with open(cache_filename, 'wb') as outfp:
        outfp.write(resp.content)
    return data


def get_region_names() -> Set[str]:
    return set(REGIONS.keys())


def get_price_list(region, offer):
    return download_or_read_cached_json(
        url=f'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{offer}/current/{region}/index.json',
        cache_filename=f'cache/aws-prices-{region}-{offer}.cache.json',
    )


def get_first_dict_value(d):
    return next(iter(d.values()))


def wildcard_filter(values, patterns):
    return itertools.chain(*((value for value in values if fnmatch.fnmatch(value, pattern)) for pattern in patterns))


def wildcard_match(value, patterns):
    return any(fnmatch.fnmatch(value, pat) for pat in patterns)
