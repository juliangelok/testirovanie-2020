from urllib.parse import urljoin

import pytest
import requests
import bs4

root_url = "https://www.kinopoisk.ru"


# Test case #0: В названии сайта есть КиноПоиск
def test_homepage_load():
    result = requests.get(root_url)
    assert result.status_code == 200

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert "кинопоиск" in html.title.string.lower()


# Test case #1: Можно найти существующий фильм (RU)
def test_search_existing_film_ru():
    url = urljoin(root_url, '/index.php')
    result = requests.get(url, params={'kp_query': 'Матрица'})
    assert result.status_code == 200

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'Матрица 1999' in html.find("div", {'class': 'element most_wanted'}).text


# Test case #2: Можно найти существующий фильм (EN)
def test_search_existing_film_en():
    url = urljoin(root_url, '/index.php')
    result = requests.get(url, params={'kp_query': 'Matrix'})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'Матрица 1999' in html.find("div", {'class': 'element most_wanted'}).text


# Test case #3: Можно найти существующий сериал
def test_search_existing_series():
    url = urljoin(root_url, '/index.php')
    result = requests.get(url, params={'kp_query': 'Отбросы'})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'Отбросы (сериал) 2009 – 2013' in html.find("div", {'class': 'element most_wanted'}).text


# Test case #4: Можно найти существующую персону
def test_search_existing_person():
    url = urljoin(root_url, '/index.php')
    result = requests.get(url, params={'kp_query': 'Бенедикт Камбербэтч'})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'Бенедикт Камбербэтч 1976' in html.find("div", {'class': 'element most_wanted'}).text


# Test case #5: Нельзя найти что-то несуществующее
def test_search_not_found():
    url = urljoin(root_url, '/index.php')
    result = requests.get(url, params={'kp_query': 'Абвагад ывфр'})
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    assert 'К сожалению, по вашему запросу ничего не найдено...' in html.text


# Test case #6: На странице фильма присутствует название фильма
def test_film_name():
    url = urljoin(root_url, '/film/1143242/')  # Джентельмены
    result = requests.get(url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    header = html.find('div', {'class': 'movie-info__header'}).text
    assert 'Джентльмены' in header
    assert 'The Gentlemen' in header


# Test case #7: На странице фильма присутствует описание фильма
def test_film_description():
    url = urljoin(root_url, '/film/326/')  # Побег из Шоушенка
    result = requests.get(url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    description = html.find('div', {'class': 'film-synopsys'}).text
    assert 'Оказавшись в тюрьме под названием Шоушенк' in description


# Test case #8: На странице фильма присутствует рейтинг фильма
def test_film_rating():
    url = urljoin(root_url, '/film/435/')  # Зеленая Миля
    result = requests.get(url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    rating = float(html.find('span', {'class': 'rating_ball'}).text)
    assert 10.0 > rating > 0.0


# Test case #9: На странице фильма присутствуют отзывы критиков
def test_film_reviews():
    url = urljoin(root_url, '/film/448/')  # Форрест Гамп
    result = requests.get(url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    reviews = html.findAll('div', {'class': 'reviewItem userReview'})
    assert len(reviews) == 10


# Test case #10: На странице фильма можно найти главного актера
def test_film_main_actor():
    url = urljoin(root_url, '/film/397667/')  # Остров проклятых
    result = requests.get(url)
    assert result.status_code == requests.codes.ok

    html = bs4.BeautifulSoup(result.text, 'html.parser')

    actors = html.find('li', {'itemprop': 'actors'}).text
    assert 'Леонардо ДиКаприо' in actors
