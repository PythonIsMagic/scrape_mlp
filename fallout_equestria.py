#!/usr/bin/env python
import scrapekit
"""
Get the Fallout Equestria book and convert from HTML to text format.

Text contains "Back to Index" from the links.
"""

if __name__ == "__main__":
    URL = 'http://ponyfictionarchive.net/viewstory.php?action=printable&textsize=0&sid=703&chapter=all'

    # This works, but results in extra junk. We'll redo by manually selecting the elements.
    #  text = scrapekit.html_to_text(URL)
    soup = scrapekit.get_soup(URL)

    print(soup.title.text.encode('utf-8'))
    infobox = soup.find('div', {'class': 'infobox'})
    print(infobox.text.encode('utf-8'))
    #  labels = infobox.findAll('span', {'class': 'label'})

    #  for l in labels:
        #  content = l.findNext()
        #  print('{}: {}'.format(l.text, content.text))

    notes = soup.find('div', {'class': 'notes'})
    print(notes.text.encode('utf-8'))

    # Optional: Get table of contents

    # Parse through all chapters
    chapters = soup.findAll('div', {'class': 'chaptertitle'})

    for i, c in enumerate(chapters):
        print('{}. {}'.format(i+1, c.text.encode('utf-8')))
