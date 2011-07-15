
"""
Take an rdf file and update any translations that might be available
for translating.
"""

import os
import glob

from argparse import ArgumentParser

from support import *

def get_args():
    """Get all args taken by this app"""
    parser = ArgumentParser(
        description=(
            "Take an rdf file and run it through the translation machinery."))

    parser.add_argument(
        '-a',
        '--all',
        action='store_const',
        const=True,
        help="implies: translate_rdf cc/licenserdf/licenses/*.rdf")

    parser.add_argument(
        'rdf_file',
        nargs='*')
    return parser.parse_args()


def cli():
    opts = get_args()
    if opts.all:
        opts.rdf_file = glob.glob("cc/licenserdf/licenses/*.rdf")

    if opts.rdf_file:
        count = 0
        for path in opts.rdf_file:
            if not os.path.exists(path):
                print "That filename does not exist."
                return 1
            else:
                graph = load_graph(path)
                translate_graph(graph)
                save_graph(graph, path)
                count += 1
        print "Translated", count, "file(s)."
    else:
        print "You need to pass at least one argument."
