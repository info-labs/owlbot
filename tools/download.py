#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals


import argparse
import sys
import os

from io import BytesIO
import gzip
import shutil

sys.path.append("./warc/")

import warc

sys.path.append(".")

import owlbot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--output", default="result.warc")

    args = parser.parse_args()


    fp = BytesIO()

    warcfile = warc.WARCFile(fileobj=fp)

    url = args.url.strip()
    # http
    if not url.startswith("http"):
        print('Abort: Unsupported protocol. "{}"'.format(url))
        return 1


    print("download: {}".format(url))
    # get
    code, resp, req = owlbot.get(url)
    if code != 200:
        print("Status {}: {}".format(resp.code, url))
    warcfile.write_record(resp)
    warcfile.write_record(req)

    # write to file
    fp.seek(0)
    if args.output.endswith(".warc.gz"):
        with gzip.open(args.output, "wb") as wfp:
            shutil.copyfileobj(fp, wfp)
    else:
        with open(args.output, "wb") as wfp:
            shutil.copyfileobj(fp, wfp)

    return 0

if __name__ == '__main__':
    sys.exit(main())
