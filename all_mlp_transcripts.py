import re
import scrapekit
import mlp_transcript
import sys
import time

"""
    Date: 10/15/16
    All of the MLP episode transcripts are located on the below URL.
    Each season has a table:
            No | Title | Writer | Releasedate | Transcript | Gallery

    Sample link:
    <a href="/wiki/Transcripts/The_Crystalling_-_Part_1" title="Transcripts/The Crystalling - Part 1">Transcript</a>

    Approach 1: Use regex to find "Transcript" and get parents that are <a href> tags
    Approach 2: Find all the <a> tags, than filter out ones that don't have Transcript
"""

URL = 'http://mlp.wikia.com/wiki/Episodes,_films,_and_shorts'
PREFIX = 'http://mlp.wikia.com'


def find_links_by_regex(soup):
    resultset = soup.findAll(text=re.compile(r'Transcript'))
    links = []
    for r in resultset:
        parent = r.parent
        if parent.name == 'a':
            links.append(parent)

    return links

if __name__ == "__main__":
    download = False
    usage = """
Usage: {} [-d]'.format(sys.argv[0])
    -d downloads all transcripts to text files.
    No arguments - display all transcript links
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

    soup = scrapekit.get_soup(URL)
    transcript_links = find_links_by_regex(soup)

    for t in transcript_links:
        link = t.attrs.get('href', '')
        print(link)

        if download:
            time.sleep(2)
            mlp_transcript.get_transcript(PREFIX + link)
