# -*- coding: utf-8 -*-

import os

from . import version

BASE_DIR = os.path.dirname(__file__)


global POLICY
POLICY = None

def load_policy(path):
    POLICY = "".join(open(path).read().strip().split())

path = os.path.join(BASE_DIR, ".OWLBOT_POLICY")
if os.path.exists(path):
    load_policy(path)
else:
    path = os.path.expanduser("~/.OWLBOT_POLICY")
    if os.path.exists(path):
        load_policy(path)
del path

# overwrite environ
if "OWLBOT_POLICY" in os.environ:
    POLICY = os.environ["OWLBOT_POLICY"]

if POLICY is None:
    raise RuntimeError("OWLBOT_POLICY does't set.")


UA_BASE = "Mozilla/5.0 (compatible;{{comment}} owlbot/{ver} +{policy})".format(ver=version.STR, policy=POLICY)
UA_DEFAULT = UA_BASE.format(comment="")
