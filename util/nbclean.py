"""
Usage:
    python nbclean.py check [file]
    python nbclean.py clean [file]

    Default is to traverse the entire directory hierarchy
"""
from argparse import ArgumentParser
import sys
import io
import os
import shutil
import tempfile
from IPython.nbformat.current import read, write


def check_notebook(filename):
    """
    Checks a notebook for output cells

    :param nb: opened notebook
    :return: count of non-empty output cells
    """
    with io.open(filename, 'rt') as f:
        nb = read(f, 'json')

        non_empty_cells = 0
        for ws in nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    if len(cell.outputs):
                        non_empty_cells += 1

        if non_empty_cells:
            print '{} non-empty output cells found in {}'.format(non_empty_cells, os.path.basename(filename))
        return non_empty_cells

def clean_notebook(filename):
    """
    Cleans a notebook file

    :param filename: name of ipython notebook file to clean in place
    """
    with tempfile.TemporaryFile(mode='w+t', suffix='nbclean') as temp_fh:
        # copy contents to temporary file
        with io.open(filename, 'rt') as input_fh:
            shutil.copyfileobj(input_fh, temp_fh)

        # parse the notebook
        temp_fh.seek(0)
        nb = read(temp_fh, 'json')

        # remove all output cells in memory
        for ws in nb.worksheets:
            for cell in ws.cells:
                if cell.cell_type == 'code':
                    cell.outputs = []

        # save over the original notebook
        with io.open(filename, 'w', encoding='utf8') as f:
            write(nb, f, 'json')

if __name__ == '__main__':
    # parse command line
    parser = ArgumentParser(
        prog='nbclean',
        description='Cleans or inspects iPython notebooks for output data',
        epilog='Helps control the size of your notebooks for version control',
    )
    subparsers = parser.add_subparsers(dest='command', metavar='command', title=None)
    check_command = subparsers.add_parser('check', help='Check files for output')
    check_command.add_argument('file', nargs='?', default=None)
    clean_command = subparsers.add_parser('clean', help='Remove output in files')
    clean_command.add_argument('file', nargs='?', default=None)

    try:
        args = parser.parse_args()
    except Exception as e:
        print >>sys.stderr, str(e)
        sys.exit(3)

    check_only = args.command == 'check'

    # open the target file
    if args.file:
        if check_only:
            try:
                has_output = (check_notebook(args.file) > 0)
            except Exception as e:
                print >>sys.stderr, str(e)
                sys.exit(2)

            if has_output:
                sys.exit(1)
        else:
            try:
                clean_notebook(args.file)
            except Exception as e:
                print >>sys.stderr, str(e)
                sys.exit(2)
    else:
        # TODO implement directory walk
        print >>sys.stderr, 'Directory traversal not implemented yet'
        sys.exit(4)

    sys.exit(0)
