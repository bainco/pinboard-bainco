#Author: Connor P. Bain
#HW 8
#Added XHR request handling
#Last modified September 30, 2012

import logging
import webapp2
import jinja2
import json
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
   
    def setupJSON(self, objID):
        self.json = False
        if (self.request.get('fmt') == 'json'):
            self.json = True
        if ('json' in self.request.path.split('.')):
            objID = objID.split('.')[0]
            self.json = True  
        return objID
        
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
        boardID = self.setupJSON(boardID)  

        if boardID == '' and self.currentUser: # GET /pin returns the list of pins
            query = Board.all().filter('owner =', self.currentUser) #Remember: "owner=" won't work!!!
            self.template_values['boards'] = query
            self.template_values['title'] = 'Your Boards'
            self.render('boardlist.html')
            return  
        
        theBoard = self.getBoard(boardID)
        query = Pin.all().filter("owner =", theBoard.owner)
        
        allPins = []
        boardPins = []           
        
        for pin in query:
            if theBoard.key() in pin.boards:
                boardPins.append(pin)
            else:
                allPins.append(pin)
                
        if self.json:
            if self.json:#self.json:
                self.response.out.headers['Content-Type'] = "text/json"
                self.response.out.write(theBoard.json(boardPins))
            return
        self.template_values['boardPins'] = boardPins
        self.template_values['allPins'] = allPins
        self.template_values['board'] = theBoard
        self.template_values['title'] = theBoard.title
        
        self.render('board.html')
                        
    def post(self, boardID):
        self.setupUser()
    
        title = self.request.get('title')
        private = self.request.get('privOpt')
        command = self.request.get('cmd')
        
        if not self.currentUser:
            self.redirect('/')
            return
        
        if boardID == '': #new pin, create it
            if private == "on":
                private = True
            else:
                private = False
            newBoard = Board(title = title, private = private, owner = self.currentUser)
            newBoard.put()   
            newUrl = '/board/%s' % newBoard.id()
            self.redirect(newUrl)
  
        elif command == 'delete': #delete the pin
            logging.info(boardID)
            newBoard = self.getBoard(boardID)
            newBoard.deleteBoard()
            self.redirect('/board/')            
            return
        
        else: #existing pin, update it
            newBoard = self.getBoard(boardID)
            if private:
                if private == "true":
                    private = True 
                else:
                    private = False
                newBoard.private = private            
            newBoard.put()
    
class PinHandler(MainPage):
    def get(self, pinID): 
        self.setupUser()

        pinID = self.setupJSON(pinID)  
        
        if pinID == '' and self.currentUser: # GET /pin returns the list of pins       
            query = Pin.all().filter('owner =', self.currentUser)
            if self.json:
                self.response.out.headers['Content-Type'] = "text/json"
                pins = []
                for pin in query:
                    pins.append(pin.dict())
                self.response.out.write(json.dumps(pins))
                return               
            self.template_values['pins'] = query
            self.template_values['title'] = 'Your Pins'
            self.render('pinlist.html')
            return
        
        thePin = self.getPin(pinID)  
        boards = []
    
        if thePin.private and (self.currentUser != thePin.owner):
            self.redirect("/")
            return
        
        if self.json:#self.json:
            self.response.out.headers['Content-Type'] = "text/json"
            self.response.out.write(json.dumps(thePin.dict()))
            return
        
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
        return
                        
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
    boards = db.ListProperty(db.Key,default=[])
    
    def id(self):
        return self.key().id()
    
    def dict(self):
        thePinDict = {}
        thePinDict['id'] = self.id()
        thePinDict['private'] = self.private
        thePinDict['imgUrl'] = self.imgUrl
        thePinDict['caption'] = self.caption
        return thePinDict
    
class Board(db.Model):
    title = db.StringProperty()
    private = db.BooleanProperty()
    owner = db.UserProperty()
    
    def id(self):
        return self.key().id()
    
    def json(self, boardPins):
        theBoardJSON = {}
        theBoardJSON['id'] = self.id()
        theBoardJSON['private'] = self.private
        theBoardJSON['title'] = self.title
        pinList = []
        for pin in boardPins:
            pinList.append(pin.dict())
        theBoardJSON['pins'] = pinList
        return json.dumps(theBoardJSON)
    
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