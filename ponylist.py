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


def strip_label(string):
    """
    Removes any labels that are delimited by a colon.
    ex: "Trainer: Unnamed Unicorn Stallion #7", this removes the "Trainer: " part.
    """
    i = string.find(':')
    return string[i + 1:].strip()


def remove_unknown(rows):
    return [r for r in rows if 'Unnamed' not in r[0]]


def clean_name(name):
    """
    Cleans up any undesirable noise in the scraped name.
    """
    n = scrapekit.fix_camelcase(name, ':')  # Fix camelCase errors
    n = n.replace('[sic]', '')  # Remove any [sic]'s# Remove any [sic]'s
    # Clean name of '/'
    n = n.replace('/', 'or')
    return n.strip()   # Strip any spaces


def get_rows(urls):
    rows = []
    for url in urls:
        print('Scraping {}'.format(url))
        soup = scrapekit.handle_url(url)
        table = soup.find('table', {'class': 'listofponies'})
        rows.extend(table_to_list(table))
    return rows


def table_to_list(t):
    """
    Extracts all the rows in a table, excluding the headers.
    """
    rows = t.findAll("tr")
    list_of_rows = []

    for row in rows:
        table_row = [cell for cell in row.findAll(['th', 'td'])]

        # Get the image url - usually in the last column
        a = table_row[-1].find('a')
        if a:
            img_link = a.attrs.get('href', 'None')
            table_row[-1] = img_link

        # Convert to text
        table_row = [cell.text.encode('utf-8') for cell in row.findAll(['th', 'td'])]
        list_of_rows.append(table_row)

    return list_of_rows


def get_images(rows):
    confirm('download images')
    scrapekit.ensure_dir(IMG_DIR)

    for row in rows:
        # We'll prepend the pony race/species to the beginning of the image file
        # So it's easier to sort or display.
        name = row[1] + ': ' + row[0]
        img_link = row[-1]
        scrapekit.save_image(name, img_link)


def display_rows(rows):
    for r in rows:
        #  print(r)
        pprint(r)


def process_rows(rows, args):
    # Keep unnamed ponies/characters?
    if args.known:
        rows = remove_unknown(rows)

    # Cleanup names (think about cleaning other rows in the future -
    for r in rows:
        r[0] = clean_name(r[0])

    if args.strip_labels:
        for r in rows:
            r[0] = strip_label(r[0])

    # Check if we only want the names.
    if args.names:
        # note: we have to keep it a list of lists for file processing
        rows = [[r[0]] for r in rows]
    return rows


def write_file(list_of_rows, args):
    if args.download == 'csv':
        filename = scrapekit.DATADIR + args.type + '.' + args.download
        print('Writing to {}.'.format(filename))
        scrapekit.write_rows_to_csv(list_of_rows, filename)

    elif args.download == 'txt':
        filename = scrapekit.DATADIR + args.type + '.' + args.download
        print('Writing to {}.'.format(filename))
        with open(filename, 'w') as f:
            for r in list_of_rows:
                pprint(r, stream=f)


def confirm(text):
    print('Are you sure you want to {}? (Might take a while!)'.format(text))
    choice = raw_input('[y/n] :> ')
    if choice.lower().startswith('y'):
        return True
    else:
        print('Aborting! :O=')
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
    parser.add_argument('-s', '--strip-labels', action='store_true',
                        help='Removes any labels from character names\n(ie: Removes "Bright Pony: " from "Bright Pony: Sunshine Smiles"')

    parser.add_argument('-k', '--known', action='store_true',
                        help='Discards any "Unnamed" names from our results.')

    return parser

if __name__ == "__main__":
    type_choices = URLS.keys()
    type_choices.append('all')
    parser = make_parser()
    args = parser.parse_args()

    if args.type == 'all':
        if confirm("scrape ALL categories"):
            scraping_urls = URLS.values()
    else:
        # Scrape one category
        scraping_urls = [URLS[args.type]]

    rows = get_rows(scraping_urls)

    original_count = len(rows)
    rows = process_rows(rows=rows, args=args)

    # Info and summary section
    if args.verbose:
        display_rows(rows)

    if not args.quiet:
        sep = '-'*60
        print('')
        print(sep.center(80))
        print('SUMMARY'.center(80))
        print('')
        print('Type selected:      {}'.format(args.type))
        print('Total rows scraped: {}'.format(original_count))
        print('Total rows kept:    {}'.format(len(rows)))
        #  print('Total unique and known names: {}'.format(len(unique_names)))

    # Filework
    if args.images:

        if not args.quiet:
            print('Downloading images!')
        images = get_images(rows)

    if args.download:
        write_file(rows, args)
