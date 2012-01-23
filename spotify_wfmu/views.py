from spotify_wfmu import app
from flask import Flask
from flask import render_template, request, jsonify, g, redirect, url_for, session, abort, flash
from spotify_wfmu.models import db
import re, os, sys, json

@app.route("/")
def home():
  tracks = db.tracks.find({}).sort("url");
  return render_template("index.html", tracks=tracks)
