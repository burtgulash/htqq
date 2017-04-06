#!/usr/bin/env python3

"""CLI html extractor

Usage:
    htqq --version
    htqq (-h|--help)
    htqq [<query>...]

Options:
    -h --help             Show this screen.
    --version             Show version.
"""

import json
import sys

import docopt
import lxml.html
import lxml.etree

from . import __version__


def preprocess_query(queries):
    for qs in queries:
        qs = filter(None, (x.strip() for x in qs.split("|")))

        # Convert css queries to xpath
        for query in qs:
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
            x = x.xpath(query)
        except lxml.etree.XPathEvalError as err:
            print(f"xpath '{query}': {err}", file=sys.stderr)
            continue
        except AttributeError:
            continue

        if isinstance(x, str):
            x = x.strip()
            if x:
                yield x
        else:
            for y in x:
                if isinstance(y, str):
                    y = y.strip()
                    if y:
                        yield y
                else:
                    yield y


def split_pipeline(ql):
    name, multi, pipeline = None, True, []

    for q in ql:
        if q.endswith(":"):
            yield name, multi, pipeline
            name = q[:-1]
            multi = name.endswith(":")
            if multi:
                name = q[:-1]
            pipeline = []
        else:
            pipeline.append(q)

    yield name, multi, pipeline


def postprocess(x, pretty=False):
    if isinstance(x, str):
        x = x.strip()
    elif isinstance(x, lxml.etree._Element):
        x = lxml.etree.tostring(
            x, encoding="utf-8", with_tail=False, pretty_print=pretty
        ).decode()
    return x


def query(query_list):
    ps = split_pipeline(query_list)
    ps = [(name, multi, list(preprocess_query(p))) for name, multi, p in ps]

    text = sys.stdin.read()
    try:
        parser = lxml.etree.HTMLParser(
            encoding="utf-8", remove_blank_text=True
        )
        tree = lxml.html.fromstring(text, parser=parser)
    except (lxml.etree.ParserError, lxml.etree.XMLSyntaxError) as err:
        print(f"Err: {err}", file=sys.stderr)
        return 3

    initial_pipeline, ps = ps[0][2], ps[1:]
    gen = [tree]
    for query in initial_pipeline:
        gen = extract(query, gen)

    for x in gen:
        try:
            d = postprocess(x, pretty=True) if not ps else {}
            for field, multi, pipeline in ps:
                subgen = [x]
                for subquery in pipeline:
                    subgen = extract(subquery, subgen)

                y = list(map(postprocess, subgen))
                if not multi:
                    if len(y) == 0:
                        y = None
                    else:
                        y = y[0]

                d[field] = y

            json.dump(d, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()
        except Exception as err:
            print("ERR:", err, file=sys.stderr)
            raise


def main():
    try:
        args = docopt.docopt(__doc__, version=__version__)
        # Default query - just echo input (root node)
        query_list = args.get("<query>") or ["/*"]

        sys.exit(query(query_list))
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
