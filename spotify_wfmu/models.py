from spotify_wfmu import app
from flask import Flask
#from pymongo.objectid import Object
from pymongo import MongoClient
db = MongoClient()['spotify_tracks']


