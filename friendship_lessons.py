#!/usr/bin/env python
import scrapekit
import sys
import textwrap
"""
    Date: 10/15/16
    All of the MLP "Friendship Lessons" are contained on the page on the below URL.
    The lessons are laid out in <dl> tags, but these are preceded by spans that each have the
    class "mw-headline". So we can use that class as the anchor to scrape by.

    The structure we're looking at is:
        <h3>
            <span class="mw-headline">
        <dl><dd> text...
"""
URL = 'http://mlp.wikia.com/wiki/Friendship_lessons'

if __name__ == "__main__":
    download = False
    usage = """
Usage: {} [-d]'.format(sys.argv[0])
    -d downloads all friendship lessons to text file.
    No arguments - display all friendship lessons.
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

    soup = scrapekit.handle_url(URL)
    spans = soup.findAll('span', {'class': 'mw-headline'})

    lessons = []

    for span in spans:
        h3 = span.parent
        dl = h3.findNext('dl')
        if dl:
            lines = dl.text.encode('utf-8').split('\n')
            text = ''
            for l in lines:
                for l in textwrap.wrap(l, 78):
                    text += (l + '\n')
            print(text)
            lessons.append(text)

    if download:
        filename = scrapekit.DATADIR + 'lessons.txt'

        with open(filename, 'w') as f:
            sep = '\n' + '~-'*40 + '\n\n'
            for l in lessons:
                f.write(l)
                f.write(sep)
