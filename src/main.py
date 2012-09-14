#Author: Connor P. Bain
#HW 3
#Added jinja2 templates as well as simple pinning ability.
#Last modified September 7, 2012

import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):        
    def get(self):
        imgUrl = self.request.get('imgUrl')
        caption = self.request.get('caption')
                
        template_values = {
            'title': 'Pinboard',
            'imgUrl': imgUrl,
            'caption': caption
            }
        
        template = jinja_environment.get_template('pinboard.html')
        self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)