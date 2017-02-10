# -*- coding: utf-8 -*-

import os

from . import version

BASE_DIR = os.path.dirname(__file__)


POLICY = None

if "OWLBOT_POLICY" in os.environ:
    POLICY = os.environ["OWLBOT_POLICY"]

__POLICY_FILE = os.path.join(BASE_DIR, ".OWLBOT_POLICY")
if os.path.exists(__POLICY_FILE):
    POLICY = "".join(open(__POLICY_FILE).read().strip().split())

if POLICY is None:
    raise RuntimeError("OWLBOT_POLICY does't set.")


UA_BASE = "Mozilla/5.0 (compatible;{{comment}} owlbot/{ver} +{policy})".format(ver=version.STR, policy=POLICY)
UA_DEFAULT = UA_BASE.format(comment="")
