import logging

from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    """Catch a RequestException."""

    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response

    except RequestException:
        logging.exception(
            f'An error occurred while loading the page {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Catch a tag search error."""

    searched_tag = soup.find(tag, attrs=(attrs or {}))

    if searched_tag is None:
        error_msg = f'Tag {tag} {attrs} not found'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)

    return searched_tag


def get_soup(session, url):
    """Get Soup :)."""

    response = get_response(session, url)
    response.encoding = 'utf-8'
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    return soup
