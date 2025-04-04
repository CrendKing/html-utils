"""
Parse HTML from stdin and output elements filtered by specified CSS selectors and arguments.
"""

import argparse
import sys
from urllib.parse import urljoin

import bs4

args_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
args_parser.add_argument('selector')
args_parser.add_argument('-a', '--attribute', help='Only output this specified attribute, if present')
args_parser.add_argument('-b', '--base', help='Use this URL as the base for links')
args_parser.add_argument('-t', '--text', action='store_true', help='Only output the text content')
args = args_parser.parse_args()

soup = bs4.BeautifulSoup(sys.stdin, 'html.parser')
results = soup.select(args.selector)


def transform(tag):
    if args.attribute:
        attr_value = tag.get(args.attribute) or ''
        if args.base and tag.name == 'a' and args.attribute == 'href':
            attr_value = urljoin(args.base, attr_value)
        return attr_value
    elif args.text:
        return tag.get_text()
    else:
        return str(tag)


final = [transform(tag) for tag in results]
print(*final, sep='\n')
