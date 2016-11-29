"""
This goes through all the lists of ponys in the wiki lists, and for each pony that has a picture,
it downloads it (if we don't already have it).

Then it constructs an HTML page that showcases a table of all the pics with their names as
labels.
"""

import os
IMG_DIR = 'data/img/'

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


def get_img_list(_dir, ext='.png'):
    images = []

    for file in os.listdir(_dir):
        if file.endswith(ext):
            images.append(file)
    return images


def mk_img_sheet(_dir, cols=5):
    images = iter(get_img_list(_dir))
    filename = './imgsheet.html'
    width, height = 150, 150

    with open(filename, 'w') as f:
        f.write(BEGIN_HTML)
        f.write('<table>\n')

        for i, img in enumerate(images):
            row, col = divmod(i, cols)
            if col == 0:
                f.write('<tr>\n')

            f.write('<td>')
            imglink = _dir + img
            imgname = os.path.basename(img)[:-4]
            f.write('<div class="thumbnail">')
            f.write('<img src="{}" width="{}px" height="{}px">'.format(imglink, width, height))
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


if __name__ == "__main__":
    mk_img_sheet(IMG_DIR)
