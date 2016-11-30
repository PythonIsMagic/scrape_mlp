"""
This goes through all the lists of ponys in the wiki lists, and for each pony that has a picture,
it downloads it (if we don't already have it).

Then it constructs an HTML page that showcases a table of all the pics with their names as
labels.
"""

import os
import requests
import scrapekit
import time
from PIL import Image
from StringIO import StringIO

DATADIR = 'data/'

BEGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
    <title>Look at the ponies!</title>
</head>
<body>
<div class="container">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header">Look at all the poniez!!</h1>
        </div>
"""

END_HTML = """
    </div>
</div>
<footer>
    <div class="row">
        <div class="col-lg-12">
            <p>You sure you looked at every one?!  Look again...</p>
        </div>
    </div>
</footer>
</body>
</html>
"""


def get_images(rows, img_dir):
    scrapekit.confirm('download images to {}'.format(img_dir))
    scrapekit.ensure_dir(img_dir)

    for row in rows:
        # We'll prepend the pony race/species to the beginning of the image file
        # So it's easier to sort or display.
        name = row[1] + '_' + row[0]
        img_link = row[-1]
        save_image(name, img_link, img_dir)


def save_image(img_name, img_link, img_dir, FORMAT='.png'):
    """ Saves a URL link to an image to disk. """

    # Image.save should determine the type from the extention

    filename = img_dir + '_'.join(img_name.lower().split()) + FORMAT

    if not img_link.startswith('http'):
        return False
    elif os.path.exists(filename):
        # Check if we have this img
        print('Already have pic for {}!'.format(img_name))
        return False
    else:
        print('Retrieving picture for {}'.format(img_name))
        time.sleep(2)
        r = requests.get(img_link)
        i = Image.open(StringIO(r.content))

        #  with open(filename, 'w') as f:
        try:
            i.save(filename)
        except IOError:
            print('{} save failed!'.format(filename))
            return False
    return True


def get_img_list(_dir, ext='.png'):
    """ Retrieves the list of images from the specified directory. Specify the
        extension(image type) with ext parameter.
    """
    images = []

    for _file in os.listdir(_dir):
        if _file.endswith(ext):
            images.append(_file)
    return images


def mk_img_sheet(img_dir, cols=5):
    """ Creates an HTML sheet of images in the given directory. """
    filename = img_dir + 'image_table.html'
    images = iter(get_img_list(img_dir))
    width, height = 150, 150

    with open(filename, 'w') as f:
        f.write(BEGIN_HTML)
        f.write('<table>\n')

        for i, img in enumerate(images):
            # row, col = divmod(i, cols)
            col = i % cols
            if col == 0:
                f.write('<tr>\n')

            f.write('<td>')
            # imglink = img_dir + img
            imgname = os.path.basename(img)[:-4]
            f.write('<div class="thumbnail">')
            f.write('<img src="{}" width="{}px" height="{}px">'.format(img, width, height))
            f.write('<b>{}</b>'.format(imgname))
            f.write('</div>')
            f.write('</td>')

            if col == cols - 1:
                f.write('</tr>\n')

        # Make sure we end the table row
        if col != cols - 1:
            f.write('</tr>\n')

        f.write('</tr>\n')
        f.write('</table>\n')
        f.write(END_HTML)
    return
