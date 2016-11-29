#!/usr/bin/env python
"""
    Scraping from the MLP songs page.
    We luckily have a bunch of tables setup.
    table[0] is the albums table
    table[1] is the theme song variations

    Table format:
        Episode | Song | Lead | Begins at | Length | Album | Lyrics
"""

import argparse
import scrapekit

URL = 'http://mlp.wikia.com/wiki/Songs'
PREFIX = 'http://mlp.wikia.com'
SONG_DIR = scrapekit.DATADIR + 'songs/'


def scrape_id_to_div(soup, div_id):
    """ Scrapes songs lyrics. """
    lyrics = soup.find(id=div_id)

    if lyrics is None:
        return None

    lyrics_parent = lyrics.parent

    contents = []
    endtag = 'div'
    # These are possible tags that we would want to end the current lyric section on.
    end_ids = ['References', 'Other_versions', 'INCONTENT_WRAPPER', 'Reprise', 'Lyrics_2']
    wanted_tags = ['dl']

    curr = lyrics_parent
    while True:
        curr = curr.find_next_sibling()

        if curr is None:
            #  Current element is None. Stopping here.
            return contents

        # Check if we reached the end of the lyric section
        for i in end_ids:
            if curr.find(id=i) or curr.attrs.get('id', None) == i:
                return contents

        if curr.name == endtag:  # For Smile Song
            break
        elif curr.name in wanted_tags:
            # Add it if its a tag we want
            contents.append(curr)

    return contents


def get_infobox_info(soup):
    """ Gets all info, like artist, title, album, from the wiki infobox. """
    infobox = soup.find('table', {'class': 'infobox'})
    unwanted = ['Episode Transcript', 'BMI Work No.', 'International versions']

    boldtags = [t for t in infobox.findAll('b') if t.text not in unwanted]

    _str = ''
    for tag in boldtags:
        _str += tag.text + ': ' + scrapekit.fix_camelcase(tag.findNext('td').text, ',')

    return _str


def scrape_song(url):
    """ Gets the lyrics and song info from a wiki url. """
    soup = scrapekit.handle_url(url)

    contents = scrape_id_to_div(soup, "Lyrics")
    if not contents:
        return None

    filetext = ''.join(c.text for c in contents)

    # Check if there is a reprise
    REPRISE = 'Reprise'

    reprise = soup.find(id=REPRISE)
    if reprise:
        filetext += '\n\n'
        filetext += REPRISE + ':\n\n'

        contents = scrape_id_to_div(soup, REPRISE)
        filetext += ''.join(c.text for c in contents)

    # Get song title, fix blank spaces for file name
    songtitle = soup.title.text.split('|')[0]

    song_text = ''
    song_text += 'Song: {}\n'.format(songtitle)
    song_text += get_infobox_info(soup)
    song_text += '\n\n'
    song_text += filetext

    return song_text


def get_lyrics(url):
    song_text = scrape_song(url)

    if song_text is None:
        return None
    else:
        return song_text


def scrape_all_songs():
    """ Gets all lyrics from all available songs on the wiki. """
    print('Scraping all songs from {}'.format(URL))

    soup = scrapekit.handle_url(URL)
    song_elements = []
    tables = soup.findAll('table')

    for t in tables:
        field_index = scrapekit.get_col_index(t, field_name="Song")

        if field_index:
            song_elements.extend(scrapekit.scrape_table_col(t, field_index))

    links = []
    for element in song_elements:
        l = element.find('a')
        if l:
            links.append(PREFIX + l.attrs.get('href', ''))
    return links


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads lyrics for My Little Pony: FiM songs from mlp.wikia.com.")

    parser.add_argument('-d', '--download', action="store_true", help="Download all songs to text files.")
    parser.add_argument('url', nargs='?', default=None,
                        help="Add a url to download a single song.")
    args = parser.parse_args()

    if args.url:
        print(get_lyrics(args.url))
        exit()

    songlinks = scrape_all_songs()

    for link in songlinks:
        print(link)

        if args.download:
            # The link doesn't include the base URL, need to add that prefix.
            if not args.quiet:
                print('Scraping {}...'.format(link))

            text = get_lyrics(link)
            filename = SONG_DIR + link.split('/')[-1]

            scrapekit.write_to_file(filename, text)
