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

__version__ = "1.0"

import sys

import docopt
import lxml.html
import lxml.etree


def process(query, text):
    if not text:
        return

    if isinstance(text, str):
        text = text.encode()

    try:
        tree = lxml.html.fromstring(text)
    except lxml.etree.ParserError as err:
        print(f"Err: {err}", file=sys.stderr)
        return

    for x in tree.xpath(query):
        if isinstance(x, str):
            x = x.strip()
        else:
            x = lxml.etree.tostring(x, with_tail=False).decode()

        if x:
            yield x


def preprocess(queries):
    for query in queries:
        # Convert css queries to xpath
        if not (query.startswith("//") or query.startswith("@")):
            from cssselect import GenericTranslator, SelectorError
            try:
                query = GenericTranslator().css_to_xpath(query)
            except SelectorError:
                print("Invalid css selector", file=sys.stderr)
                exit(3)

        yield query


def extract(query, xs):
    for x in xs:
        try:
            yield from process(query, x)
        except lxml.etree.XPathEvalError as err:
            print(f"xpath '{query}': {err}", file=sys.stderr)
            exit(4)


def main():
    args = docopt.docopt(__doc__, version=__version__)
    query = args.get("<query>") or ["*"]
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
