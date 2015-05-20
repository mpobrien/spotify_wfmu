import requests
import sys
import time
import re
from BeautifulSoup import BeautifulSoup
import htmlentitydefs
import spotimeta
from pymongo import MongoClient
from jinja2 import Template

out_templ = """
<html>
  <body>
    <table>
      {% for t in tracks %}
        <tr>
          <td>{{t['track']}}</td>
          <td>{{t['artist']}}</td>
          <td><a href="{{t['spotify']['s_href']}}">{{t['spotify']['s_artist']}} : {{t['spotify']['s_title']}}</a></td>
        </tr>
      {% endfor %}
    </table>
  </body>
</html>
"""
templ = Template(out_templ)

extract = lambda keys, dict: reduce(lambda x, y: x.update({y[0]:y[1]}) or x,
                                    map(None, keys, map(dict.get, keys)), {})

db = MongoClient()['spotify_tracks']

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def main(args):
  if not args:
    url = 'http://wfmu.org/playlists/shows/40602'
  else:
    url = args[0]
  tracks = gettracks(url)
  #tracks = spotifytracks(tracks)
  for index, t in enumerate(spotifytracks(tracks)):
    print "got", t
    track_id = url
    trackdoc = dict(artist=t['artist'],
                    title=t['track'],)
    if 'spotify' in t:
      trackdoc.update(dict(spotify=dict(artist=t['spotify']['s_artist'], title=t['spotify']['s_title']),
                      href=t['spotify']['s_href']))
    print trackdoc
    db.tracks.update({"index":index, "url":url}, {"$set":trackdoc}, upsert=True)
    time.sleep(5)

  #print tracks
  #print templ.render(tracks=tracks)

def spotifytracks(tracklist):
  for track in tracklist:
    print "searching spotify for", track['artist'], track['track']
    search = spotimeta.search_track(track['artist'] + " " + track['track'])
    if search["total_results"] > 0:
      topresult = search["result"][0]
      s_artist = ", ".join([a['name'] for a in topresult['artists']])
      s_title = topresult['name']
      s_href = topresult['href']
      track['spotify'] = dict(s_artist=s_artist, s_title=s_title, s_href=s_href)
      yield track
    else:
        print "no results, skipping"
        continue


def gettracks(url):
  r = requests.get(url)
  body = r.content
  soup = BeautifulSoup(body)

  headers = soup.findAll("th")
  real_table = None
  for h in headers:
    if unescape(h.text.strip()).lower().find("artist") >=0:
      real_table = h.parent.parent
      break

  header_mappings = {}
  for i, h in enumerate(real_table.findAll("th")):
    if unescape(h.text.strip()).lower().find("artist") >=0:
      header_mappings['artist'] = i
    elif unescape(h.text.strip()).lower().find("album") >=0:
      header_mappings['album'] = i
    elif unescape(h.text.strip()).lower().find("title") >=0 or unescape(h.text.strip()).lower().find("track") >=0 or unescape(h.text.strip()).lower().find("song") >=0:
      header_mappings['title'] = i

  print header_mappings

  if not real_table:
    print "i couldn't find the table :("
    sys.exit(0)

  tracks = []
  rows = real_table.findAll("tr")
  for row in rows:
    if row.find("th"):
      continue # skip header row
    cols = row.findAll("td")
    if len(cols) < 3:
      continue
    artist = unescape(cols[header_mappings['artist']].text)
    artist = artist.replace(u'\xa0',' ');
    artist = re.sub("\(Listen<!--.*$","", artist, flags=re.DOTALL).strip()

    track = unescape(cols[header_mappings['title']].text)
    track = track.replace(u'\xa0',' ');
    track = re.sub("\(Listen.*$","", track, flags=re.DOTALL).strip()

    album = ""
    if "album" in header_mappings:
      album = unescape(cols[header_mappings['album']].text)
      album = album.replace(u'\xa0',' ').strip();
    tracks.append({"artist":artist, "track":track,"album":album})
  return tracks






if __name__ == '__main__':
  main(sys.argv[1:])
