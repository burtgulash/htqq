#!/usr/bin/env python3

"""CLI html extractor

Usage:
    htqq --version
    htqq (-h|--help)
    htqq [-lj] [<query>...]

Options:
    -l                    One html per line.
    -j                    Output as json snippets.
    -h --help             Show this screen.
    --version             Show version.
"""

import json
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

    y = tree.xpath(query)
    if isinstance(y, str):
        yield y
        return

    for x in y:
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

def split_pipeline(ql):
    name, pipeline = None, []

    for q in ql:
        if q.endswith(":"):
            yield name, pipeline
            name, pipeline = q[:-1], []
        else:
            pipeline.append(q)

    yield name, pipeline


def do():
    args = docopt.docopt(__doc__, version=__version__)
    query = args.get("<query>") or ["/*"]  # Default query - print itself
    lines = args.get("-l")
    as_json = args.get("-j")

    if lines:
        gen = iter(sys.stdin)
    else:
        gen = [sys.stdin.read()]

    ps = split_pipeline(query)
    ps = [(name, list(preprocess(p))) for name, p in ps]

    initial_pipeline, ps = ps[0][1], ps[1:]
    for query in initial_pipeline:
        gen = extract(query, gen)

    for x in gen:
        try:
            d = x if not ps else {}
            for field, pipeline in ps:
                subgen = [x]
                for subquery in pipeline:
                    subgen = extract(subquery, subgen)

                y = list(subgen)
                if len(y) == 0:
                    y = None
                elif len(y) == 1:
                    y = y[0]

                d[field] = y

            json.dump(d, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()
        except:
            pass


def main():
    try:
        do()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
