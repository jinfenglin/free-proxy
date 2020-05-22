#!/usr/bin/env python3

import random
import sys

import lxml.html as lh
import requests


class FreeProxy:

    def __init__(self, country_id=[], timeout=0.5,
                 protocol_type=('http', 'https'),
                 anonymity=('anonymous', 'transparent', 'elite proxy'),
                 update_time=15 * 60,
                 rand=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonymity = anonymity
        self.update_time = update_time
        self.protocol_type = protocol_type

    def update_time_to_seconds(self, update_time_str):
        parts = update_time_str.split()
        num = int(parts[0])
        unit = parts[1]
        if 'minute' in unit:
            num *= 60
        return num

    def is_valid(self, country_id, https, update_time, anonymity):
        if self.country_id and country_id not in self.country_id:
            return False
        if https not in self.protocol_type:
            return False
        if anonymity not in self.anonymity:
            return False
        if update_time > self.update_time:
            return False
        return True

    def get_proxy_list(self):
        try:
            page = requests.get('https://www.sslproxies.org')
            doc = lh.fromstring(page.content)
            tr_elements = doc.xpath('//*[@id="proxylisttable"]//tr')
            proxies = []
            for i in range(1, 101):
                ip = tr_elements[i][0].text_content()
                port = tr_elements[i][1].text_content()
                country_id = tr_elements[i][2].text_content()
                anonymity = tr_elements[i][4].text_content()
                https = 'https' if tr_elements[i][6].text_content() == 'yes' else 'http'
                update_time_sec = self.update_time_to_seconds(tr_elements[i][7].text_content())
                if self.is_valid(country_id, https, update_time_sec, anonymity):
                    proxy_url = {https: "{}://{}:{}".format(https, ip, port)}
                    proxies.append(proxy_url)
            return proxies
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

    def get(self):
        proxy_list = self.get_proxy_list()
        if self.random:
            random.shuffle(proxy_list)
            proxy_list = proxy_list
        working_proxy = None

        for proxies in proxy_list:
            try:
                if self.check_if_proxy_is_working(proxies):
                    working_proxy = self.check_if_proxy_is_working(proxies)
                    return working_proxy
            except requests.exceptions.RequestException:
                continue

        if not working_proxy:
            if self.country_id is not None:
                self.country_id = None
                return self.get()
            else:
                return 'There are no working proxies at this time.'

    def check_if_proxy_is_working(self, proxies):
        with requests.get('http://www.google.com', proxies=proxies, timeout=self.timeout, stream=True) as r:
            if r.raw.connection.sock:
                return list(proxies.values())[0]
