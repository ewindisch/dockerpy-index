# Copyright 2014 Docker, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import urllib
import urllib2

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser


class DockerIndexRepoPage(HTMLParser):
    def __init__(self):
        self.buffering = False
        self.buf = ''
        self.dockerfile = ''
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag != 'code':
            return
        classes = filter(lambda x: x[0] == 'class', attrs)
        if len(classes) == 1 and classes[0][1] == 'dockerfile':
            self.buffering = True

    def handle_data(self, data):
        if not self.buffering:
            return
        self.buf += data

    def handle_endtag(self, tag):
        if not self.buffering:
            return

        self.dockerfile = self.buf
        self.buf = ''
        self.buffering = False

class DockerIndex(object):
    def search(self, term):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'docker/0.7.5')]
        
        base_url = 'https://index.docker.io'
        path = '/v1/search'

        query = { 'q': term }
        uenc = urllib.urlencode(query)

        url = base_url + path + "?" + uenc
        print url
        resp = opener.open(url)
        return json.loads(resp.read())

    def get_dockerfile(self, repo):
        base_url = 'https://index.docker.io/u/'
        url = base_url + repo + '/'
        opener = urllib2.build_opener()
        try:
            resp = opener.open(url)
        except urllib2.HTTPError:
            return ""

        parser = DockerIndexRepoPage()  #HTMLParser()        
        parser.feed(resp.read())

        print parser.dockerfile
        return parser.dockerfile
