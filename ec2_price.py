import json
import logging
import sys
from decimal import Decimal

import click

from utils import get_first_dict_value, get_price_list, get_region_names, wildcard_filter, wildcard_match

log = logging.getLogger(__name__)


def get_instance_on_demand_prices(region, os='Linux', current_only=False):
    prices = {}
    plist = get_price_list(region, 'AmazonEC2')
    for pid, product in plist['products'].items():
        if product.get('productFamily') != 'Compute Instance':
            continue
        attrs = product['attributes']
        if attrs['tenancy'] == 'Host':
            continue
        if attrs['operatingSystem'] != os:
            continue
        if attrs['preInstalledSw'] != 'NA':
            continue
        if attrs['capacitystatus'] != 'Used':  # AllocatedCapacityReservation//UnusedCapacityReservation/Used
            continue
        if current_only and attrs['currentGeneration'] == 'No':
            continue

        price_terms = plist['terms']['OnDemand'][pid]
        first_price_term = get_first_dict_value(price_terms)
        first_price_dimension = get_first_dict_value(first_price_term['priceDimensions'])
        instance_type = attrs['instanceType']
        price = Decimal(first_price_dimension['pricePerUnit']['USD'])
        prices[instance_type] = price
    return prices


def format_data(format, data):
    import pandas as pd

    df = pd.DataFrame(data)
    df: pd.DataFrame = df.pivot(index='instance', columns='region', values='price')
    if format == 'html':
        import seaborn as sns

        colormap = sns.light_palette("orange", as_cmap=True)
        s = df.style.background_gradient(cmap=colormap).set_properties(**{'text-align': 'right'})
        print(s.render(na_rep='-'))
    elif format == 'csv':
        print(df.to_csv(na_rep='-'))


@click.command()
@click.option('-r', '--region', 'regions', multiple=True, required=True, help='region names or wildcard patterns')
@click.option('-t', '--type', 'instance_types', multiple=True, help='instance types or wildcard patterns')
@click.option('--current-only/--no-current-only', default=True, help='current-gen instance types only')
@click.option('--format', type=click.Choice(('csv', 'html', 'json')), default='csv')
def main(regions, instance_types, current_only, format):
    logging.basicConfig(level=logging.INFO)
    region_names = get_region_names()
    regions = set(wildcard_filter(values=region_names, patterns=regions))
    log.info(f'Regions: {regions}')
    data = []
    for region in regions:
        for instance, price in get_instance_on_demand_prices(region, current_only=current_only).items():
            if instance_types and not wildcard_match(instance, instance_types):
                continue
            data.append({'region': region, 'instance': instance, 'price': float(price)})
    if format == 'json':
        json.dump(data, sys.stdout)
        return
    format_data(format, data)


if __name__ == '__main__':
    main()
