import time
import json
import pychromecast
from pychromecast.controllers.spotify import SpotifyController

import spotify_token as st
import spotipy

class CastPlayer:
    def __init__(self, cast_item_name="Basement Desk Speaker"):
        self.cast_item_name = cast_item_name
        self.cast_item = None
        self.mc = None
        self.client = None
        self.spotify_device_id = None
        self.shuffle = False
        self.sp = None

    def get_cast_item(self):
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[self.cast_item_name])
        if len(chromecasts) > 0:
            self.cast_item = chromecasts[0]
            self.cast_item.wait()
            print("Chromecast '{}' found.".format(self.cast_item_name))
        else:
            print("Chromecast '{}' could not be found. Please try again later.".format(self.cast_item_name))

    def connect_spotify(self):
        data = st.start_session(self.read_sp_dc(), self.read_sp_key())
        access_token = data[0]
        expires = data[1] - int(time.time())
        self.client = spotipy.Spotify(auth=access_token)
        self.sp = SpotifyController(access_token, expires)
        self.cast_item.register_handler(self.sp)
        self.sp.launch_app()

        if not self.sp.is_launched and not self.sp.credential_error:
            self.cast_item.media_controller.play_media(self.help_url, "audio/mp3")
            time.sleep(2)
            self.cast_item.wait()
            self.cast_item.register_handler(self.sp)
            self.sp.launch_app()
        elif not self.sp.is_launched and self.sp.credential_error:
            print("Failed to launch Spotify controller due to credential error")

        devices_available = self.client.devices()

        self.spotify_device_id = self.sp.device
        print(self.sp.device)

        if not self.spotify_device_id:
            print('No device with id "{}" known by Spotify'.format(self.sp.device))
            print("Known devices: {}".format(devices_available["devices"]))

    def play(self):
        _status = "OK"
        _statusMessage = ""
        self.client.start_playback(self.spotify_device_id)
        _statusMessage = "Playback has started."
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def next(self):
        _status = "OK"
        _statusMessage = ""
        self.client.next_track(self.spotify_device_id)
        _statusMessage = "Moving to the next track."
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def previous(self):
        _status = "OK"
        _statusMessage = ""
        self.client.previous_track(self.spotify_device_id)
        _statusMessage = "Moving to the previous track."
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def pause(self):
        _status = "OK"
        _statusMessage = ""
        self.client.pause_playback(self.spotify_device_id)
        _statusMessage = "Playback has paused."
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def shuffle(self):
        _status = "OK"
        _statusMessage = ""
        if self.shuffle:
            self.shuffle = False
            _statusMessage = "Shuffle has been turned off."
        else:
            self.shuffle = True
            _statusMessage = "Shuffle has been turned on."
        self.client.shuffle(self.shuffle, self.spotify_device_id)
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def repeat(self, repeat_state):
        _status = "OK"
        _statusMessage = ""
        if repeat_state in ("track", "context", "off"):
            self.client.repeat(repeat_state, self.spotify_device_id)
            _statusMessage = "Repeat has been set to {}.".format(repeat_state)
        else:
            _statusMessage = "Repeat cannot be set to a state of {}.".format(repeat_state)
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def play_item(self, song_url):
        _status = "OK"
        _statusMessage = ""
        print("Song is {}".format(song_url))

        _statusMessage = "Looking for {}.\n".format(self.cast_item_name)
        self.cast_item = None
        self.get_cast_item()
        if self.cast_item is not None:
            self.spotify_device_id = None
            _statusMessage = _statusMessage + "Connecting to Spotify.\n"
            self.connect_spotify()
            if self.spotify_device_id is not None:
                print("Spotify Device = {}".format(self.spotify_device_id))
                if ":track:" in song_url:
                    string_array = [song_url]
                    print("Playing Track = {}".format(song_url))
                    self.client.start_playback(device_id=str(self.spotify_device_id), uris=string_array)
                else:
                    print("Playing Album or Playlist = {}".format(song_url))
                    self.client.start_playback(device_id=str(self.spotify_device_id), context_uri=song_url)
                _statusMessage = _statusMessage + "Playback of {} on {} will be starting shortly.\n".format(song_url, self.cast_item_name)
            else:
                _statusMessage = _statusMessage + "Could not find the Spotify device, cannot play music."
        else:
            _statusMessage = _statusMessage + "Could not find the Chromecast, cannot play music."
        results = {
            "Status": _status,
            "StatusMessage": _statusMessage
        }
        print(_statusMessage)
        return json.dumps(results)

    def read_sp_dc(self):
        with open("sp_dc.txt", "r") as f:
            username = f.read()
            print(username)
            return username

    def read_sp_key(self):
        with open("sp_key.txt", "r") as f:
            password = f.read()
            print(password)
            return password
