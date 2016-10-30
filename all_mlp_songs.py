#!/usr/bin/env python
"""
    Scraping from the MLP songs page.
    We luckily have a bunch of tables setup.
    table[0] is the albums table
    table[1] is the theme song variations

    Table format:
        Episode | Song | Lead | Begins at | Length | Album | Lyrics
"""
import scrapekit
import mlp_song
import sys

URL = 'http://mlp.wikia.com/wiki/Songs'
PREFIX = 'http://mlp.wikia.com'
SONG_DIR = scrapekit.DATADIR + 'songs/'


def get_column_index(table, field_name):
    table_header = table.tr
    #  print('Table header: {}'.format(table_header))

    column_names = table_header.findAll('th')
    #  print('Columns: {}'.format(column_names))

    for i, col in enumerate(column_names):
        if field_name in col.text:
            return i
            break
    else:
        #  print('Table does not contain field: {}'.format(field_name))
        return None


def scrape_table_col(table, field_index):
    """
    Get all the <td> elements from the column in the table that correspond to the given
    field index.
    """
    rows = table.findAll('tr')
    countdown = 0
    tempcol = None
    songlinks = []

    # Go through each row in the table
    for r in rows[1:]:  # ignore the header row
        columns = r.findAll('td')

        # Deal with row spans.
        # If there is a row span, then the song column is going to shift to the left.
        # But we will instead keep the song col the same, and append the same col for as
        # many times the row span lasts

        rowspan = columns[0].attrs.get('rowspan', 0)

        if rowspan:
            countdown = int(rowspan) - 1
            tempcol = columns[0]
        elif countdown:
            columns.insert(0, tempcol)
            countdown -= 1

        songlinks.append(columns[field_index])

    return songlinks


def scrape_all_songs():
    print('Scraping all songs from {}'.format(URL))
    soup = scrapekit.get_soup(URL)
    song_elements = []
    tables = soup.findAll('table')

    for t in tables:
        field_name = 'Song'
        field_index = get_column_index(t, field_name)

        if field_index:
            song_elements.extend(scrape_table_col(t, field_index))

    songlinks = []
    for element in song_elements:
        link = element.find('a')
        if link:
            songlinks.append(PREFIX + link.attrs.get('href', ''))
    return songlinks

if __name__ == "__main__":
    download = False
    usage = """
Usage: {} [-d]'.format(sys.argv[0])
    -d downloads all lyrics to text files.
    No arguments - display all song links.
    """

    if len(sys.argv) == 2:
        if sys.argv[1] == '-d':
            download = True
        elif sys.argv[1] in ['?', '--h', '-h']:
            print(usage)
            exit()
    elif len(sys.argv) > 2:
        print(usage)
        exit()

    songlinks = scrape_all_songs()

    for link in songlinks:
        print(link)
        if download:
            # The link doesn't include the base URL, need to add that prefix.
            print('Scraping {}...'.format(link))

            text = mlp_song.get_lyrics(link)
            filename = SONG_DIR + link.split('/')[-1]

            scrapekit.write_to_file(filename, text)
