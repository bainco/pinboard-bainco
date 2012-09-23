#Author: Connor P. Bain
#HW 4
#Added Datastore functionality
#Last modified September 23, 2012

import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):        
    def get(self):
        self.setupUser();             
        self.template_values['title'] = "Pinboard"
        self.render("main.html")    
        
    def setupUser(self): 
        self.template_values = {}
        self.currentUser = users.get_current_user()  
        self.template_values['user'] = self.currentUser
        if self.currentUser:
            self.template_values['login'] = ('<a href="/pin">My Pins</a> - <b>%s</b> - <a href="%s">Logout</a>' 
                                             % (self.currentUser.nickname(), users.create_logout_url("/")))
        else:
            self.template_values['login'] = ('<a href="%s">Login</a>' % (users.create_login_url(self.request.uri)))

    def render(self, loadTemplate):
        template = jinja_environment.get_template(loadTemplate)   
        self.response.out.write(template.render(self.template_values))  
        
class BoardHandler(MainPage):        
    def get(self):
        self.setupUser()
        if not self.currentUser:
            self.redirect("/")
            return    
        self.template_values['title'] = 'Your Pins'
        self.template_values['pins'] = Pin.all().filter("owner =", self.currentUser.nickname())
        self.render("pinboard.html")
    
    def post(self):  
        self.setupUser()
        inImgUrl = self.request.get('imgUrl')
        inCaption = self.request.get('caption')
        newPin = Pin(imgUrl=inImgUrl, caption=inCaption, owner=self.currentUser.nickname()) 
        newPin.put()  
        self.redirect("/pin/" + str(newPin.key().id()))
        
class PinHandler(MainPage):
    def get(self): 
        self.setupUser()
        if not self.currentUser:
            self.redirect("/")
            return    
        
        splitUrl = self.request.path.split('/')
        pinID = splitUrl[2]
        if pinID == "":
            self.redirect("/pin")
            return
        
        self.template_values['title'] =  "Pin " + pinID
        self.template_values['pin'] = Pin.get_by_id(int(pinID))
        self.template_values['pinUrl'] = "/pin/" + pinID
        
        self.render("pin.html")            
        
    def post(self):
        self.setupUser()
        splitUrl = self.request.path.split('/')
        pinID = splitUrl[2]
        newPin = Pin.get_by_id(int(pinID)) 
        
        if len(splitUrl) > 3:
            if splitUrl[3] == "d":
                newPin.delete()
                self.redirect("/pin")
                return
        else:    
            newPin.imgUrl = self.request.get('imgUrl')
            newPin.caption = self.request.get('caption')
            newPin.put()
            self.redirect("/pin/" + pinID)  
        
class Pin(db.Model):
    imgUrl = db.StringProperty()
    caption = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    owner = db.StringProperty()
   
app = webapp2.WSGIApplication([('/pin/.*', PinHandler), ('/pin.*', BoardHandler), ('/.*', MainPage)], debug=True)