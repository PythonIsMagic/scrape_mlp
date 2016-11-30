# coding=utf-8
"""
  " Tools for scraping with requests, BeautifulSoup, urllib, and Selenium
  """

from bs4 import BeautifulSoup
import csv
import os
import re
import requests
import time

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

DELAY = 2  # Seconds
DATADIR = "data/"
PAGEDIR = "pages/"

HEADER_MOZ1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5)'}
HEADER_MOZ2 = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) \
               AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
               "Accept": "text/html,application/xhtml+xml,application/xml;\
               q=0.9,image/webp,*/*;q=0.8"}


def saved_html_name(url):
    """ Converts a URL to a safe filename. """
    parsed = urlparse(url)
    filename = parsed.netloc + parsed.path + parsed.query
    if not filename.endswith('.html'):
        filename += '.html'

    # We cannot use '/' in our names - conflicts with Linux. Use '__' instead.
    filename = filename.replace('/', '__')
    return filename


def get_soup(html):
    """ Get the Beautiful Soup tree from HTML. """
    #  return BeautifulSoup(req.content, "html.parser")
    #  return BeautifulSoup(req.text, "html5lib")  # Haven't tested this yet
    return BeautifulSoup(html, "html.parser")


def get_request(url, headers=None):
    """ Requests a URL and returns the HTML as text. """
    time.sleep(DELAY)  # Be polite! ;)

    try:
        # req = requests.get(url)
        # req.headers = headers
        if headers:
            req = requests.get(url, headers=headers)
        else:
            req = requests.get(url)
    except requests.exceptions.InvalidURL as e:
        print('Invalid URL: {}'.format(e))

        return None

    if req.ok:
        print(type(req.text))
        return req.text
    else:
        print('Request unsuccessful with code: {}'.format(req.status_code))
        return None


def save_html(url, html, path=PAGEDIR):
    """ Save the given URL as a HTML file on the drive. Returns the path to the file."""
    ensure_dir(path)
    filename = path + saved_html_name(url)

    # Don't overwrite...
    if os.path.exists(filename):
        return filename

    with open(filename, 'w') as f:
        f.write(html.encode('utf-8'))
    return filename


def load_html(url, path=PAGEDIR):
    """ Check if we have the page saved on disk and returns the HTML text,
        returns None if it wasn't found.
    """
    filename = path + saved_html_name(url)

    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.read()
    else:
        return None


def handle_url(url, path=PAGEDIR):
    """ Checks if the URL exists as a saved html file, and returns it's soup.
        If we don't have it, we download it and save it. And return it's soup.

        timestamp - useful if we want to keep checking updated versions.
        overwrite - if we always want the newest ver.
    """

    html = load_html(url, path)

    if not html:
        # print('Downloading {}.'.format(url))
        html = get_request(url)

    # HTML on file.

    if html:
        save_html(url, html, path=path)
        return get_soup(html)
    else:
        print('Problem generating soup!')
        return None


def fix_camelcase(name, separator=' '):
    """ Fixes capitalized words that got smooshed together. Uses an optional
        separator to delimit.

        Ex: If we use : as the separator, changes "Incidental PonyWhoa Nelly" to
        "Incidental Pony: Whoa Nelly"
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1{}\2'.format(separator), s1)


def ensure_dir(_dir):
    """ Checks if a directory exists and creates it if it doesn't exist. """
    if not os.path.exists(_dir):
        os.makedirs(_dir)


def table_to_list(t):
    """ Extracts all the text from the table rows to a list of lists. 
    	Note: This won't work for getting hyperlink references, it will get the 
    	text inside.
    """
    return [[cell.text for cell in row.findAll(['th', 'td'])] for row in t.findAll("tr")]


def get_col_index(table, field_name):
    """ Searches the table for the field name in the table header, and returns
        the index of the column it occupies. Returns None if not found.
    """
    table_header = table.tr
    column_names = table_header.findAll('th')

    for i, col in enumerate(column_names):
        if field_name in col.text:
            return i
    return None


def scrape_table_col(table, field_index):
    """
    Get all the <td> elements from the column in the table that correspond to
        the given field index.
    """
    rows = table.findAll('tr')
    countdown = 0
    tempcol = None
    column = []

    # Go through each row in the table
    # for r in rows[1:]:  # ignore the header row
    for r in rows:  # ignore the header row
        cols = r.findAll(['th', 'td'])

        # Deal with row spans.
        # If there is a row span, then the song column is going to shift to the left.
        # But we will instead keep the song col the same, and append the same col for as
        # many times the row span lasts

        rowspan = cols[0].attrs.get('rowspan', 0)

        if rowspan:
            countdown = int(rowspan) - 1
            tempcol = cols[0]
        elif countdown:
            cols.insert(0, tempcol)
            countdown -= 1

        column.append(cols[field_index])

    return column


def write_to_file(filepath, text):
    """ Writes the given text to file in utf-8 format. """
    ensure_dir(os.path.dirname(filepath))

    with open(filepath, 'w') as f:
        f.write(text.encode('utf-8'))


def write_rows_to_csv(row_list, filename):
    """ Takes a list of lists(aka "rows"), and writes the data to a csv file. """
    csv_file = open(filename, 'w')
    writer = csv.writer(csv_file)

    try:
        for row in row_list:
            writer.writerow(row)
    finally:
        csv_file.close()


def write_rows_to_txt(row_list, filename):
	""" Takes a list of lists(aka "rows"), and writes the data to a text file. """
	with open(filename, 'w') as f:
		for r in row_list:
			f.write(' | '.join(r))
			f.write('\n')


def more_pages(soup, text):
    """ Checks if there is is a link with the text in it (usually something like
        "more" or "next page".) Returns the link if it exists, or None if it doesn't.
    """

    results = soup.findAll(text=re.compile(r'{}'.format(text)))

    for r in results:
        parent = r.parent

        if parent and parent.name == 'a':
            return parent['href']
    return None


def is_integer(num):
    """ Returns True if the num argument is an integer, and False if it is not. """
    try:
        num = float(num)
    except ValueError:
        return False

    return num.is_integer()


def analyze_request(url):
    """ Prints out the info on a URL session. """
    r = requests.get(url)
    print(r.status_code)
    print(r.status_headers)


def find_links_by_regex(soup, regex):
    """ Find all the links in the HTML that match the given regular expression. """
    resultset = soup.findAll(text=re.compile(regex))
    links = []
    for r in resultset:
        parent = r.parent

        if parent.name == 'a':
            links.append(parent.attrs.get('href', ''))

    return links


def strip_label(string):
    """
    Removes any labels that are delimited by a colon.
    ex: "Trainer: Unnamed Unicorn Stallion #7", this removes the "Trainer: " part.
    """
    i = string.find(':')
    return string[i + 1:].strip()


def confirm(text):
    """ Confirm that user would want to download/scrape something that might be time-consuming. """
    print('Are you sure you want to {}? (Might take a while!)'.format(text))
    choice = raw_input('[y/n] :> ')
    if choice.lower().startswith('y'):
        return True
    else:
        print('Aborting! :O=')
        exit()
