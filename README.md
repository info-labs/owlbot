owlbot
======

[![Build Status](https://travis-ci.org/info-labs/owlbot.svg?branch=master)](https://travis-ci.org/info-labs/owlbot)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

Archive bot

### requirements

* [warc3]
* requests
* dnspython
* lxml

[warc3]: https://github.com/erroneousboat/warc3

### Usage

```python
# require the policy URL for robots User-Agent
import os
policy = "http://example.com/your/crawl/policy"
os.environ["OWLBOT_POLICY"] = policy

import io
import gzip
import shutil
import owlbot

# create WARCFile
filename = "example.warc.gz"
fp = io.BytesIO()
arc = owlbot.Archvie(filename, fileobj=fp)

# crawl & archive web page
resp = arc.get("http://example.com/")
if resp.code == 200:
    for link in resp.links():
        arc.get(link)

# compress data
fp.seek(0)
with gzip.open(filename, "wb") as wfp:
    shutil.copyfileobj(fp, wfp)
```
