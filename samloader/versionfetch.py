# SPDX-License-Identifier: GPL-3.0+
# Copyright (C) 2020 Nayil Mukhametshin

# Get the latest firmware version for a device.

import xml.etree.ElementTree as ET
import requests

def getlatestver(region, model):
    r = requests.get("https://fota-cloud-dn.ospserver.net/firmware/" + region + "/" + model + "/version.xml")
    r.raise_for_status()
    root = ET.fromstring(r.text)
    vercode = root.find("./firmware/version/latest").text
    vc = vercode.split("/")
    if len(vc) == 3:
        vc.append(vc[0])
    if vc[2] == "":
        vc[2] = vc[0]
    return "/".join(vc)
