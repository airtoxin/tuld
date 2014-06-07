#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytumblr
import json
import os
import time

BASE_IMAGE_DIR = "./images"
BASE_UPLOADED_DIR = "./uploaded"
IMAGE_EXT = ["gif", "png", "jpg", "jpeg", "bmp"]

def client_gen(consumer_key, consumer_secret, oauths):
    for oauth in oauths:
        oauth_token = oauth["oauth_token"]
        oauth_token_secret = oauth["oauth_token_secret"]
        client = pytumblr.TumblrRestClient(
            consumer_key,
            consumer_secret,
            oauth_token,
            oauth_token_secret
        )
        client_info = client.info()
        print "Connect to Tumblr '%s'" % client_info["user"]["name"]
        yield client


if __name__ == "__main__":
    setting = json.load(open("setting.json"))
    consumer_key = setting["consumer_key"]
    consumer_secret = setting["consumer_secret"]
    oauths = setting["oauths"]

    imagefiles = [os.path.join(current_dir, filename)
                  for current_dir, directories, filenames in os.walk(BASE_IMAGE_DIR)
                  for filename in filenames
                  if len(filename.split(".")) == 2
                  and filename.split(".")[1] in IMAGE_EXT]

    for client in client_gen(consumer_key, consumer_secret, oauths):
        blog_name = client.info()["user"]["name"]
        try:
            while len(imagefiles) != 0:
                imagefile = imagefiles.pop()
                ret = client.create_photo(
                    blog_name,
                    state="published",
                    data=imagefile
                )
                if ("meta" in ret
                and "status" in ret["meta"]
                and ret["meta"]["status"] == 400):
                    print "! Upload limit for today !"
                    break
                else:
                    print "* Upload complete '%s'" % imagefile
                    os.rename(imagefile, os.path.join(BASE_UPLOADED_DIR, imagefile.split("/")[-1]))
                    time.sleep(1)

        except Exception as e: # upload limit
            print e