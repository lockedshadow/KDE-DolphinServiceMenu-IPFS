#!/usr/bin/env python3

import sys
import subprocess
import shlex

import ipfsapi

LOCAL_NODE_ADDRESS = '127.0.0.1'
NODE_API_PORT = 5001
DEFAULT_PUBLIC_GATEWAY = 'https://ipfs.io'

def to_ipfs(selected_file, ipfs_api):
    dbusRef = subprocess.run(shlex.split(
        'kdialog --title IPFS --progressbar "Uploading..." 0'),
        capture_output=True, text=True)
    subprocess.run(['qdbus', *dbusRef.stdout.split(), 'showCancelButton', 'false'])
    ipfs_resource = api.add(selected_file, only_hash=True)
    subprocess.run(['qdbus', *dbusRef.stdout.split(), 'close'])
    
    return ipfs_resource

def format_metadata(ipfs_resource, public_gateway):
    name, cid, size = (ipfs_resource[v] for v in ('Name', 'Hash', 'Size'))
    public_gateway_url ='{}/ipfs/{}'.format(public_gateway, cid)
    metadata_string = '\n'.join((
        '{:<17} {}'.format('Name:', name),
        '{:<17} {}'.format('Size:', size),
        '{:<17} {}'.format('URL:', public_gateway_url),
        '\nThe URL is copied to your clipboard!'))
    
    return metadata_string, public_gateway_url

def show_message(string):
    messagebox = shlex.split('kdialog --title IPFS --msgbox "{}"'.format(string))
    #messagebox = shlex.split('kdialog --title IPFS --textbox -')
    subprocess.run(messagebox, text=True, #input=string,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def to_clipboard(public_gateway_url):
    subprocess.run(shlex.split(' '.join((
        'qdbus org.kde.klipper /klipper setClipboardContents', public_gateway_url))))
    
if __name__ == '__main__':
    filecount = len(sys.argv[1:])
    if filecount > 1:
        subprocess.run(shlex.split(
            'kdialog --title IPFS --sorry\
            "Only one file can be uploaded at this moment, but {} received."'.format(filecount)),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)
    
    try:
        api = ipfsapi.connect(LOCAL_NODE_ADDRESS, NODE_API_PORT)
    except ipfsapi.exceptions.ConnectionError:
        subprocess.run(shlex.split(
            'kdialog --title IPFS --error\
            "Unsuccessful connection attempt to local IPFS node. Maybe it not running?"'),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(1)
    
    ipfs_resource = to_ipfs(sys.argv[1], api)
    metadata_string, public_gateway_url = format_metadata(ipfs_resource, DEFAULT_PUBLIC_GATEWAY)
    
    to_clipboard(public_gateway_url)
    show_message(metadata_string)
