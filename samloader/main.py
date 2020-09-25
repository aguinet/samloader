# SPDX-License-Identifier: GPL-3.0+
# Copyright (C) 2020 Nayil Mukhametshin

import click
import os
import xml.etree.ElementTree as ET
from clint.textui import progress

from . import request
from . import crypt
from . import fusclient
from . import versionfetch

def getbinaryfile(client, fw, region, model):
    req = request.binaryinform(fw, region, model, client.nonce)
    resp = client.makereq("NF_DownloadBinaryInform.do", req)
    root = ET.fromstring(resp)
    filename = root.find("./FUSBody/Put/BINARY_NAME/Data").text
    path = root.find("./FUSBody/Put/MODEL_PATH/Data").text
    return path, filename

def initdownload(client, filename):
    req = request.binaryinit(filename, client.nonce)
    resp = client.makereq("NF_DownloadBinaryInitForMass.do", req)

@click.group()
def cli():
    pass

@cli.command(help="Check the update server for the latest available firmware.")
@click.argument("model")
@click.argument("region")
def checkupdate(model, region):
    fw = versionfetch.getlatestver(region, model)
    print(fw)

@cli.command(help="Download the specified firmware version.")
@click.argument("version")
@click.argument("model")
@click.argument("region")
@click.argument("out")
def download(version, model, region, out):
    client = fusclient.FUSClient()
    path, filename = getbinaryfile(client, version, region, model)
    initdownload(client, filename)
    if os.path.isdir(out):
        out = os.path.join(out, filename)
        txt = "Downloading"
    if os.path.isfile(out):
        f = open(out, "ab")
        f.seek(0, 2)
        start = f.tell()
        txt = "Resuming download of" 
    else:
        f = open(out, "wb")
        start = None
    print("{} file {}".format(txt,path+filename))
    r = client.downloadfile(path+filename,start)
    length = int(r.headers["Content-Length"])
    if start is not None:
        length -= start
    for chunk in progress.bar(r.iter_content(chunk_size=0x10000), expected_size=(length/0x10000)+1):
        if chunk:
            f.write(chunk)
            f.flush()
    f.close()
    print("Done!")

@cli.command(help="Decrypt enc4 files.")
@click.argument("version")
@click.argument("model")
@click.argument("region")
@click.argument("infile")
@click.argument("outfile")
def decrypt4(version, model, region, infile, outfile):
    key = crypt.getv4key(version, model, region)
    print("Decrypting with key {}...".format(key.hex()))
    length = os.stat(infile).st_size
    with open(infile, "rb") as inf:
        with open(outfile, "wb") as outf:
            crypt.decrypt_progress(inf, outf, key, length)
    print("Done!")

@cli.command(help="Decrypt enc2 files.")
@click.argument("version")
@click.argument("model")
@click.argument("region")
@click.argument("infile")
@click.argument("outfile")
def decrypt2(version, model, region, infile, outfile):
    key = crypt.getv2key(version, model, region)
    print("Decrypting with key {}...".format(key.hex()))
    length = os.stat(infile).st_size
    with open(infile, "rb") as inf:
        with open(outfile, "wb") as outf:
            crypt.decrypt_progress(inf, outf, key, length)
    print("Done!")

if __name__ == "__main__":
    cli()
