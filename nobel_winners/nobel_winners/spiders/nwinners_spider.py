import logging

import scrapy
from scrapy import Request
from scrapy.http import Response

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s',
                    datefmt='%b %d - %H:%M:%S',
                    handlers=[  # logging.FileHandler(f'{__file__}.log'),
                        logging.StreamHandler()])
logger = logging.getLogger(__file__)

BASE_URL = 'https://en.wikipedia.org'


class NWinnerItem(scrapy.Item):
    country = scrapy.Field()
    category = scrapy.Field()
    year = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    date_of_birth = scrapy.Field()
    date_of_death = scrapy.Field()
    place_of_birth = scrapy.Field()
    place_of_death = scrapy.Field()
    gender = scrapy.Field()


class NWinnerSpider(scrapy.Spider):
    name = 'nwinners'
    allowed_domains = ['en.wikipedia.org']
    start_urls = [BASE_URL + '/wiki/List_of_Nobel_laureates_by_country', ]

    def parse(self, response: Response):
        for (country, ol) in _country(response):
            for (name, href, category, year) in _winner(ol):
                request = Request(BASE_URL + href, callback=_wikidata,
                                  dont_filter=True)
                request.meta['winner'] = {'name': name, 'country': country,
                                          'link': href, 'category': category,
                                          'year': year}
                yield request


def _country(response: Response):
    h3s = response.css('h3')
    ols = response.css('h3+ol')
    for h3, ol in zip(h3s, ols):
        country = h3.css('span.mw-headline::text').get()
        if country:
            yield (country, ol)


def _winner(ol):
    for li in ol.css('li'):
        name = li.css('a::text').get()
        href = li.css('a::attr(href)').get()
        category = li.re_first(r'Physiology or Medicine|Economics|Physics'
                               r'|Peace|Chemistry|Literature')
        year = li.re_first(r'\d{4}')
        yield (name, href, category, year)


def _wikidata(response: Response):
    href = response.css('li#t-wikibase>a::attr(href)').get()
    request = Request(href, callback=_wikidata_info, dont_filter=True)
    request.meta['winner'] = response.meta['winner']
    yield request


def _wikidata_info(response: Response):
    property_codes = [
        {'name': 'date_of_birth', 'code': 'P569'},
        {'name': 'date_of_death', 'code': 'P570'},
        {'name': 'place_of_birth', 'code': 'P19', 'link': True},
        {'name': 'place_of_death', 'code': 'P20', 'link': True},
        {'name': 'gender', 'code': 'P21', 'link': True}
    ]
    winner_info = {}
    for prop in property_codes:
        if prop.get('link'):
            sel = response.css(f'#{prop["code"]} .wikibase-snakview-value'
                               f' a::text')
        else:
            sel = response.css(f'#{prop["code"]} .wikibase-snakview-value'
                               f'::text')
        if sel:
            if not sel.get():
                print(f'No field {prop["name"]} for {response.url}')
            winner_info[prop['name']] = sel.extract_first()
    yield NWinnerItem(**winner_info, **response.meta['winner'])
