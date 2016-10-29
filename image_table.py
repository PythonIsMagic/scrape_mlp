import os

BEGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <title>Look at the ponies!</title>
</head>
<body>
"""

END_HTML = """
</body>
</html>
"""


def get_img_list(DIR, ext='.png'):
    images = []

    for file in os.listdir('.' + DIR):
        if file.endswith(ext):
            images.append(file)
    return images


def mk_img_sheet(DIR, cols=5):
    images = iter(get_img_list(DIR))
    filename = 'imgsheet.html'
    width, height = 150, 150

    with open(filename, 'w') as f:
        f.write(BEGIN_HTML)
        f.write('<table>\n')

        for i, img in enumerate(images):
            row, col = divmod(i, cols)
            if col == 0:
                f.write('<tr>\n')

            f.write('<td>')
            imglink = os.curdir + DIR + img
            imgname = os.path.basename(img)[:-4]
            f.write('\n<p>{}</p>'.format(imgname))
            f.write('<img src="{}" width="{}px" height="{}px">'.format(imglink, width, height))
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
    DIR = '/data/img/'
    mk_img_sheet(DIR)
