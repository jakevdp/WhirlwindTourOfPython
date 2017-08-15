"""
This script copies all notebooks from the book into the website directory, and
creates pages which wrap them and link together.
"""
import os
import nbformat
import shutil

PAGEFILE = """title: {title}
url:
save_as: {htmlfile}
Template: {template}

{{% notebook notebooks/{notebook_file} cells[{cells}] %}}
"""

INTRO_TEXT = """
This website contains the full text of my free O'Reilly report, [*A Whirlwind Tour of Python*](http://www.oreilly.com/programming/free/a-whirlwind-tour-of-python.csp).

*A Whirlwind Tour of Python* is a fast-paced introduction to essential features of the Python language, aimed at researchers and developers who are already familiar with programming in another language.
The material is particularly designed for those who wish to use Python for data science and/or scientific programming, and in this capacity serves as an introduction to my longer book, [*The Python Data Science Handbook*](http://jakevdp.github.io/PythonDataScienceHandbook).

The content is also available [on Github](https://github.com/jakevdp/WhirlwindTourOfPython) in the form of Jupyter Notebooks, or from O'Reilly site as a [free e-book](http://www.oreilly.com/programming/free/a-whirlwind-tour-of-python.csp) or [free pdf](http://www.oreilly.com/programming/free/files/a-whirlwind-tour-of-python.pdf).

This material is released under the "No Rights Reserved" [CC0 license](https://creativecommons.org/share-your-work/public-domain/cc0/), and thus you are free to re-use, modify, build-on, and enhance this material for any purpose.
"""


def abspath_from_here(*args):
    here = os.path.dirname(__file__)
    path = os.path.join(here, *args)
    return os.path.abspath(path)

NB_SOURCE_DIR = abspath_from_here('..')
NB_DEST_DIR = abspath_from_here('content', 'notebooks')
PAGE_DEST_DIR = abspath_from_here('content', 'pages')


def copy_notebooks():
    nblist = sorted(nb for nb in os.listdir(NB_SOURCE_DIR)
                    if nb.endswith('.ipynb'))
    name_map = {nb: nb.rsplit('.', 1)[0].lower() + '.html'
                for nb in nblist}

    figsource = abspath_from_here('..', 'fig')
    figdest = abspath_from_here('content', 'figures')

    if os.path.exists(figdest):
        shutil.rmtree(figdest)
    shutil.copytree(figsource, figdest)

    figurelist = os.listdir(figdest)
    figure_map = {os.path.join('fig', fig) :
                  os.path.join('/WhirlwindTourOfPython/figures', fig)
                  for fig in figurelist}

    for nb in nblist:
        base, ext = os.path.splitext(nb)
        print('-', nb)

        content = nbformat.read(os.path.join(NB_SOURCE_DIR, nb),
                                as_version=4)

        if nb == 'Index.ipynb':
            cells = '1:'
            template = 'page'
            title = 'A Whirlwind Tour of Python'
            content.cells[3].source = INTRO_TEXT
        else:
            cells = '2:'
            template = 'booksection'
            title = content.cells[2].source
            if not title.startswith('#') or len(title.splitlines()) > 1:
                raise ValueError('title not found in third cell')
            title = title.lstrip('#').strip()

            # put nav below title
            content.cells[0], content.cells[1], content.cells[2] = content.cells[2], content.cells[0], content.cells[1]

        # Replace internal URLs and figure links in notebook
        for cell in content.cells:
            if cell.cell_type == 'markdown':
                for nbname, htmlname in name_map.items():
                    if nbname in cell.source:
                        cell.source = cell.source.replace(nbname, htmlname)
                for figname, newfigname in figure_map.items():
                    if figname in cell.source:
                        cell.source = cell.source.replace(figname, newfigname)
                        
        nbformat.write(content, os.path.join(NB_DEST_DIR, nb))

        pagefile = os.path.join(PAGE_DEST_DIR, base + '.md')
        htmlfile = base.lower() + '.html'
        with open(pagefile, 'w') as f:
            f.write(PAGEFILE.format(title=title,
                                    htmlfile=htmlfile,
                                    notebook_file=nb,
                                    template=template,
                                    cells=cells))

if __name__ == '__main__':
    copy_notebooks()

    
