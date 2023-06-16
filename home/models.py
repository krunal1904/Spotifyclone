from django.db import models
import base64
import datetime
from urllib.parse import urlencode
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import requests
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.utils import timezone


# Create your models here.
class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    refresh_token = models.CharField(max_length=250)
    access_token = models.CharField(max_length=250)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)


class SpotifyAPI(object):
    access_token = 'access token'
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def base_search(self, query_params):  # type
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)
    
    def print_artist(self,id):
        artist_dict = {}
        s = self.get_artist(id)
        name = s['name']
        type = s['type']
        image = s['images'][2]['url']
        link = s['external_urls']['spotify']
        artist_dict['name'] = name
        artist_dict['type'] = type
        artist_dict['image'] = image
        artist_dict['link'] = link
        return artist_dict
    
    def print_album(self,id):
        import re
        album_dict = {}
        s = self.get_album(id)
        album_name = s['name']
        album_artist = s['artists'][0]['name']
        image = s['images'][1]['url']
        link = s['external_urls']['spotify']
        date = s['release_date']
        t = re.search('\d{% s}'% 4, date)
        year = (t.group(0) if t else '')
        album_dict['album_name'] = album_name
        album_dict['album_artist'] = album_artist
        album_dict['image'] = image
        album_dict['link'] = link
        album_dict['year'] = year
        return album_dict

def get_spotify_auth(scope):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=settings.SPOTIFY_CLIENT_ID,client_secret=settings.SPOTIFY_CLIENT_SECRET,
                                                     redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                                                     scope=scope))

def get_user_profile(access_token):
    spotify = spotipy.Spotify(access_token)
    return spotify.me()


k = SpotifyAPI('f2af8fbd7de64f10ad8e785ad458e9d1','1472d07084a0418c849ec7aae9155c26')
