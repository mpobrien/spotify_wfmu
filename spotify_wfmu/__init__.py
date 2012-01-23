from flask import Flask
app = Flask(__name__)
#app.debug = True

#MONGODB_HOST = 'localhost'
#MONGODB_PORT = 27017

app.config.from_object(__name__)
import spotify_wfmu.views
import spotify_wfmu.models
import spotify_wfmu.forms

