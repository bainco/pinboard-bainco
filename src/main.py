#Author: Connor P. Bain
#HW 3
#Added CSS styling and implemented Users API
#Last modified September 14, 2012

import webapp2
import jinja2
import os
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):        
    def get(self):
        currentUser = users.get_current_user()
        imgUrl = self.request.get('imgUrl')
        caption = self.request.get('caption')
        
        template_values = {
            'title': 'Pinboard',
            'imgUrl': imgUrl,
            'caption': caption,
            'user': currentUser,
            'login': users.create_login_url(self.request.uri),
            'logout': users.create_logout_url("/")
            }

        template = jinja_environment.get_template('pinboard.html')   
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)