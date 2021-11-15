import os
from pprint import pprint
import requests as requests
import spotify
import spotipy
from bs4 import BeautifulSoup
import lxml
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from datetime import date

client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://example.com",
                                               scope="playlist-modify-private",
                                               show_dialog=True,
                                               cache_path="token.txt"
                                               ))

id = sp.current_user()["id"]

print(id)

dates = input("What year do you want to travel to? Type the date in this format (YYYY-MM-DD): ")
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{dates}")
day = int(dates.split("-")[2])
month = int(dates.split("-")[1])
year = int(dates.split("-")[0])
dates = date(day=day, month=month, year=year).strftime('%d %B %Y')
soup = BeautifulSoup(response.text, "lxml")
songs = soup.find_all("span", {"class": ["chart-element__information__song"]})
artists = soup.find_all("span", {"class": ["chart-element__information__artist"]})

songDictionary = {}

for song, artist in zip(songs, artists):
    songDictionary[song.get_text()] = artist.get_text()

uriList = []
for value in songDictionary:
    song = value
    artist = songDictionary[value]
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        uriList.append(uri)
    except:
        print(f"{song} by {artist} not found")

name = f"{dates}, Billboard 100"
flag = 0
for song in sp.current_user_playlists()["items"]:
    if song["name"] == name:
        flag = 1
        break

if flag == 0:
    response = sp.user_playlist_create(id, name, public=False, collaborative=False, description='')
    res = sp.playlist_add_items(response["id"], uriList, position=None)
    sp.playlist_change_details(response["id"], public=True)

else:
    print("Play List Exists")
