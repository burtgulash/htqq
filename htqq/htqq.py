#!/usr/bin/env python3

"""CLI html extractor

Usage:
    htqq --version
    htqq (-h|--help)
    htqq [options] [<query>...]

Options:
    -l                    One html per line.
    -h --help             Show this screen.
    --version             Show version.
"""

import sys

import docopt
import lxml.html
import lxml.etree

from . import __version__


def process(query, text):
    if not text:
        return

    try:
        parser = lxml.etree.HTMLParser(
            encoding="utf-8", remove_blank_text=True
        )
        tree = lxml.html.fromstring(text, parser=parser)
    except lxml.etree.ParserError as err:
        print(f"Err: {err}", file=sys.stderr)
        return

    for x in tree.xpath(query):
        if isinstance(x, str):
            x = x.strip()
        else:
            x = lxml.etree.tostring(
                x, encoding="utf-8", with_tail=False,
            ).decode()

        if x:
            yield x


def preprocess(queries):
    for query in queries:
        # Convert css queries to xpath
        if not (query.startswith("//") or query.startswith("@")):
            from cssselect import GenericTranslator, SelectorError
            try:
                # Try to interpret the selector as css
                query = GenericTranslator().css_to_xpath(query)
            except SelectorError:
                # Else fallback to xpath
                pass

        yield query


def extract(query, xs):
    for x in xs:
        try:
            yield from process(query, x)
        except lxml.etree.XPathEvalError as err:
            print(f"xpath '{query}': {err}", file=sys.stderr)
            exit(4)


def do():
    args = docopt.docopt(__doc__, version=__version__)
    query = args.get("<query>") or ["/*"]  # Default query - print itself
    lines = args.get("-l")

    if lines:
        gen = iter(sys.stdin)
    else:
        gen = [sys.stdin.read()]

    for query in preprocess(query):
        gen = extract(query, gen)

    for x in gen:
        try:
            sys.stdout.write(x)
            sys.stdout.write("\n")
            sys.stdout.flush()
        except:
            pass


def main():
    try:
        do()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
