#!/usr/bin/python3

# (C) Oliver Diedrich, oliver.die@gmail.com. Feel free to use as you like.
# No warranty at all.

# reads your own google music playlists (but no playlists shared with you)
# and creates identical playlists on spotify

# needs gmusicapi and spotipy, install both with pip3

# ENTER YOUR ACCOUNT DATA BELOW.
# If you're using 2 factor authentication, you need to create an app-specific
# password (https://security.google.com/settings/security/apppasswords)

# On first start, you must allow the spotify access by opening a web site
# (URL is printed by the script) and copying the URL you're redirected to
# the command line  

from gmusicapi import Mobileclient
from spotipy import Spotify
import spotipy.util as util
import sys

# GMUSIC CREDENTIALS
USER = ''     # YOUR GOOGLE ACCOUNT
PASS = ''     # YOUR GOOGLE PASSWORD

# SPOTIFY CREDENTIALS
USERNAME=''   # YOUR SPOTIFY ACCOUNT
SCOPE = 'playlist-modify-public playlist-modify-private'  # privileges
CLIENT_ID = '1a41c7d071714551a0306720148a1aa4'
CLIENT_SECRET = '9fba2d4680fe4516bece23120c67379c'

LIMIT = 50    # max number of hits that a spotify search returns



def filter_hits(hits):
# removes non matching hits (different artist or title)
# hits: list of tracks as returned by spotify search
# returns a list of exactly matching hits
  ret = []                         # list of really matching tracks

  for track in hits['tracks']['items']:
    same_artist = False            # same artist?
    for a in track['artists']:     # may contain several artists
      if a['name'].lower() == artist.lower():
        same_artist = True
    if not same_artist:
      continue
    if track['name'].lower() != title.lower(): # not the same title?
      i = title.find(' (')       # Spotify uses "- ..." instead of "(...)"
      if i > 1:
        if track['name'][:i] != title[:i]:   # same title until first "("?
          continue
      else:
        continue
    ret.append(track)
  return(ret)



# Mobileclient is the simplest gmusicapi interface
gm = Mobileclient()
if not gm.login(USER, PASS, '0123456789abcdef'):
  print('gmusic login for', USER, 'failed')
  sys.exit()

# get authorization token for spotify
token = util.prompt_for_user_token(username=USERNAME,
                              scope=SCOPE,
                              client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET,
                              redirect_uri='https://example.com/callback')
if not token:
  print("Can't get spotify token for", USERNAME)
  sys.exit()
sp = Spotify(auth=token)  # create spotify object

# get all Google Music playlists
playlists = gm.get_all_user_playlist_contents()

# iterate across the Google Music playlists
for pl in playlists:
  print('\n*** Playlist', pl['name'], '***\n')

# create spotify playlist with same name
  spotify_playlist = sp.user_playlist_create(USERNAME,
                                            pl['name'],
                                            public=True)
  spotify_playlist_id = spotify_playlist['id']
  n_tracks = 0          # number of transferred tracks
  missing = []          # list of tracks that couldn't be found on spotify

# iterate across the playlist's tracks
  for tr in pl['tracks']:
    try:                  # track objects might have no title and artist
      title = tr['track']['title']
      artist = tr['track']['artist']
      print(artist, ':', title)
    except:
      missing.append(tr['trackId'])
      continue

# search track on Spotify
    hits = sp.search(artist + ' ' + title, 
                     limit=LIMIT,
                     offset=0,
                     type='track')
    n = hits['tracks']['total']   # number of hits
    print(n, 'hits')
    items = filter_hits(hits)     # remove non matching tracks

    search = 1
    while search*LIMIT < n:       # more then LIMIT results
      hits = sp.search(artist + ' ' + title,
                       limit=LIMIT,
                       offset=search*LIMIT,
                       type='track')
      search += 1
      print('', search*LIMIT, '\r', end='')   # status info
      items += filter_hits(hits)

# print hits and add them to Spotify playlist
    print(len(items), 'matching hits')
    if len(items) == 0:
      missing.append('%s : %s' % (artist, title))
    else:
      n_tracks += 1
      popularity = 0      # use match with the highest popularity ...
      spotify_id = ''     # ... and store it here
      for track in items: # print all matches
        print()
        print('artist:', track['artists'][0]['name'])
        print('name:', track['name'])
        print('duration:', track['duration_ms']/1000)
        print('id:', track['id'])
        print('popularity:', track['popularity'])
        if track['popularity'] >= popularity:
          spotify_id = track['id']
          popularity = track['popularity']
      results = sp.user_playlist_add_tracks(USERNAME,
                                            spotify_playlist_id,
                                            [spotify_id])
    print('----------------------------------')

# print summary
  print(n_tracks, 'tracks transferred,', len(missing), 'not found:')
  for i in missing:
    print(i)

