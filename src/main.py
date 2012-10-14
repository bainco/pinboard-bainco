#Author: Connor P. Bain
#HW 7
#Added XHR request handling
#Last modified September 30, 2012

import logging
import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):        
    def setupUser(self): 
        self.template_values = {}
        self.currentUser = users.get_current_user()  
        self.template_values['user'] = self.currentUser
        if self.currentUser:
            self.template_values['login'] = users.create_logout_url("/")
        else:
            self.template_values['login'] = users.create_login_url(self.request.uri)
        
    def render(self, loadTemplate):
        template = jinja_environment.get_template(loadTemplate)   
        self.response.out.write(template.render(self.template_values))  
    
    def get(self):
        self.setupUser();             
        self.template_values['title'] = "Pinboard"
        self.render("main.html")    
        
    def getPin(self, pinID):
        key = db.Key.from_path('Pin', long(pinID))
        thePin = db.get(key)
        if thePin == None:
            self.redirect('/')
            return None
        return thePin   
    
    def getBoard(self, boardID):
        key = db.Key.from_path('Board', long(boardID))
        theBoard = db.get(key)
        if theBoard == None:
            self.redirect('/')
            return None
        if theBoard.private == True:
            if theBoard.owner != self.currentUser: #not his pin, kick him out.
                return None
        return theBoard   
        
class BoardHandler(MainPage):        
    def get(self, boardID):
        self.setupUser()  
        if boardID == '': # GET /pin returns the list of pins
            if not self.currentUser:
                self.redirect('/')
                return
            query = Board.all().filter('owner =', self.currentUser) #Remember: "owner=" won't work!!!
            self.template_values['boards'] = query
            self.template_values['title'] = 'Your Boards'
            self.render('boardlist.html')
            return  
        
        theBoard = self.getBoard(boardID)
        if not theBoard:
            self.redirect('/')
            return
        query = Pin.all().filter("owner =", theBoard.owner)
        
        allPins = []
        boardPins = []           
        
        for pin in query:
            if theBoard.key() in pin.boards:
                boardPins.append(pin)
            else:
                allPins.append(pin)
        self.template_values['boardPins'] = boardPins
        self.template_values['allPins'] = allPins
        self.template_values['board'] = theBoard
        self.template_values['title'] = theBoard.title
        
        self.render('board.html')
                        
    def post(self, boardID):
        self.setupUser()        
        title = self.request.get('title')
        if self.request.get('private') == "on":
            private = True
        else:
            private = False
            
        aPin = self.request.get('aPin')
        rPin = self.request.get('rPin')
        command = self.request.get('cmd')
        
        if not self.currentUser:
            self.redirect('/')
            return
        if boardID == '': #new pin, create it
            newBoard = Board(title = title, private = private, owner = self.currentUser)
            newBoard.put()   
  
        elif command == 'delete': #delete the pin
            newBoard = self.getBoard(boardID)
            newBoard.deleteBoard()
            self.redirect('/board/')            
            return
        
        else: #existing pin, update it
            newBoard = self.getBoard(boardID)
            newBoard.title = title
            newBoard.private = private
            
            if aPin != "--":
                temp = self.getPin(aPin)
                temp.boards.append(newBoard.key())
                temp.put()
                
            if rPin != "--":
                temp = self.getPin(rPin)
                temp.boards.remove(newBoard.key())
                temp.put()
                        
            newBoard.put()
        newUrl = '/board/%s' % newBoard.id()
        self.redirect(newUrl)
    
class PinHandler(MainPage):
    def get(self, pinID): 
        self.setupUser() 
        if pinID == '' and self.currentUser: # GET /pin returns the list of pins
            query = Pin.all().filter('owner =', self.currentUser) #Remember: "owner=" won't work!!!
            self.template_values['pins'] = query
            self.template_values['title'] = 'Your Pins'
            self.render('pinlist.html')
            return
        
        thePin = self.getPin(pinID)
    
        if thePin.private and (self.currentUser != thePin.owner):
            self.redirect("/")
            return
        
        boards = []
        for key in thePin.boards:
            boards.append(db.get(key))
        
        if self.currentUser == thePin.owner:
            self.template_values['editor'] = True
        else:
            self.template_values['editor'] = False
                 
        self.template_values['pin'] = thePin
        self.template_values['boards'] = boards
        self.template_values['title'] = 'Pin %s' % pinID
        self.render('pin.html')
                        
    def post(self, pinID):
        self.setupUser()
        if not self.currentUser:
            self.redirect('/')
            return     
        
        imgUrl = self.request.get('imgUrl')
        caption = self.request.get('caption')
        command = self.request.get('cmd')
      
        if pinID == '': #new pin, create it
            if self.request.get('privOpt') == "on":
                private = True
            else:
                private = False
            newPin = Pin(imgUrl = imgUrl, caption = caption, private = private, owner = self.currentUser)
            newPin.put()
            newUrl = '/pin/%s' % newPin.id()
            self.redirect(newUrl)
            return
        elif command == 'delete': #delete the pin
            newPin = self.getPin(pinID)
            newPin.delete()
            self.redirect('/pin/')            
            return
        else: #existing pin, update it 
            private = self.request.get('privOpt')
            newPin = self.getPin(pinID)
            if caption:
                newPin.caption = caption
            if private:
                if private == "true":
                    private = True 
                else:
                    private = False
                newPin.private = private
            newPin.put()       

            
class Pin(db.Model):
    imgUrl = db.StringProperty(required=True)
    caption = db.StringProperty(indexed=False)
    date = db.DateTimeProperty(auto_now_add=True)
    owner = db.UserProperty(required=True)
    private = db.BooleanProperty(default=False)
    boards = db.ListProperty(db.Key,default=[]) #references to the pins in this pinboard
    
    def id(self):
        return self.key().id()
    
class Board(db.Model):
    title = db.StringProperty()
    private = db.BooleanProperty()
    owner = db.UserProperty()
    
    def id(self):
        return self.key().id()
    
    def deleteBoard(self):
        query = Pin.all()
        for pin in query:
            if self.key() in pin.boards:
                pin.boards.remove(self.key())
                pin.put()
        self.delete()
        return
    
app = webapp2.WSGIApplication([('/board/(.*)', BoardHandler), ('/board()', BoardHandler),
                               ('/pin/(.*)', PinHandler), ('/pin()', PinHandler), 
                               ('/.*', MainPage)], debug=True)