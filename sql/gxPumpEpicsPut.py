#!/usr/bin/python3 -u
"""
Script to extract temperature valuesi from Edwards GX Pumps
 GX600L (HV) Mk5
  Address '192.168.0.41'
    EquipmentName ('igx-000c6d00a18d');
    EquipmentType ('GX600L (HV) Mk5');

  Address '192.168.0.42'
   EquipmentName ('igx-000c6d00a1f5');
   EquipmentType ('');

"""

import re
import requests
from bs4 import BeautifulSoup
import signal

import time
from epics import caput  # caget, caput, cainfo


PV_NAME = "Esther:EDW:DryPump-{}-Temp"

PVs = [{'pv': 'ST', 'ip': '192.168.0.41'},
       {'pv': 'DT', 'ip': '192.168.0.42'}]


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def get_temp(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    element = soup.find('script', attrs={'type': 'text/javascript'})
    ele_str = element.string.strip()
#    print(ele_str)
    res = re.findall(r"self.parent.ObjectGaugeUpdate "
                     r"+\(57, +\'number\', +\'(\d+)\'", ele_str)
    # resHz = re.findall(r"self.parent.ObjectGaugeUpdate"
    #                   r" +\(184, +\'number\', +\'(\d+)\'", ele_str)
    # print(f"Freq: {int(resHz[0])} Hz")
    temp = int(res[0])
    return temp


def get_url(ip):
    return f'http://{ip}/update_sev_gauges.htm'
# browser.open("http://192.168.0.41/update_sev_gauges.htm")
# browser.open("http://192.168.0.41/sev_gauges.htm")


def clear_pvs():
    for p in PVs:
        pv_name = PV_NAME.format(p['pv'])
        caput(pv_name, 'nan')


def read_loop():
    killer = GracefulKiller()
    while not killer.kill_now:
        for p in PVs:
            url = get_url(p['ip'])
            pv_name = PV_NAME.format(p['pv'])
            try:
                temp = get_temp(url)
            except Exception:
                caput(pv_name, 'nan')
                print("Can't get page")
            caput(pv_name, temp)
            print(f"{pv_name} Temper {temp} ºC")
        time.sleep(30)  # Sleep seconds

    # print("KeyboardInterrupt. Stopping")
    clear_pvs()
    print("End of the program gxPumpEpicsPut.py. Killed gracefully :)")


if __name__ == '__main__':
    clear_pvs()
    read_loop()

# vim: set syntax=python ts=4 sw=4 sts=4 sr et
