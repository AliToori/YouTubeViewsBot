#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    *******************************************************************************************
    YouTubeViewsBot: YouTube Views Bot
    Author: Ali Toori, Python Developer [Bot Builder]
    Website: https://boteaz.com
    YouTube: https://youtube.com/@AliToori
    *******************************************************************************************
"""
import concurrent.futures
import json
import logging.config
import os
import random
import smtplib
import ssl
import threading
import urllib.parse
from datetime import datetime
from pathlib import Path
from time import sleep
import os
import ntpath
import zipfile
from selenium import webdriver
import pandas as pd
import pyfiglet
import requests
import urllib3
from django.http import JsonResponse
from py3cw.request import Py3CW
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from streamlink import Streamlink



def get_logger():
    """
    Get logger file handler
    :return: LOGGER
    """
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        'formatters': {
            'colored': {
                '()': 'colorlog.ColoredFormatter',  # colored output
                # --> %(log_color)s is very important, that's what colors the line
                'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
                'log_colors': {
                    'DEBUG': 'green',
                    'INFO': 'cyan',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                },
            },
            'simple': {
                'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
            },
        },
        "handlers": {
            "console": {
                "class": "colorlog.StreamHandler",
                "level": "INFO",
                "formatter": "colored",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": "YouTubeViewsBot.log",
                "maxBytes": 2 * 1024 * 1024,
                "backupCount": 1
            },
        },
        "root": {"level": "INFO",
                 "handlers": ["console", "file"]
                 }
    })
    return logging.getLogger()


PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
file = str(PROJECT_ROOT / 'YouTubeViewsBot.log')


LOGGER = get_logger()


# takes proxies from proxies.txt and returns to list
def create_proxy_list():
    proxy_file = r"BotRes\proxy_list.txt"
    with open(proxy_file, 'r') as f:
        proxy_list = [line.strip() for line in f.readlines()]
    return proxy_list


def get_user_agents():
    file_uagents = r"BotRes\user_agents.txt"
    with open(file_uagents) as f:
        content = f.readlines()
    u_agents_list = [x.strip() for x in content]
    return u_agents_list
    
    
def get_chromedriver(proxy=None, user_agent=None, headless=False):
    driver_bin = 'chromedriver.exe'
    # driver_bin = str(self.PROJECT_ROOT / "SMSRes/bin/chromedriver.exe")
    service = Service(executable_path=driver_bin)
    options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features")
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if proxy is not None:
        proxy_parts = proxy.split(":")
        if len(proxy_parts) == 4:
            ip = proxy_parts[0]
            port = proxy_parts[1]
            username = proxy_parts[2]
            password = proxy_parts[3]
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """
            background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (ip, port, username, password)
            plugin_file = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(plugin_file)
        elif len(proxy_parts) == 2:
            proxy = ":".join(proxy_parts[0:2])
            options.add_argument(f"--proxy-server={proxy}")
    if user_agent is not None:
        options.add_argument(F'--user-agent={user_agent}')
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def wait_until_visible(driver, css_selector=None, element_id=None, name=None, class_name=None, tag_name=None, link_text=None, duration=10000, frequency=0.01):
    if css_selector:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
    elif element_id:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
    elif name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    elif tag_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
    elif link_text:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.LINK_TEXT, link_text)))


user_agents = get_user_agents()


# Watch Twitch Videos or Live Stream
def selenium_watch(proxies):
    for proxy in proxies:
        user_agent = random.choice(user_agents)
        driver = get_chromedriver(proxy=proxy, user_agent=user_agent)
        target_urls = ['https://youtu.be/Cf4pMtQ5PnU', 'https://youtu.be/RoRvs3OHGVY', 'https://youtu.be/9iV4p3PbQN8', 'https://youtu.be/2DVxc4ErGRk', 'https://youtu.be/BVUBGR4n0R4']
        proxy_parts = proxy.split(":")
        proxy = ":".join(proxy_parts[0:2])
        LOGGER.info(f'Watching with proxy: {proxy}')
        for target_url in target_urls:
            driver.get(target_url)
            # Click Remind Me Later button
            try:
                wait_until_visible(driver=driver, css_selector='[id="return-to-youtube"]', duration=5)
                remind_btn = driver.find_element(By.CSS_SELECTOR, '[id="return-to-youtube"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", remind_btn)
                remind_btn.click()
            except:
                try:
                    wait_until_visible(driver=driver, link_text='Remind me later', duration=5)
                    remind_btn = driver.find_element(By.LINK_TEXT, 'Remind me later')
                    driver.execute_script("arguments[0].scrollIntoView(true);", remind_btn)
                    remind_btn.click()
                except:
                    pass
            # Accept Cookies Consent
            try:
                wait_until_visible(driver=driver, css_selector='[aria-label="Accept the use of cookies and other data for the purposes described"]', duration=5)
                accept_btn = driver.find_element(By.CSS_SELECTOR, '[aria-label="Accept the use of cookies and other data for the purposes described"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
                accept_btn.click()
            except:
                try:
                    wait_until_visible(driver=driver, link_text='Accept all', duration=5)
                    accept_btn = driver.find_element(By.LINK_TEXT, 'Accept all')
                    driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
                    accept_btn.click()
                except:
                    pass
            try:
                # Scroll up
                driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.UP)
                wait_until_visible(driver=driver, css_selector='[class="ytp-play-button ytp-button"]', duration=90)
            except:
                try:
                    LOGGER.warning(f'Proxy is down: {proxy}')
                    driver.close()
                    driver.quit()
                    return
                except:
                    pass
            play_button = driver.find_element(By.CSS_SELECTOR, '[class="ytp-play-button ytp-button"]')
            if 'Play' in str(play_button.get_attribute('title')):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", play_button)
                    sleep(5)
                    play_button.click()
                except:
                    try:
                        play_button.send_keys('k')
                    except:
                        pass
            try:
                # Accept Cookies consent
                wait_until_visible(driver=driver, link_text='Accept all', duration=5)
                accept_btn = driver.find_element(By.LINK_TEXT, 'Accept all')
                driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
                accept_btn.click()
            except:
                pass
            wait_until_visible(driver=driver, css_selector='[class="ytp-time-duration"]')
            video_duration = driver.find_element(By.CSS_SELECTOR, '[class="ytp-time-duration"]').text
            if ':' in video_duration:
                time_parts = video_duration.split(":")
                # If duration is in HH:MM:SS
                if len(time_parts) == 3:
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    seconds = int(time_parts[2])
                    video_duration = (hours * 60 * 60) + (minutes * 60) + seconds
                elif len(time_parts) == 2:
                    minutes = int(time_parts[0])
                    seconds = int(time_parts[1])
                    video_duration = (minutes * 60) + seconds
            else:
                video_duration = int(video_duration)
            LOGGER.info(f'Video Duration: {video_duration} secs')
            # Wait until video ends
            sleep(video_duration)
            try:
                driver.close()
                driver.quit()
            except:
                pass
            LOGGER.info(f'Watched full video')


def main():
    # number of viewer bots
    proxy_list = create_proxy_list()
    # chunk = round(len(proxy_list) / 12)
    proxy_chunks = [proxy_list[x:x + 12] for x in range(len(proxy_list))]
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executer:
        executer.map(selenium_watch, proxy_chunks)


if __name__ == '__main__':
    main()
