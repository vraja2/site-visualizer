#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import re
from google.appengine.api import users


HOME_PAGE_HTML = """\
<html>
    <body>
        <form action="/run_script" method="post">
            http://www.<input type="text" name="content" rows="3" cols="100">
            <div><input type="submit" value="Visualize"/></div>
        </form>
    </body>
</html>
"""

class MainHandler(webapp2.RequestHandler):
    def get(self):
       self.response.write(HOME_PAGE_HTML)

class StupidHandler(webapp2.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write(self.request.get('content'))


app = webapp2.WSGIApplication([
    ('/', MainHandler), ('/hello', StupidHandler) 
], debug=True)
