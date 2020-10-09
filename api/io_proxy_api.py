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
    api_proxy_url = configuration['api_proxy_server']['api_proxy_url']
    #/v2/servers/_defaultServer_/vhosts/_defaultVHost_/
    serverName = configuration['api_proxy_server']['server_name']
    apiUrl = configuration['publisher-engine']['api_url']
    apiPort = str(configuration['publisher-engine']['port'])
    versoin = str(configuration['api_proxy_server']['version'])

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
@app.route(api_proxy_url , methods=['GET'])
def getServerConfig():
    with open(r'conf.yml') as config_file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        server_config = yaml.load(config_file, Loader=yaml.FullLoader)
        return jsonify(server_config)


# ----------------------
# Applications
# ----------------------
# Applications - Retrieve all apps: Retrieves the list of Applications for the specifed server
# GET: get /v2/servers/{serverName}/vhosts/{vhostName}/applications
@app.route(api_proxy_url + 'applications', methods=['GET'])
def getApplications():
    response = requests.get(apiUrl + ':' + apiPort + '/applications/')
    root = ET.fromstring(response.content)
    import xml.etree.ElementTree as etree
    xml_root = etree.Element('Applications')
    xml_root.set('serverName', serverName)
    for app in root.findall('*'):
        app_name = app.find('name')
        app_href = api_proxy_url + 'applications/' + app_name.text
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


# Applications - Retrieve app: Retrieves the specified Application configuration
# GET: get /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}
@app.route(api_proxy_url + 'applications/<name>', methods=['GET'])
def getApplication(name):
    response = requests.get(apiUrl + ':' + apiPort + '/applications/' + name)
    if response.status_code == 404:
        xml_out = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><error><code>404</code><message>The server has not found anything matching the request URI</message></error>"
        return Response(xml_out, status=404,  mimetype='text/xml')
    else:
        response = requests.get(apiUrl + ':' + apiPort + '/applications/?name=' + name)
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


# Applications - Add App: Adds an Application to the list of Applications for the specifed vhost
# POST: /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}
@app.route(api_proxy_url + 'applications/<name>', methods=['POST'])
def addApplication(name):
    if not request.json or not 'name' in request.json:
        abort(400)
    app_name = request.json['name']
    app_type = request.json['appType']
    app_description = request.json['description']
    req_url = apiUrl + ':' + apiPort + '/applications/'
    import xml.etree.ElementTree as etree
    xml_root = etree.Element('root')
    xml_item_name = etree.Element('name')
    xml_item_name.text = app_name
    xml_root.append(xml_item_name)
    xml_item_type = etree.Element('type')
    xml_item_type.text = app_type
    xml_root.append(xml_item_type)
    xml_item_description = etree.Element('description')
    xml_item_description.text = app_description
    xml_root.append(xml_item_description)
    doc_type = '<?xml version="1.0" encoding="UTF-8" ?>'
    _tostring = etree.tostring(xml_root).decode('utf-8')
    xml_data = (f"'{doc_type}{_tostring}'").replace('\'', '')
    headers = {'Content-Type': 'application/xml'}
    # Give the object representing the XML file to requests.post.
    r = requests.post(req_url, headers=headers, data=xml_data)
    if r.status_code == 201:
        return Response(r.text, mimetype='text/xml'), 201
    elif r.status_code == 400 and 'application with this name already exists' in r.text:
        return Response(r.text, mimetype='text/xml'), 400
    else:
        return Response(r.text, mimetype='text/xml'), 404


# Applications - Add app adv config: Adds the specified advanced Application configuration
# POST: /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}/adv
@app.route(api_proxy_url + 'applications/<name>/adv', methods=['POST'])
def addApplicationAdv(name):
    r = name
    return (r, 200)


# Applications - Delete App: Delete an Application from the list of Applications for the specifed vhost
# DEL: /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}
@app.route(api_proxy_url + 'applications/<name>', methods=['DELETE'])
def deleteApplication(name):
    app_name = name
    req_url = apiUrl + ':' + apiPort + '/applications/' + app_name
    r = requests.delete(req_url)
    if r.status_code == 204:
        return Response('The application ' + app_name + ' has been deleted', mimetype='text/xml'), 200
    elif r.status_code == 404 and 'Not found.' in r.text:
        return Response(r.text, mimetype='text/xml'), 404
    else:
        return Response(r.text, mimetype='text/xml'), 400


# Applications - Update App: Update an Application in the list of Applications for the specifed vhost
# PUT: /v2/servers/{serverName}/vhosts/{vhostName}/applications/{appName}


# ----------------------
# Server
# ----------------------
# Server -  Server status
# GET: /v2/servers/_defaultServer_/status
@app.route('/v2/servers/_defaultServer_/status', methods=['GET'])
def getServerStatus():
    encoding = 'utf-8'
    hostname= str(subprocess.Popen('hostname', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0], encoding).replace("\n","")
    uptime = str(subprocess.Popen("uptime | awk -F ',' ' {print $1} ' | awk ' {print $3} ' | awk -F ':' ' {hrs=$1; min=$2; print hrs*24*3600 + min} '", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0], encoding).replace("\n","")
    os = str(subprocess.Popen('lsb_release -a', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0], encoding).replace("\n","")
    import xml.etree.ElementTree as etree
    xml_root = etree.Element('ServerStatus')
    xml_root.set('serverName', serverName)
    apiversion = etree.SubElement(xml_root, 'Version')
    apiversion.text = versoin
    iohubpubname = etree.SubElement(xml_root, 'ioPubName')
    iohubpubname.text = hostname
    timerunning = etree.SubElement(xml_root, 'TimeRunning')
    timerunning.text = uptime
    osversion = etree.SubElement(xml_root, 'OSVersion')
    osversion.text = os
    doc_type = '<?xml version="1.0" encoding="UTF-8" ?>'
    _tostring = etree.tostring(xml_root).decode('utf-8')
    xml_out = (f"'{doc_type}{_tostring}'").replace('\'', '')
    return Response(xml_out, mimetype='text/xml')
###
# Server - restart nginx status
# PUT: v2/servers/_defaultServer_/actions/restart
@app.route('/v2/servers/_defaultServer_/actions/restart', methods=['PUT'])
def restart():
    restart_cmd = "ls"
    output = subprocess.Popen(restart_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    print(output.returncode)

if __name__ == '__main__':
    app.run(debug=False)
    app.run(host='0.0.0.0')
