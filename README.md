owlbot
======

Archive bot

### requirements

* [warc3]
* requests

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
warcfile = owlbot.create(filename, fp=fp)

# crawl & archive web page
code, response, request = owlbot.get("http://example.com/")
warcfile.write_record(response)
warcfile.write_record(request)

# compress data
fp.seek(0)
with gzip.open(filename, "wb") as wfp:
    shutil.copyfileobj(fp, wfp)
```
