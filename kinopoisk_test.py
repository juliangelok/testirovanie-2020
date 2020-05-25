import sys
from urllib.parse import urljoin
from dataclasses import dataclass

import pytest
import requests
import bs4

root_url = "https://www.kinopoisk.ru"


@dataclass
class Actor:
    name: str
    url: str = ''


@dataclass
class Film:
    name: str
    name_en: str
    description: str
    actor: Actor
    url: str = ''


actors_list = [
    Actor('Киану Ривз'),
    Actor('Мэттью МакКонахи'),
    Actor('Питер Динклэйдж'),
    Actor('Нэйтан Стюарт-Джарретт'),
]

films_list = [
    Film('Матрица', 'Matrix', 'Жизнь Томаса Андерсона разделена на', actors_list[0]),
    Film('Джентльмены', 'The Gentlemen', 'Один ушлый американец ещё со', actors_list[1]),
]

series_list = [
    Film('Отбросы', 'Misfits', 'Келли, Нейтан, Кертис, Алиша и Саймон выполняют', actors_list[2]),
    Film('Игра престолов', 'Game of Thrones', 'К концу подходит время благоденствия', actors_list[3]),
]


@pytest.fixture
def session():
    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/39.0.2171.95 Safari/537.36',
    }

    # Получить все куки
    session.get(root_url)
    return session


@pytest.fixture(params=actors_list)
def actor(request):
    cur: Actor = request.param

    session = requests.Session()
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': cur.name})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')
    top_result = html.find('div', {'class': 'element most_wanted'})
    assert cur.name in top_result.text

    actor_href = top_result.find('div', {'class': 'info'}).find('a', {'data-type': 'person'})['data-url']
    cur.url = urljoin(root_url, actor_href)
    return cur


@pytest.fixture(params=films_list)
def film(request):
    cur: Film = request.param

    session = requests.Session()
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': cur.name})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')
    top_result = html.find('div', {'class': 'element most_wanted'})
    assert cur.name in top_result.text

    film_href = top_result.find('div', {'class': 'info'}).find('a', {'data-type': 'film'})['data-url']
    cur.url = urljoin(root_url, film_href)
    return cur


@pytest.fixture(params=series_list)
def series(request):
    cur: Film = request.param

    session = requests.Session()
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': cur.name})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')
    top_result = html.find('div', {'class': 'element most_wanted'})

    film_href = top_result.find('div', {'class': 'info'}).find('a', {'data-type': 'series'})['data-url']
    cur.url = urljoin(root_url, film_href)
    return cur


# Test case #0: В названии сайта есть КиноПоиск
def test_homepage_load(session):
    result = session.get(root_url)
    assert result.status_code == 200

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert "кинопоиск" in html.title.string.lower()


# Test case #1: Можно найти существующий фильм (RU)
def test_search_existing_film_ru(session, film):
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': film.name})
    assert result.status_code == 200

    html = bs4.BeautifulSoup(result.text, 'html.parser')
    text = html.find("div", {'class': 'element most_wanted'}).text
    sys.stderr.write(text)
    assert film.name in text


# Test case #2: Можно найти существующий фильм (EN)
def test_search_existing_film_en(session, film):
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': film.name_en})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert film.name in html.find("div", {'class': 'element most_wanted'}).text


# Test case #3: Можно найти существующий сериал
def test_search_existing_series(session, series):
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': series.name})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert series.name in html.find("div", {'class': 'element most_wanted'}).text


# Test case #4: Можно найти существующую персону
def test_search_existing_person(session, actor):
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': actor.name})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert actor.name in html.find("div", {'class': 'element most_wanted'}).text


# Test case #5: Нельзя найти что-то несуществующее
def test_search_not_found(session):
    url = urljoin(root_url, '/index.php')
    result = session.get(url, params={'kp_query': 'Абвагад ывфр'})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'К сожалению, по вашему запросу ничего не найдено...' in html.text


# Test case #6: На странице фильма присутствует название фильма
def test_film_name(session, film):
    result = session.get(film.url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    header = html.find('div', {'class': 'movie-info__header'}).text
    assert film.name in header
    assert film.name_en in header


# Test case #7: На странице фильма присутствует описание фильма
def test_film_description(session, film):
    result = session.get(film.url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    description = html.find('div', {'class': 'film-synopsys'}).text
    assert film.description in description


# Test case #8: На странице фильма присутствует рейтинг фильма
def test_film_rating(session, film):
    result = session.get(film.url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    rating = float(html.find('span', {'class': 'rating_ball'}).text)
    assert 10.0 > rating > 0.0


# Test case #9: На странице фильма присутствуют отзывы критиков
def test_film_reviews(session, film):
    result = session.get(film.url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    reviews = html.findAll('div', {'class': 'reviewItem userReview'})
    assert len(reviews) == 10


# Test case #10: На странице фильма можно найти главного актера
def test_film_main_actor(session, film):
    result = session.get(film.url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    actors = html.find('li', {'itemprop': 'actors'}).text
    assert film.actor.name in actors


# Test case #11: Найти актера, выбрать его фильм и убедиться, что актер есть в списке актеров
def test_actor_reverse_lookup(session, actor):
    # Найти фильм
    result_actor = session.get(actor.url)
    assert result_actor.status_code == requests.codes.ok

    html_actor = bs4.BeautifulSoup(result_actor.text, 'html.parser')
    film_href = html_actor. \
        find('div', {'class': 'personPageItems', 'data-work-type': 'actor'}). \
        findAll('div', {'class': 'item'})[2]. \
        find('table'). \
        find('a')['href']

    film_url = urljoin(root_url, film_href)

    # Найти актера на странице фильма
    film_result = requests.get(film_url)
    assert film_result.status_code == requests.codes.ok
    film_html = bs4.BeautifulSoup(film_result.text, 'html.parser')
    actors = ''.join(map(str, film_html.findAll('li', {'itemprop': 'actors'})))
    assert actor.name in actors
