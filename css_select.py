'''
Parse HTML from stdin and output elements filtered by specified CSS selectors and arguments.
'''

from urllib.parse import urljoin
import argparse
import bs4
import sys

parser = argparse.ArgumentParser()
parser.add_argument('selector')
parser.add_argument('-a', '--attribute', help='Only output this specified attribute, if present')
parser.add_argument('-b', '--base', help='Use this URL as the base for links')
parser.add_argument('-t', '--text', action='store_true', help='Only output the text content')

args = parser.parse_args()
soup = bs4.BeautifulSoup(sys.stdin, 'html.parser')
results = soup.select(args.selector)

if args.attribute:
    def transform(tag):
        attr_value = tag.get(args.attribute) or ''
        if args.base and tag.name == 'a' and args.attribute == 'href':
            attr_value = urljoin(args.base, attr_value)
        return attr_value

elif args.text:
    transform = lambda tag: tag.get_text()
else:
    transform = lambda tag: str(tag)

final = (transform(tag) for tag in results)
print(*final, sep='\n')
