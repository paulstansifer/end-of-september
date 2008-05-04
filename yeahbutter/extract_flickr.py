#from xml import xpath
import sys, urllib2
from elementtree.ElementTree import parse, Element

result = urllib2.urlopen('http://api.flickr.com/services/rest/?method=flickr.test.echo&name=value')

print parse(result)