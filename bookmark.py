#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2014 Cédric Picard
#
# LICENSE
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# END_OF_LICENSE
#
"""
Simple command line browser independant bookmark utility.

Usage: bookmark [options] [-r] URL TAG...
       bookmark [options]  -d  URL
       bookmark [options]  -l  TAG...
       bookmark [options]  -L  TAG...
       bookmark [options]  URL


Arguments:
    URL     The url to bookmark
            If alone, print the sorted tags associated with URL
            If the url corresponds to an existing file,
            the absolute path is substituted to URL
    TAG     The tags to use with the url.
            'all' is a special tag that matches every other tag

Options:
    -h, --help         Print this help and exit
    -r, --remove       Remove TAG from URL
    -d, --delete       Delete an url from the database
    -l, --list-any     List the urls with any of TAG
    -L, --list-every   List the urls with every of TAG
    -f, --file FILE    Use FILE as the database
                       Default is ~/.database
    --no-path-subs     Disable file path substitution
"""

import os
import yaml
from docopt import docopt

def add(database, url, tags):
    if url in database:
        for tag in tags:
            database[url].append(tag)
            database[url].sort()

    else:
        database[url] = list(tags)


def remove(database, url, tags):
    try:
        for tag in tags:
            database[url].remove(tag)
    except ValueError:
        pass


def delete(database, url):
    try:
        database.pop(url)
    except KeyError:
        pass


def list_any(database, tags):
    for url in database:
        if set(tags).intersection(set(database[url])) != set():
            yield url


def list_every(database, tags):
    for url in database:
        if set(tags) == set(database[url]):
            yield url


def list_tags(database, url):
    for each in database[url]:
        yield each


def main():
    args = docopt(__doc__)
    url = args["URL"]
    if os.path.exists(url) and not args["--no-path-subs"]:
        url = os.path.abspath(url)

    d_file = args["--file"] or os.environ["HOME"] + "/.bookmarks"
    try:
        if not os.path.exists(d_file):
            print('The file "' + d_file + '" does not exists: creating it.',
                    file=os.sys.stderr)
            open(d_file, "a+").close()

        database = yaml.load(open(d_file)) or {}

    except PermissionError as e:
        os.sys.exit(e)

    tags = args["TAG"]
    if "all" in [x.lower() for x in tags]:
        tags = set()
        for each in database.values():
            tags = tags.union(set(each))

    if args["--delete"]:
        delete(database, url)
        yaml.dump(database, open(d_file, 'w'))

    elif args["--list-any"]:
        for url in list_any(database, tags):
            print(url)

    elif args["--list-every"]:
        for url in list_every(database, tags):
            print(url)

    elif args["--remove"]:
        remove(database, url, tags)
        yaml.dump(database, open(d_file, 'w'))

    elif args["TAG"]:
        add(database, url, tags)
        yaml.dump(database, open(d_file, 'w'))

    else:
        for tag in list_tags(database, url):
            print(tag)

if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        print("No such bookmark:", e, file=os.sys.stderr)
        os.sys.exit(1)
