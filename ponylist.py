import os
import scrapekit
import sys
"""
Scraping the pony lists from mlp.wikia.com
Each page has a legend table and a table containing a list of all the ponies and their attributes.

The main table has a class: "wikitable sortable listofponies jquery-tablesorter p402_hide"

With columns:
    Name
    Kind(K)
    Group(G)
    Coat color(C)
    Mane Color(M)
    Eye Color(E)
    First appearance(F) - Season Episode Minute Second
    Description and appearance
    Image
"""

# URLSLists of all relevant and official characters in the MLP universe.
URLS = [
    'http://mlp.wikia.com/wiki/List_of_ponies/Unicorn_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Pegasus_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Earth_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Unicorn_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Crystal_Ponies',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Elders',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Foals',
    #  'http://mlp.wikia.com/wiki/List_of_ponies/Mentioned_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_comic_ponies',
    #  'http://mlp.wikia.com/wiki/List_of_Wonderbolts'
]


def scrapenames(url):
    """
    Scrapes the pony names from the wiki page. Returns them in a list.
    """
    soup = scrapekit.get_soup(url)
    tables = soup.findAll('table')
    rows = tables[1].findAll('tr')

    namelist = []
    # Get all the text from the first table element in each row
    for i, r in enumerate(rows):
        if i == 0:
            continue  # skip the header row
        name = r.find('td').text
        namelist.append(name)
    return namelist


def strip_label(string):
    """
    Removes any labels that are delimited by a colon.
    ex: "Trainer: Unnamed Unicorn Stallion #7", this removes the "Trainer: " part.
    """
    i = string.find(':')
    return string[i + 1:]


def remove_unknown(namelist):
    return [n for n in namelist if 'Unnamed' not in n]


def clean_name(n):
    """
    This cleans up any undesireable noise in the scraped name.
    """
    n = scrapekit.fix_camelcase(name, ':')  # Fix camelCase errors
    n = strip_label(name)  # Get rid of any labels.
    n = name.replace('[sic]', '')  # Remove any [sic]'s# Remove any [sic]'s
    return n.strip()   # Strip any spaces


def scrape_all():
    """
    Scrape all lists in URLS, clean up the names, filter out "unknown" characters, and
    filter out duplicate entries.
    """
    masterlist = []
    tally = 0
    for url in URLS:
        names = scrapenames(url)
        tally += len(names)
        print('{} names in {}'.format(len(names), url))
        masterlist.extend(names)

    unique_names = set()
    for n in remove_unknown(masterlist):
        unique_names.add(n)

    print('Total names scraped(including Unnamed ponies): {}'.format(tally))
    print('Total unique and known names: {}'.format(len(unique_names)))
    for n in unique_names:
        print(n)


def get_csv():
    filename = scrapekit.DATADIR + 'pony_list.csv'
    # Remove the file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    rows = []
    for url in URLS:
        soup = scrapekit.get_soup(url)

        # The main comparison table is currently the first table on the page
        table = soup.find('table', {'class': 'listofponies'})
        rows.extend(scrapekit.table_to_list(table))

    scrapekit.write_rows_to_csv(sorted(rows), filename)


def get_images():
    imagelinks = []

    for url in URLS:
        soup = scrapekit.get_soup(url)
        table = soup.find('table', {'class': 'listofponies'})
        #  tbody = table.find('tbody')
        rows = table.findAll('tr')

        # Skip first row
        for row in rows[1:]:
            cols = row.findAll('td')
            if cols:
                name = cols[0].text.strip()
                #  print(name)
                img = cols[-1].find('a').attrs.get('href', 'None')
                #  print(img)

                local_img_src = scrapekit.save_image(name, img)

    return imagelinks

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python ponylist.py <url of pony list>')
        print('ie: python ponylist.py http://mlp.wikia.com/wiki/List_of_ponies/Unicorn_ponies')
        print('To scrape all lists at once:')
        print('$ python ponylist.py all')
        print('To scrape all lists into a csv file:')
        print('$ python ponylist.py csv')
        print('To scrape all pony images in the lists:')
        print('$ python ponylist.py imb')

    elif sys.argv[1] == 'all':
        scrape_all()
    elif sys.argv[1] == 'csv':
        get_csv()
    elif sys.argv[1] == 'img':
        images = get_images()

    elif sys.argv[1].startswith('http://mlp.wikia.com/wiki/List_of_ponies/Unicorn_ponies'):
        for name in scrapenames(sys.argv[1]):
            print(name)
