import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response, get_soup


def pep(session):
    """Parsing PEP statuses."""

    soup = get_soup(session, PEP_URL)

    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    status_sum = {}
    total_peps = 0

    results = [('Status', 'Amount')]

    for pep in tqdm(tr_tags):

        total_peps += 1

        data = list(find_tag(pep, 'abbr').text)
        preview_status = data[1:][0] if len(data) > 1 else ''

        url = urljoin(PEP_URL, find_tag(pep, 'a', attrs={
            'class': 'pep reference internal'})['href'])
        soup = get_soup(session, url)

        table_info = find_tag(soup, 'dl',
                              attrs={'class': 'rfc2822 field-list simple'})
        status_pep_page = table_info.find(
            string='Status').parent.find_next_sibling('dd').string

        if status_pep_page in status_sum:
            status_sum[status_pep_page] += 1
        if status_pep_page not in status_sum:
            status_sum[status_pep_page] = 1
        if status_pep_page not in EXPECTED_STATUS[preview_status]:
            error_message = (f'Mismatching statuses:\n'
                             f'{url}\n'
                             f'Status in card: {status_pep_page}\n'
                             f'Expected statuses: '
                             f'{EXPECTED_STATUS[preview_status]}')
            logging.warning(error_message)

    for status in status_sum:
        results.append((status, status_sum[status]))
    results.append(('Total', total_peps))

    return results


def whats_new(session):
    """Parsing innovations in Python."""

    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)

    main_div = find_tag(
        soup, 'section', attrs={'id': 'what-s-new-in-python'}
    )

    div_with_ul = find_tag(
        main_div, 'div', attrs={'class': 'toctree-wrapper'}
    )

    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Link to article', 'Title', 'Editor, Author')]

    for section in tqdm(sections_by_python):

        version_a_tag = section.find('a')
        href = version_a_tag['href']

        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        h1 = find_tag(soup, 'h1')
        dl = soup.find('dl').text
        dl_text = dl.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    """Parsing versions of Python."""

    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('List with Python versions not found')

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    results = [('Link to documentation', 'Version', 'Status')]

    for a_tag in a_tags:

        link = a_tag['href']

        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )

    return results


def download(session):
    """Downloading Python archive of python documentation."""

    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)

    main_tag = soup.find('div', {'role': 'main'})
    table_tag = main_tag.find('table', {'class': 'docutils'})

    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'The archive was downloaded and saved: {archive_path}')


MODE_TO_FUNCTION = {
    'pep': pep,
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():

    configure_logging()

    logging.info('Parser started!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Command line arguments: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Parser has completed its work.')


if __name__ == '__main__':
    main()
