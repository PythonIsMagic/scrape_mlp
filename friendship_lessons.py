#!/usr/bin/env python
import scrapekit
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
    soup = scrapekit.get_soup(URL)
    spans = soup.findAll('span', {'class': 'mw-headline'})

    for span in spans:
        h3 = span.parent
        dl = h3.findNext('dl')
        if dl:
            text = dl.text
            print(text.encode('utf8'))
