#!flask/bin/python
import os
import configparser
from pathlib import Path
from shutil import copyfile
from flask import Flask, jsonify, request, abort

app = Flask(__name__)
app.run(host='0.0.0.0')

@app.route('/')
def index():
    return "ffplayout engine v1.0"

@app.route('/api/v1/config', methods=['GET'])
def getConfig():
        # Read config file
        config = configparser.ConfigParser()
        config.read('../ffplayout.conf')
        log_path = config.get("LOGGING", "log_file")
        text = config.get("TEXT", "textfile")
        logo = config.get("PRE_COMPRESS", "logo")
        out = config.get("OUT","out_addr")
        return jsonify("default settings","log_path:",log_path,"output name:",out,"text file:",text,"logo:",logo)

@app.route('/api/v1/playlist', methods=['POST'])
def addPlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        playlist = request.json['playlistid']
        if not os.path.isdir('../playlists'):
                os.makedirs('../playlists')
        if not os.path.isdir('../playlists/config'):
                os.makedirs('../playlists/config')
        if not os.path.isdir('../playlists/text'):
                os.makedirs('../playlists/text')
        if not os.path.isdir('../playlists/logos'):
                os.makedirs('../playlists/logos')
        if not os.path.isdir('../playlists/logs'):
                os.makedirs('../playlists/logs')
        config = configparser.ConfigParser()
        config.read('../ffplayout.conf')
        # set variables
        config.set('LOGGING', 'log_file', './playlists/logs/' + playlist + '.log')
        config.set('TEXT', 'textfile', './playlists/text/' + playlist + '.txt')
        config.set('PRE_COMPRESS', 'logo', './playlists/logos/' + playlist + '.png')
        config.set('OUT', 'out_addr', playlist)
        # save new config file
        with open('../playlists/config/' + playlist + '.conf', 'w') as configfile:
                config.write(configfile)
                configfile.close()
        Path('../playlists/text/' + playlist + '.txt').touch()
        Path('../playlists/logs/' + playlist + '.log').touch()
        copyfile('../logo.png', '../playlists/logos/' + playlist + '.png')
        return jsonify('playlist configuration saved'), 201

@app.route('/api/v1/playlist', methods=['PUT'])
def updatePlaylistConfig():
        if not request.json or not 'playlistid' in request.json:
                abort(400)
        current_playlist = request.json['playlistid']
        new_playlist = request.json['newplaylistid']
        config = configparser.ConfigParser()
        config.read('../playlists/config/' + current_playlist + '.conf')
        # set variables
        config.set('LOGGING', 'log_file', './playlists/logs/'+ new_playlist + '.log')
        config.set('TEXT', 'textfile', './playlists/text/'+ new_playlist + '.txt')
        config.set('PRE_COMPRESS', 'logo', './playlists/logos/' + new_playlist + '.png')
        config.set('OUT', 'out_addr', new_playlist)
        # save new config file
        with open('../playlists/config/' + new_playlist + '.conf', 'w') as configfile:
                config.write(configfile)
                configfile.close()
        Path('../playlists/logs/' + new_playlist + '.log').touch()
        Path('../playlists/text/' + new_playlist + '.txt').touch()
        copyfile('../playlists/logos/' + current_playlist + '.png', '../playlists/logos/' + new_playlist + '.png')
        os.remove('../playlists/config/' + current_playlist + '.conf')
        os.remove('../playlists/text/' + current_playlist + '.txt')
        os.remove('../playlists/logs/' + current_playlist + '.log')
        os.remove('../playlists/logos/' + current_playlist + '.png')
        return jsonify('playlist configuration updated'), 201

if __name__ == '__main__':
    app.run(debug=False)
    app.run(host='0.0.0.0')
