"""
  " Downloads MLP transcripts from the wiki.
  " All of the MLP episode transcripts are located on the below URL.
  " Each season has a table:
  "         No | Title | Writer | Releasedate | Transcript | Gallery
  "
  " Sample link:
  " <a href="/wiki/Transcripts/The_Crystalling_-_Part_1" title="Transcripts/The Crystalling - Part 1">Transcript</a>
  "
  " Approach 1: Use regex to find "Transcript" and get parents that are <a href> tags
  " Approach 2: Find all the <a> tags, than filter out ones that don't have Transcript
  "
  " Sample transcript page: http://mlp.wikia.com/wiki/Transcripts/My_Little_Pony_Equestria_Girls:_Rainbow_Rocks
  " It appears that the main content is located in id: WikiaMainContentContainer
  " The more central text is located under id='WikiaArticle'
  """

import argparse
import scrapekit

TRANSCRIPT_DIR = scrapekit.DATADIR + '/transcripts/'
URL = 'http://mlp.wikia.com/wiki/Episodes,_films,_and_shorts'
PREFIX = 'http://mlp.wikia.com'


def scrape_transcript(url):
    ID = 'WikiaArticle'
    soup = scrapekit.handle_url(url)
    text = soup.find(id=ID).text
    filename = TRANSCRIPT_DIR + url.split('/')[-1]
    scrapekit.ensure_dir(TRANSCRIPT_DIR)
    scrapekit.write_to_file(filename, text)


def main():
    """ Main entry point. """
    parser = argparse.ArgumentParser(description="Get all links for My Little Pony transcripts from mlp.wikia.com.")
    parser.add_argument('-d', '--download', action="store_true", help="Download all transcripts to text files.")
    parser.add_argument('url', nargs='?', default=None,
                        help="Add a url to download a single transcript.")
    args = parser.parse_args()

    if args.url:
        print(scrape_transcript(args.url))
        exit()

    soup = scrapekit.handle_url(URL)
    transcript_links = scrapekit.find_links_by_regex(soup, r'Transcript')
    print('got past getting transcript links')

    for t in transcript_links:
        print(t)

        if args.download:
            scrape_transcript(PREFIX + t)


if __name__ == "__main__":
    main()
