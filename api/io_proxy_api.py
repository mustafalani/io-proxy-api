#!flask/bin/python
# -*- coding: utf-8 -*-

# This file is part of iohub publisher.
# ------------------------------------------------------------------------------
# iopublisher api proxy
# ------------------------------------------------------------------------------

import os, configparser, subprocess, json, yaml
import xml
from pathlib import Path
from shutil import copyfile
from flask import Flask, jsonify, request, abort, make_response, Response
import urllib.request
import requests
import xml.etree.ElementTree as ET


app = Flask(__name__)
#app.run(host='0.0.0.0')

# ----------------------
# system configuration
# ----------------------
with open(r'conf.yml') as configfile:
    configuration = yaml.load(configfile, Loader=yaml.FullLoader)
    base_endpoint = configuration['server']['base_endpoint']
    serverName = configuration['server']['server_name']

# ----------------------
# Root
# ----------------------
@app.route('/')
def index():
    return "iohub Publishing Engine 1 - api proxy v1.0"

# ----------------------
# system configuration
# ----------------------
# Return Default system configuration
@app.route(base_endpoint , methods=['GET'])
def getServerConfig():
    with open(r'conf.yml') as config_file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        server_config = yaml.load(config_file, Loader=yaml.FullLoader)
        return jsonify(server_config)


# ----------------------
# Applications
# ----------------------
# Applications : Retrieves the list of Applications for the specifed server
# GET: get /v2/servers/{serverName}/vhosts/{vhostName}/applications0
@app.route(base_endpoint + 'applications', methods=['GET'])
def getApplications():
    response = requests.get('http://127.0.0.1:8000/applications/')
    root = ET.fromstring(response.content)
    import xml.etree.ElementTree as etree
    xml_root = etree.Element('Applications')
    xml_root.set('serverName', serverName)
    for app in root.findall('*'):
        app_name = app.find('name')
        app_href = base_endpoint + 'applications/' + app_name.text
        app_description = app.find('description')
        app_type = app.find('type')
        xml_items = etree.SubElement(xml_root, 'Application')
        xml_items.set('id', app_name.text)
        xml_items.set('href', app_href)
        xml_app_type = etree.Element('AppType')
        xml_app_type.text = app_type.text
        xml_items.append(xml_app_type)
        xml_app_description = etree.Element('Description')
        xml_app_description.text = app_description.text
        xml_items.append(xml_app_description)
    doc_type = '<?xml version="1.0" encoding="UTF-8" ?>'
    _tostring = etree.tostring(xml_root).decode('utf-8')
    xml_out = (f"'{doc_type}{_tostring}'").replace('\'', '')
    return Response(xml_out, mimetype='text/xml')


# Applications : Retrieves the specified Application configuration
# GET: get /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}
@app.route(base_endpoint + 'applications/<name>', methods=['GET'])
def getApplication(name):
    response = requests.get('http://127.0.0.1:8000/applications/?name=' + name)
    root = ET.fromstring(response.content)
    import xml.etree.ElementTree as etree
    xml_root = etree.Element('Application')
    xml_root.set('serverName', serverName)
    for app in root.findall('*'):
        app_name = app.find('name')
        app_description = app.find('description')
        app_type = app.find('type')
        xml_item_name = etree.Element('Name')
        xml_item_name.text = app_name.text
        xml_root.append(xml_item_name)
        xml_item_type = etree.Element('AppType')
        xml_item_type.text = app_type.text
        xml_root.append(xml_item_type)
        xml_item_description = etree.Element('Description')
        xml_item_description.text = app_description.text
        xml_root.append(xml_item_description)
    doc_type = '<?xml version="1.0" encoding="UTF-8" ?>'
    _tostring = etree.tostring(xml_root).decode('utf-8')
    xml_out = (f"'{doc_type}{_tostring}'").replace('\'', '')
    return Response(xml_out, mimetype='text/xml')


# Applications : Adds an Application to the list of Applications for the specifed vhost
# post /v2/servers/{serverName}/vhosts/{vhostName}/applications/





if __name__ == '__main__':
    app.run(debug=False)
    app.run(host='0.0.0.0')
