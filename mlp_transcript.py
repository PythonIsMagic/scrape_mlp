import scrapekit
import sys
"""
    Sample transcript page: http://mlp.wikia.com/wiki/Transcripts/My_Little_Pony_Equestria_Girls:_Rainbow_Rocks
    It appears that the main content is located in id: WikiaMainContentContainer
    The more central text is located under id='WikiaArticle'
"""
TRANSCRIPT_DIR = scrapekit.DATADIR + '/transcripts/'


def scrape_transcript(url):
    ID = 'WikiaArticle'
    soup = scrapekit.get_soup(url)
    return soup.find(id=ID).text


def get_transcript(url):
    text = scrape_transcript(url)
    filename = TRANSCRIPT_DIR + url.split('/')[-1]
    scrapekit.ensure_dir(TRANSCRIPT_DIR)
    scrapekit.write_to_file(filename, text)

if __name__ == "__main__":
    #  URL = '#WikiaMainContentContainer'
    if len(sys.argv) != 2:
        print('Usage: python scrape_transcript.py url')
        exit()

    URL = sys.argv[1]
    get_transcript(URL)
