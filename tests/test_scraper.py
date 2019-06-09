import requests
from scrapy.http import HtmlResponse, Response

from nobel_winners.nobel_winners.spiders.nwinners_spider import \
    NWinnerSpider, _country, _winner, _wikidata, _wikidata_info

spider = NWinnerSpider()


def fake_response(url: str) -> Response:
    body = bytes(requests.get(url).text, 'UTF-8')
    response = HtmlResponse(url, body=body)
    return response


def test_country():
    response = fake_response('https://en.wikipedia.org/wiki'
                             '/List_of_Nobel_laureates_by_country')
    country, _ = next(_country(response))
    assert country == 'Argentina'


def test_winner():
    response = fake_response('https://en.wikipedia.org/wiki'
                             '/List_of_Nobel_laureates_by_country')
    ol = response.css('h3+ol')[0]
    name, href, category, year = next(_winner(ol))
    print(f'name={name}')
    print(f'href={href}')
    assert name == 'César Milstein'
    assert href == '/wiki/C%C3%A9sar_Milstein'
    assert category == 'Physiology or Medicine'
    assert year == '1984'


def test_wikidata():
    response = fake_response('https://en.wikipedia.org/wiki/C%C3'
                             '%A9sar_Milstein')
    request = next(_wikidata(response))
    assert request.url == 'https://www.wikidata.org/wiki/Special:EntityPage' \
                          '/Q155525'


def test_wikidata_info():
    response = fake_response('https://www.wikidata.org/wiki/Special'
                             ':EntityPage/Q155525')
    winner = next(_wikidata_info(response))
    print(f'\nwinner = {winner}')
    assert winner['gender'] == 'male'
