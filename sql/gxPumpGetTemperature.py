#!/usr/bin/env python3
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

# import sys
import re
#import mechanicalsoup
import requests
from bs4 import BeautifulSoup

import argparse
import time
from epics import caput  # caget, caput, cainfo

IPs = ['192.168.0.41', '192.168.0.42']
IPdict = {'ST': '192.168.0.41', 'DT': '192.168.0.42'}


def get_temp(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    element = soup.find('script', attrs={'type': 'text/javascript'})
    ele_str = element.string.strip()
#    print(ele_str)
    res = re.findall(r"self.parent.ObjectGaugeUpdate +\(57, +\'number\', +\'(\d+)\'",
                     ele_str)
    resHz = re.findall(r"self.parent.ObjectGaugeUpdate"
                       r" +\(184, +\'number\', +\'(\d+)\'", ele_str)
    print(f"Freq: {int(resHz[0])} Hz")
    return int(res[0])


def get_url(ip):
    return f'http://{ip}/update_sev_gauges.htm'
# browser.open("http://192.168.0.41/update_sev_gauges.htm")
# browser.open("http://192.168.0.41/sev_gauges.htm")


def read_loop(url, pv):
    pv_name = f"Esther:EDW:DryPump-{pv}-Temp"
    while True:
        # html = browser.refresh()
        #try:

        try:
            temp = get_temp(url)
        except KeyboardInterrupt:
            print("KeyboardInterrupt. Stopping")
            caput(pv_name, 'nan')
            exit()
        except Exception:
            caput(pv_name, 'nan')
            print("Can't get page")
        caput(pv_name, temp)
        # caput("Esther:EDW:DryPump-ST-Temp", temp)
        print(f"Temperature {temp} ºC")
        time.sleep(30)  # Sleep seconds


def main(args):
    #browser = mechanicalsoup.StatefulBrowser()

    # print(args.machine)
    url = get_url(args.machine)
    print(url)

    #try:
    #    browser.open(url)
    #    print(get_tempB(url))
    #except Exception:
    #    print(f"Can't find {args.machine}")
    #    exit()

    #  pv_name = "Esther:EDW:DryPump-ST-Temp"
    # caput(pv_name, 'nan')

    # element = html.find('script', attrs={'type': 'text/javascript'})
    # res=re.findall(r"self.parent.ObjectGaugeUpdate +\(57, +\'number\', +\'(\d+)\'", ele_str)
    if (args.single):
        temp = get_temp(url)
        print(f"Temperature {temp} ºC")

    if (args.loop):
        pv = 'ST'
        pv_name = f"Esther:EDW:DryPump-{pv}-Temp"
        caput(pv_name, 'nan')
        read_loop(url, 'ST')

    if (args.print):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        element = soup.find('script', attrs={'type': 'text/javascript'})
        html = element.string.strip()
        print(html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Script to extract temperature from Edwards GX Pumps')
    parser.add_argument('-s', '--single',
                        action='store_true', help='Single run')
    parser.add_argument('-p', '--print',
                        action='store_true', help='Print Html')
    parser.add_argument('-l', '--loop',
                        action='store_true', help='Endless Loop')
    parser.add_argument('-m', '--machine', type=str,
                        help='Gx Dry Pump ip address', default=IPdict['ST'])
    # '192.168.0.41')

    args = parser.parse_args()
    main(args)

# vim: set syntax=python ts=4 sw=4 sts=4 sr et
