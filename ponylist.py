from pprint import pprint
import argparse
import scrapekit
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
IMG_DIR = './data/img/'

# URLSLists of all relevant and official characters in the MLP universe.
URLS = {
    'unicorns': 'http://mlp.wikia.com/wiki/List_of_ponies/Unicorn_ponies',
    'pegasus': 'http://mlp.wikia.com/wiki/List_of_ponies/Pegasus_ponies',
    'earthponies': 'http://mlp.wikia.com/wiki/List_of_ponies/Earth_ponies',
    'crystal': 'http://mlp.wikia.com/wiki/List_of_ponies/Crystal_Ponies',
    'elders': 'http://mlp.wikia.com/wiki/List_of_ponies/Elders',
    'foals': 'http://mlp.wikia.com/wiki/List_of_ponies/Foals',
    'mentioned': 'http://mlp.wikia.com/wiki/List_of_ponies/Mentioned_ponies',
    'comic': 'http://mlp.wikia.com/wiki/List_of_comic_ponies',
    'wonderbolts': 'http://mlp.wikia.com/wiki/List_of_Wonderbolts',
    'alicorns': 'http://mlp.wikia.com/wiki/List_of_ponies/Alicorn_ponies',
    'prose': 'http://mlp.wikia.com/wiki/List_of_prose_ponies',
    'other': 'http://mlp.wikia.com/wiki/List_of_non-pony_characters',
}


def get_images(category_urls):
    scrapekit.ensure_dir(IMG_DIR)

    imagelinks = []
    for url in category_urls:
        soup = scrapekit.handle_url(url)
        table = soup.find('table', {'class': 'listofponies'})
        rows = table.findAll('tr')

        # Skip first row
        for row in rows[1:]:
            cols = row.findAll('td')
            if cols:
                name = cols[0].text.encode('utf-8').strip()
                # We'll ignore unknown ponies:
                if 'Unnamed' in name:
                    continue
                img = cols[-1].find('a').attrs.get('href', 'None')

                scrapekit.save_image(name, img)

    return imagelinks


def strip_label(string):
    """
    Removes any labels that are delimited by a colon.
    ex: "Trainer: Unnamed Unicorn Stallion #7", this removes the "Trainer: " part.
    """
    i = string.find(':')
    return string[i + 1:]


def remove_unknown(rows):
    return [r for r in rows if 'Unnamed' not in r[0]]


def clean_name(name):
    """
    This cleans up any undesireable noise in the scraped name.
    """
    n = scrapekit.fix_camelcase(name, ':')  # Fix camelCase errors
    n = n.replace('[sic]', '')  # Remove any [sic]'s# Remove any [sic]'s
    return n.strip()   # Strip any spaces


def get_rows(urls):
    rows = []
    for url in urls:
        print('Scraping {}'.format(url))
        soup = scrapekit.handle_url(url)
        table = soup.find('table', {'class': 'listofponies'})
        rows.extend(scrapekit.table_to_list(table))
    return rows


def display_rows(rows):
    for r in rows:
        #  print(r)
        pprint(r)


def process_rows(rows, args):
    # Keep unnamed ponies/characters?
    if args.known:
        rows = remove_unknown(rows)

    # Cleanup
    if args.clean_names:
        for r in rows:
            r[0] = clean_name(r[0])

    # Check if we only want the names
    if args.names:
        rows = [r[0] for r in rows]

    if args.download == 'csv':
        filename = scrapekit.DATADIR + args.type + '.' + args.download
        print('Writing to {}.'.format(filename))
        scrapekit.write_rows_to_csv(sorted(rows), filename)

    elif args.download == 'txt':
        filename = scrapekit.DATADIR + args.type + '.' + args.download
        print('Writing to {}.'.format(filename))
        with open(filename, 'w') as f:
            for r in rows:
                pprint(r, stream=f)
    return rows


def confirm_all():
    print('Are you sure you want to scrape ALL types? (Might take a while!)')
    choice = raw_input('[y/n] :> ')
    if choice.lower().startswith('y'):
        return True
    else:
        exit()


def make_parser():
    parser = argparse.ArgumentParser(
        description='List all ponies, or specific categories of characters, from My Little Pony songs from mlp.wikia.com.')

    v_group = parser.add_mutually_exclusive_group()
    v_group.add_argument('-v', '--verbose', action='count',
                         help='Display extra details while processing.')
    v_group.add_argument('-q', '--quiet', action='store_true',
                         help="Don't display text while processing.")

    parser.add_argument('type', type=str, choices=type_choices,
                        help='The category of pony to list')
    parser.add_argument('-i', '--images', action='store_true',
                        help='Download all images found on the lists.')
    parser.add_argument('-n', '--names', action='store_true',
                        help='Only get the pony names, discard all other columns.')

    parser.add_argument('-d', '--download', type=str, choices=['txt', 'csv'],
                        help='Download the info to file format of your choice.')
    parser.add_argument('-c', '--clean-names', action='store_true',
                        help='Clean up names (Fixes camelcase and removes brackets.')
    parser.add_argument('-k', '--known', action='store_true',
                        help='Discards any "Unnamed" names from our results.')

    #  parser.add_argument('-f', '--file', type=str, default='pony_list',
                        #  help="Specify the filename to write to.")

    return parser

if __name__ == "__main__":
    type_choices = URLS.keys()
    type_choices.append('all')
    parser = make_parser()
    args = parser.parse_args()

    if args.type == 'all':
        if confirm_all():
            scraping_urls = URLS.values()
    else:
        # Scrape one category
        scraping_urls = [URLS[args.type]]

    #  rows = scrape_everything()
    rows = get_rows(scraping_urls)

    if args.images:
        print('Downloading images!')
        #  images = get_images(scraping_urls)

    original_count = len(rows)
    rows = process_rows(rows=rows, args=args)

    # Info and summary section
    if not args.quiet:
        display_rows(rows)

    if args.verbose:
        sep = '-'*60
        print('')
        print(sep.center(80))
        print('SUMMARY'.center(80))
        print('')
        print('Type selected:      {}'.format(args.type))
        print('Total rows scraped: {}'.format(original_count))
        print('Total rows kept:    {}'.format(len(rows)))
        #  print('Total unique and known names: {}'.format(len(unique_names)))
