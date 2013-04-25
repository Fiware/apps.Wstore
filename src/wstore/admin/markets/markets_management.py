
from urllib2 import HTTPError

from django.conf import settings

from wstore.models import Marketplace
from wstore.market_adaptor.marketadaptor import MarketAdaptor


def get_marketplaces():

    marketplaces = Marketplace.objects.all()
    result = []

    for market in marketplaces:
        result.append({
            'name': market.name,
            'host': market.host
        })

    return result


def register_on_market(name, host, site):

    # Check that the market name is not in use
    existing = True

    try:
        Marketplace.objects.get(name=name)
    except:
        existing = False

    if existing:
        raise Exception('Marketplace name already in use')

    store_name = settings.STORE_NAME

    if host[-1] != '/':
        host += '/'

    marketadaptor = MarketAdaptor(host)

    store_info = {
        'store_name': store_name,
        'store_uri': site,
    }

    try:
        marketadaptor.add_store(store_info)
    except HTTPError:
        raise Exception('Bad Gateway')

    try:
        Marketplace.objects.create(name=name, host=host)
    except Exception, e:
        # If the marketplace model creation fails it is necesary to unregister the store
        # in order to avoid an inconsistent state
        marketadaptor.delete_store(store_name)
        raise e


def unregister_from_market(market):

    marketplace = None
    try:
        marketplace = Marketplace.objects.get(name=market)
    except:
        raise Exception('Not found')

    host = marketplace.host
    if host[-1] != '/':
        host += '/'

    marketadaptor = MarketAdaptor(host)

    try:
        marketadaptor.delete_store(settings.STORE_NAME)
    except HTTPError:
        raise Exception('Bad Gateway')

    marketplace.delete()