"""
Take an rdf file and update any translations that might be available
for translating.
"""

from argparse import ArgumentParser

def get_args():
    """Get all args taken by this app"""
    parser = ArgumentParser(
        help="Take an rdf file and run it through the translation machinery.")

    parser.add_argument('rdf_file', nargs=1)
    return parser.parse_args()


def cli():
    opts = get_args()
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        print "That filename does not exist."
    graph = load_graph(filename)
    translate_graph(graph)
    save_graph(graph, filename)
    
