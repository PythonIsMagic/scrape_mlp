#!/usr/bin/env python
import argparse
import scrapekit
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
    parser = argparse.ArgumentParser(description="Get all friendship lessons from the show.")
    parser.add_argument('-v', '--verbose', action="store_true",
                        help="Display more info about processing.")
    parser.add_argument('-d', '--download', action='store_true',
                        help="Download all friendship lessons to text file.")
    parser.add_argument('-o', '--format', action='store_true',
                        help='Formats the text for better readability.')
    args = parser.parse_args()

    soup = scrapekit.handle_url(URL)
    spans = soup.findAll('span', {'class': 'mw-headline'})

    lessons = []

    # Collect lessons text
    for span in spans:
        h3 = span.parent
        dl = h3.findNext('dl')
        if dl:
            text = dl.text.encode('utf-8')
            lessons.append(text)

    if args.format:
        print('Formatting text...')

        for x, lesson in enumerate(lessons[:]):
            text = ''
            lines = lesson.split('\n')
            for i in lines:
                for i in textwrap.wrap(i, 78):
                    text += i + '\n'
            lessons[x] = text

    if args.verbose:
        for i in lessons:
            print(i)

    if args.download:
        filename = scrapekit.DATADIR + 'lessons.txt'

        with open(filename, 'w') as f:
            for i in lessons:
                f.write(i)
