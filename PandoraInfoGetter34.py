'''
Created on Oct 21, 2016

@author: atorr
'''

import requests
from pip._vendor.distlib.compat import raw_input
from html.parser import HTMLParser
import webbrowser

class LoginException(Exception):
    pass

class MyHtmlParser(HTMLParser):
    
    SONG = "`Encountered-Song"
    
    def __init__(self):
        super(MyHtmlParser, self).__init__()
        self.data = ""
        self.thumb_start_index = 0
    
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if ("infobox-body" in attr[1]):
                self.data += MyHtmlParser.SONG
            elif ("data-nextthumbstartindex" in attr[0]):
                self.thumb_start_index = attr[1]                
                
                
    def handle_data(self, data):
        if data.strip() != "":
            self.data += "~"+data.strip()
        

class PandoraClient(object):
    LOGIN_URL = "https://www.pandora.com/login.vm"
    LIKES_URL = "http://www.pandora.com/content/tracklikes"
    STATIONS_URL = "http://www.pandora.com/content/stations"
    
    def __init__(self, email, password):
        self.session = requests.session()
        
        response = self.session.post(PandoraClient.LOGIN_URL, data={
            "login_username": email,
            "login_password": password
        })
        
        if "0;url=http://www.pandora.com/people/" not in response.text:
            raise LoginException("Pandora login failed, check email and password")
        
    def liked_tracks(self):
        
        like_start_index = 0
        thumb_start_index = 0
        more_pages = True
        page = 1
        with open("Likes.txt", "w+") as f:
            while more_pages:
                response = self.session.get(PandoraClient.LIKES_URL, params={
                    "likeStartIndex": like_start_index,
                    "thumbStartIndex": thumb_start_index
                })
                
                print("\nFetching Pandora Likes page "+str(page)+" ... Likes gathered: "+str(thumb_start_index))
                parser = MyHtmlParser()
                parser.feed(response.text)
                parser.data = parser.data.split("`")
                parser.data.pop(0)
                
                for data in parser.data:
                    data = data.split("~")       
                    song = data[1]
                    artist = data[3]
                    track = song+" - "+artist
                    if (track not in f.read()):
                        f.write(track+"\n")
                        print(track)
                    else:
                        print("Removed duplicate")
                    f.seek(0)
                
                thumb_start_index = parser.thumb_start_index                    
                				
                page += 1
                
                if (thumb_start_index == 0):
                    more_pages = False
        
        f.close()
        
        webbrowser.open("http://www.playlist-converter.net/#/", new=2)
        webbrowser.open("Likes.txt")
		
		
loggingIn = True

while loggingIn:
    print("Sign into your pandora account to get all your likes")
    print("Email:")
    username = raw_input()
    print("Password:")
    password = raw_input()
    try:
        pandoraClient = PandoraClient(username, password)
    except Exception as e:
        print(e)
        print("Login credentials wrong! Try again!")
    else:
        print("Login successful!")
        loggingIn = False
        
pandoraClient.liked_tracks()
    
        
        