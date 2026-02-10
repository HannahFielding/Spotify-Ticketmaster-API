from datetime import datetime
import urllib.parse
import time
from flask import Flask, redirect, request, jsonify, session, render_template
import requests
import os

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TICKET_URI_KEY = os.getenv("TICKETMASTER_API_KEY")

REDIRECT_URI = "http://127.0.0.2:8888/callback"
AUTH_URL="https://accounts.spotify.com/authorize"
TOKEN_URL="https://accounts.spotify.com/api/token"
API_BASE_URL="https://api.spotify.com/v1/"
TICKET_URL="https://app.ticketmaster.com/discovery/v2/attractions.json?"

response_type = "code"
app=Flask(__name__)
app.secret_key="hgfh4567EGHSRDgjkgjh778"

@app.route('/')
def index():
    return redirect("/login")



@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-library-read playlist-read-private'
    params = {'client_id': CLIENT_ID,'response_type':'code','scope':scope, 'redirect_uri':REDIRECT_URI,
              'show_dialog':True} #change this to false later to stop the user from logging in every time
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({'error': request.args['error']})
    if 'code' in request.args:
        req_body = {'code': request.args['code'],'grant_type': 'authorization_code','redirect_uri':REDIRECT_URI,'client_id': CLIENT_ID,'client_secret': CLIENT_SECRET}
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token']=token_info['refresh_token']
        session['expires_at']=datetime.now().timestamp()+token_info['expires_in']

        return render_template('text2.html')

@app.route('/submit', methods=['POST'])
def submit():
    num = request.form.get("Number of Top Artists")
    if not num.isdigit():
        return render_template('text2.html')
    artists= list(get_playlists().items())[:int(num)]
    msg = f"Your top artists:\n"
    for artist in artists:
        msg = msg + f"{artist[0]}\n"
    concerts = tickets(artists)
    ms=''
    for a in concerts.items():
        ms = ms + f'{a[0]} Events:\n'
        for li in a[1]:
            ms = ms + f"<li><a href='{li[1]}'>{li[0]}</a></li>\n"
    return render_template("text2.html", concerts=concerts)

@app.route('/tickets')
def tickets(artists):
    concerts={}
    for artist in artists:
        p = {
        "keyword": artist[0],
        "apikey": TICKET_URI_KEY,
        }
        r = requests.get(TICKET_URL, params=p).json()
        p.pop("keyword")
        attractions = r.get("_embedded", {}).get("attractions", [])
        c=[]
        for a in attractions:
            if a.get('id') is not None:
                p.update({'attractionId':a.get('id')})
                e= requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params = p).json().get("_embedded", {})
                if len(e)>0:
                    event = e.get("events", [])[0]
                    USA =False
                    venue = event.get('_links',{}).get("venues", {})
                    for v in venue: # full URL
                        venue_details = requests.get("https://app.ticketmaster.com" + v['href'], params={"apikey": TICKET_URI_KEY}).json()
                        country_code = venue_details.get("country", {}).get("countryCode")
                        if country_code == "US":
                            USA = True
                    if event.get('dates', {}).get('status', {}).get('code') =='onsale' and USA and a.get('url') is not None:
                        c.append((a.get('name'),a.get('url')))
                USA = False
        #c = [(i.get('name'),i.get('url')) for i in attractions if i.get('url') is not None and i.get('upcomingEvents').get('_total') is not 0 and i.get('locale')=='en-us']
        if len(c)>0:
            concerts.update({artist[0]: c})
    return concerts



@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp()>session['expires_at']:
        return redirect('/refresh-token')

    headers = {'Authorization': f'Bearer {session['access_token']}'}
    user = requests.get('https://api.spotify.com/v1/me', headers=headers).json().get('display_name')
    response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
    print(response.status_code)
    print(response.headers.get("Retry-After"))
    playlists = response.json()
    likedsongs = requests.get(API_BASE_URL + 'me/tracks', headers=headers)
    likedsongs=likedsongs.json()
    tracks = []
    for playlist in playlists['items']:
        if playlist.get("owner", {}).get("display_name") == user:
            url = f"{API_BASE_URL}playlists/{playlist['id']}/tracks?limit=100"
            while url is not None:
                response = requests.get(url, headers=headers)
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                     # retry the request
                    response = requests.get(url, headers=headers)
                tracks.extend(response.json()['items'])
                url = response.json().get("next")
    tracks.extend(likedsongs['items'])
    artists=[]
    for info in tracks:
        if info is not None:
            track = info.get('track')
            if track is not None:
                for artist in track.get('artists',[]):
                    artists.append(artist['name']) if artist['name'] is not None else None
    dictionary = {}
    for info in artists:
        if info not in dictionary:
            dictionary[info] = 1
        else:
            dictionary[info] = dictionary[info] + 1
    sorted_dict = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    return sorted_dict

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp()>session['expires_at']:
        req_body = {'grant_type':'refresh_token','refresh_token': session['refresh_token'],'client_id': CLIENT_ID,'client_secret': CLIENT_SECRET}
        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp()+new_token_info['expires_in']
        return redirect('/playlists')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)