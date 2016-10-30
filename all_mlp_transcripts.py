import argparse
import re
import scrapekit
import mlp_transcript
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
    parser = argparse.ArgumentParser(description="Get all links for My Little Pony transcripts from mlp.wikia.com.")
    parser.add_argument('-q', '--quiet', action="store_true", help="Don't display text while processing.")
    parser.add_argument('-d', '--download', action="store_true", help="Download all transcripts to text files.")
    args = parser.parse_args()

    soup = scrapekit.get_soup(URL)
    transcript_links = find_links_by_regex(soup)

    for t in transcript_links:
        link = t.attrs.get('href', '')

        if not args.quiet:
            print(link)

        if args.download:
            time.sleep(2)
            mlp_transcript.get_transcript(PREFIX + link)
