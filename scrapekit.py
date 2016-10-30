# coding=utf-8
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO
import csv
import os
import re
import requests
import urlparse
import time

DELAY = 5  # Seconds
DATADIR = "data/"
PAGEDIR = "./pages/"

HEADER_MOZ1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5)'}
HEADER_MOZ2 = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) \
               AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
               "Accept": "text/html,application/xhtml+xml,application/xml;\
               q=0.9,image/webp,*/*;q=0.8"}


def saved_html_name(url):
    parsed = urlparse.urlparse(url)
    filename = parsed.netloc + parsed.path + parsed.query
    if not filename.endswith('.html'):
        filename += '.html'

    # We cannot use '/' in our names - conflicts with Linux. Use '__' instead.
    filename = filename.replace('/', '__')
    return PAGEDIR + filename


def save_html(url):
    # We will save the file as the url if possible.
    req = requests.get(url, headers=HEADER_MOZ1)

    if req.ok:
        time.sleep(DELAY)  # Be polite! ;)
        html = req.text
    else:
        print('Request unsuccessful with code: {}'.format(req.status_code))
        return None

    if html:
        ensure_dir(PAGEDIR)
        filename = saved_html_name(url)

        with open(filename, 'w') as f:
            f.write(html.encode('utf-8'))
        return html
    else:
        print('Not able to retrieve and save html!')
        return None


def load_html(url):
    filename = saved_html_name(url)

    # If file is empty, just delete it
    if os.path.exists(filename) and os.path.getsize(filename) == 0:
        os.remove(filename)

    # Check if file exists and return the html
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.read()
    else:
        return None


def handle_url(url):
    # Checks if the URL exists as a saved html file, and returns it's soup.
    # If we don't have it, we download it and save it. And return it's soup.

    # dir is a subdir of PAGEDIR.
    # timestamp - useful if we want to keep checking updated versions.
    # overwrite - if we always want the newest ver.
    html = load_html(url)

    if not html:
        print('Downloading {}.'.format(url))
        html = save_html(url)
    else:
        print('HTML on file.')

    if html:
        return BeautifulSoup(html, "html.parser")
    else:
        print('Problem generating soup!')
        return None


def get_soup(url, headers=None):
    """
    Get the Beautiful Soup tree from an HTML link by using the requests module.
    """
    time.sleep(DELAY)
    if headers:
        #  html = requests.get(url, headers=headers)
        req = requests.get(url)
        req.headers = headers
    else:
        req = requests.get(url)

    if req.ok:
        html = req.text
        #  return BeautifulSoup(req.content, "html.parser")
        #  return BeautifulSoup(req.text, "html5lib")  # Haven't tested this yet
        return BeautifulSoup(html, "html.parser")
    else:
        print('Request unsuccessful with code: {}'.format(req.status_code))
        return None


def fix_camelcase(name, separator=' '):
    """
    Fixes capitalized words that got smooshed together. Uses an optional separator to delimit.

    Ex: If we use : as the separator, changes "Incidental PonyWhoa Nelly" to
        "Incidental Pony: Whoa Nelly"
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1{} \2'.format(separator), s1)


def make_ascii(name):
    return name.decode('utf8').encode('ascii', 'replace')


def analyze_request(url):
    r = requests.get(url)
    print(r.status_code)
    print(r.status_headers)


def ensure_dir(_dir):
    if not os.path.exists(_dir):
        os.makedirs(_dir)


def write_to_file(filename, text):
    # Ensure the dir exists.
    ensure_dir(os.path.dirname(filename))

    # Winter Wrap Up had an encoding error, so we'll use .encode('utf8')
    with open(filename, 'w') as f:
        f.write(text.encode('utf-8'))
        #  f.write(make_ascii(text))


def html_to_text(url):
    soup = get_soup(url)
    return soup.text.encode('utf-8')


def table_to_list(t):
    rows = t.findAll("tr")
    list_of_rows = []

    for row in rows:
        list_of_rows.append(
            # Turn the current table row into a list. Make sure it's ascii friendly. :)
            [cell.text.encode('utf-8') for cell in row.findAll(['th', 'td'])]
        )
    return list_of_rows


def write_rows_to_csv(list_of_rows, filename):
    csvFile = open(filename, 'a')
    writer = csv.writer(csvFile)

    try:
        for row in list_of_rows:
            writer.writerow(row)
    finally:
        csvFile.close()


def save_image(name, source):
    FORMAT = '.png'
    # Image.save should determine the type from the extention

    IMGDIR = DATADIR + 'img/'
    # Clean name of '/'
    name = name.replace('/', 'or')
    filename = IMGDIR + '_'.join(name.lower().split()) + FORMAT

    # Check if we have this img
    if os.path.exists(filename):
        print('Already have pic for {}!'.format(name))
        pass
    else:
        print('Retrieving picture for {}'.format(name))
        time.sleep(2)
        r = requests.get(source)
        i = Image.open(StringIO(r.content))

        #  with open(filename, 'w') as f:
        try:
            i.save(filename)
        except:
            print('{} save failed!'.format(filename))
            exit()

    return filename


def more_pages(soup, text):
    # Return True if there is a link with the text in it (usually something like "more" or
    # "next page")
    # Return the link, or None

    results = soup.findAll(text=re.compile(r'{}'.format(text)))

    for r in results:
        parent = r.parent

        if parent and parent.name == 'a':
            return parent['href']
    return None
