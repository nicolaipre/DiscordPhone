from bs4 import BeautifulSoup
import requests
import discourse
import sys
import time

import discourse

client = discourse.Client(
    host='https://chiefdelphi.com'
)

client.session.headers = []

with open("./CDmarkov.txt", "a") as f:
    for id in range(357888,359888):
        print("Scraping post id={}".format(id))
        time.sleep(0.25)
        try:
            post = client.get_post(id)
        except Exception as e:
            print(e)
            continue #meh
        
        for line in post.raw.splitlines():
            line = line.strip()
            if(line.startswith('[/quote')):
                continue
            elif(line.startswith('[quote=')):
                continue
            elif(line.startswith('```')):
                continue
            else:
                f.write(line + "\n")