from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .models import SpotifyAPI
from django.shortcuts import redirect
from .models import get_spotify_auth, SpotifyAPI, get_user_profile
from .utils import update_or_create_user_tokens
import requests



# def spotify_login(request):
#     scope = 'user-read-private user-read-email'  # Add any additional scopes you need
#     spotify = get_spotify_auth(scope)
#     auth_url = spotify.auth_manager.get_authorize_url()
#     return redirect(auth_url)


# def spotify_callback(request):
#     code = request.GET.get('code')
#     spotify = get_spotify_auth('')
#     token_info = spotify.auth_manager.get_access_token(code)
#     access_token = token_info['access_token']
#     profile_data = get_user_profile(access_token)
#     # Process the profile data as needed
#     name = profile_data['display_name']
#     followers = profile_data['followers']['total']
#     images = profile_data['images'][0]['url']
#     id =  profile_data['id']
#     email =  profile_data['email']

#     kb = {
#         'profile_data' : profile_data,
#         'name' : name,
#         'followers' : followers,
#         'images' : images,
#         'id' : id,
#         'email' : email

#     }
#     return render(request, 'profile.html',kb)


def index(request):
    k = SpotifyAPI('f2af8fbd7de64f10ad8e785ad458e9d1','1472d07084a0418c849ec7aae9155c26')
    d = k.search('remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis&type=playlist&offset=0&limit=1',None,None,'playlist')
    l = d['playlists']
    lst = []
    artist_list = []
    album_list =[]
    playlist = {}
    for i in range(0,6):
        img = d['playlists']['items'][i]['images'][0]['url']
        playlist_name = d['playlists']['items'][i]['name']
        desc = d['playlists']['items'][i]['description']
        link = d['playlists']['items'][i]['external_urls']['spotify']
        playlist = {}
        playlist['image'] = img
        playlist['name'] = playlist_name
        playlist['disc'] = desc
        playlist['link'] = link
        lst.append(playlist)
    
    artist_list.append(k.print_artist('4YRxDV8wJFPHPTeXepOstw'))
    artist_list.append(k.print_artist('1wRPtKGflJrBx9BmLsSwlU'))
    artist_list.append(k.print_artist('4PULA4EFzYTrxYvOVlwpiQ'))
    artist_list.append(k.print_artist('1mYsTxnqsietFxj1OgoGbG'))
    artist_list.append(k.print_artist('4IKVDbCSBTxBeAsMKjAuTs'))
    artist_list.append(k.print_artist('0oOet2f43PA68X5RxKobEy'))

    album_list.append(k.print_album('3HLuAGbNIeDhx1MlR9auER'))
    album_list.append(k.print_album('7BijEioOLwaJFRbJAbbO0q'))
    album_list.append(k.print_album('1HeX4SmCFW4EPHQDvHgrVS'))
    album_list.append(k.print_album('6zCprYy2C6wVdEZomk3mFv'))
    album_list.append(k.print_album('1jfeeOgS84Wm8QzDri8Skh'))
    album_list.append(k.print_album('49g8Aqji0Lw9rTeI5Av4Va'))

    context = {
        'lst' : lst,
        'd' : d,
        'img' : img,
        'playlist_name' : playlist_name,
        'desc' : desc,
        'playlist': playlist,
        'type' : type ,
        'link' : link,
        'artist_list' : artist_list,
        'album_list' : album_list
    }
    return render(request, 'index.html',context)

def search(request):
    return render(request, 'search.html')

def signup(request):
    return render(request, 'signup.html')


def spotify_login(request):
    client_id = 'f2af8fbd7de64f10ad8e785ad458e9d1'
    redirect_uri = 'http://localhost:8000/redirect'
    auth_url = 'https://accounts.spotify.com/authorize'
    scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'  # Add any required scopes
    
    authorization_url = f'{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&show_dialog=true'
    
    return HttpResponseRedirect(authorization_url)


def spotify_callback(request):
    client_id = 'f2af8fbd7de64f10ad8e785ad458e9d1'
    client_secret = '1472d07084a0418c849ec7aae9155c26'
    redirect_uri = 'http://localhost:8000/redirect'
    # redirect_url = request.build_absolute_uri() 
    code = request.GET.get('code')

    print('code is:-',code)
    # print('url is:-',redirect_url)
    
    # Exchange the authorization code for an access token
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    

    response = requests.post(token_url, data=payload)
    response_data = response.json()
    
    access_token = response_data.get('access_token')
    token_type = response_data.get('token_type')
    refresh_token = response_data.get('refresh_token')
    expires_in = response_data.get('expires_in')

    
    # Use the access token to fetch the user profile
    profile_url = 'https://api.spotify.com/v1/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    profile_response = requests.get(profile_url, headers=headers)
    profile_data = profile_response.json()
    
    # Print user details
    print("User details:", profile_data)

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)
    
    # Process the retrieved user profile data as needed
    # ...
    
    return render(request, 'profile.html', {'profile_data': profile_data})





