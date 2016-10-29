#!/usr/bin/env python
import sys
import scrapekit



def scrape_id_to_div(soup, id):
    lyrics = soup.find(id='Lyrics')

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
            #  print('Current element is None! Stopping here.')
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
    infobox = soup.find('table', {'class': 'infobox'})
    unwanted = ['Episode Transcript', 'BMI Work No.', 'International versions']

    boldtags = [t for t in infobox.findAll('b') if t.text not in unwanted]

    _str = ''
    for tag in boldtags:
        _str += tag.text + ': ' + scrapekit.fix_camelcase(tag.findNext('td').text, ',')

    return _str


def scrape_song_url(url):
    soup = scrapekit.get_soup(url)

    contents = scrape_id_to_div(soup, 'Lyrics')
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
    #  filename = songtitle.replace(' ', '_') + '.txt'

    text = ''
    text += 'Song: {}\n'.format(songtitle)
    text += get_infobox_info(soup)
    text += '\n\n'
    text += filetext

    # This duplicates lines!?!?
    #  for line in contents:
        #  print(line.text)

    return text


def get_lyrics(url):
    text = scrape_song_url(url)

    if text is None:
        return None
    else:
        return text

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: scraper.py url')
        exit()
    else:
        print(get_lyrics(sys.argv[1]))
