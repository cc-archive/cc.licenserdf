
from rdflib import Namespace, Literal
from rdflib.Graph import Graph

NS_FOAF = Namespace("http://xmlns.com/foaf/0.1/")
NS_EXIF = Namespace("http://www.w3.org/2003/12/exif/ns#")

index = Graph()
index.bind("cc", "http://creativecommons.org/ns#")
index.bind("dc", "http://purl.org/dc/elements/1.1/")
index.bind("dcq","http://purl.org/dc/terms/")
index.bind("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
index.bind("foaf","http://xmlns.com/foaf/0.1/")
index.load('./rdf/index.rdf')

output = Graph()
output.bind("foaf","http://xmlns.com/foaf/0.1/")
output.bind("exif","http://www.w3.org/2003/12/exif/ns#")

for img in index.objects(None, NS_FOAF.logo):
    print img
    width, height = img[:-len('.png')].split('/')[-1].split('x')
    output.add( (img, NS_EXIF.width, Literal(width)) )
    output.add( (img, NS_EXIF.height, Literal(height)) )

file('./rdf/images.rdf', 'w').write(
    output.serialize(format="pretty-xml", max_depth=2))
