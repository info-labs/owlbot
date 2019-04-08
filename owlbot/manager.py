# -*- conding: utf-8 -*-

import os
import sys
import time

from . import rule
from .utility.url import urlparse


class DownloadManager:
    def __init__(self, archive, wait=1, verbose=False):
        self.archive = archive
        self.wait = wait * 1000
        self.last_time = time.process_time()
        self.verbose = verbose
        self.queue = []
        self.done = []
        self.processing = ""
        self.rule = rule.CrawlRule()

    def start(self, url, root=False):
        self.enqueue(url)
        if root:
            ol = urlparse(url)
            self.rule.set_domain(ol.netloc)
            dirname = os.path.dirname(ol.path)
            if not dirname.endswith("/"):
                dirname += "/"
            self.rule.add_follow_path(dirname)

    def enqueue(self, url):
        if url == self.processing:
            return
        if url in self.done:
            return
        if url in self.queue:
            return
        self.queue.append(url)

    def download(self):
        url = self.queue.pop(0)
        self.processing = url
        if self.verbose:
            print("download:", url, file=sys.stderr)
        now = time.process_time()
        # delta: [0, ∞] msec
        delta = now - self.last_time
        if delta < self.wait:
            time.sleep((self.wait - delta) / 1000)  # sec
        self.last_time = time.process_time()
        resp = self.archive.get(url)
        self.done.append(url)
        self.processing = ""
        for link in self.rule.extract_links(resp):
            self.enqueue(link)
        return resp

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.queue) == 0:
            raise StopIteration()
        return self.download()
