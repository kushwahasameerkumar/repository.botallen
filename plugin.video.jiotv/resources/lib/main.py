# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# xbmc imports
from xbmc import executebuiltin
from xbmcaddon import Addon
from xbmcgui import Dialog, DialogProgress

# codequick imports
from codequick import Route, run, Listitem, Script, Resolver
from codequick.utils import keyboard, urlparse, parse_qs
from codequick.script import Settings

# add-on imports
from .utils import isLoggedIn, check_addon, LOGGEDIN
from .constants import M3U_SRC, EPG_SRC, LANGUAGES, PROXY

# additional imports
import urlquick
import sys
import os
import socket
import time
import inputstreamhelper
from datetime import timedelta, date


# Root path of plugin
@Route.register
@isLoggedIn
def root(plugin):
    for e in urlquick.get(PROXY+"/list/root", max_age=1800).json():
        yield Listitem.from_dict(**e)


# Shows Filter options
@Route.register
@isLoggedIn
def show_listby(plugin, by):
    for each in urlquick.get(PROXY+"/list/"+by, max_age=1800).json():
        yield Listitem.from_dict(**each)


# Shows channels by selected filter/category
@Route.register
@isLoggedIn
def show_category(plugin, category_id, id=False):
    fltr = "?id={0}&langs=".format(id) if id else "?langs="
    for x in LANGUAGES:
        try:
            if Settings.get_boolean(x, addon_id="pvr.jiotv"):
                fltr += x + ","
        except:
            fltr = fltr.replace("langs=", "")
            break
        resp = urlquick.get(PROXY+"/list/" +
                            category_id + fltr[:-1], max_age=-1, timeout=60).json()
        for each in resp:
            catchup = each.get("isCatchupAvailable")
            channel_id = each.get("channelId")
            if catchup is not None:
                del each["isCatchupAvailable"]
            if channel_id is not None:
                del each["channelId"]
            litm = Listitem.from_dict(**each)
            if catchup:
                litm.context.container(show_epg, "Catchup", 0, channel_id)
            yield litm


# Shows EPG container from Context menu
@Route.register
@isLoggedIn
def show_epg(plugin, day, channel_id):
    resp = urlquick.get(
        PROXY+"/catchup/{0}/{1}".format(day, channel_id), max_age=-1).json()
    for each in resp:
        yield Listitem.from_dict(**each)
    if int(day) == 0:
        for i in range(-1, -7, -1):
            label = 'Yesterday' if i == - \
                1 else (date.today() + timedelta(days=i)).strftime('%A %d %B')
            yield Listitem.from_dict(**{
                "label": label,
                "callback": show_epg,
                "params": {
                    "day": i,
                    "channel_id": channel_id
                }
            })


# Play `route`
@Resolver.register
def play(plugin, id):
    is_helper = inputstreamhelper.Helper('mpd', drm="com.widevine.alpha")
    if is_helper.check_inputstream():
        # resp = urlquick.get(PROXY+"/playback/%d" % id, max_age=-1).json()[0]
        # if resp.get("isCatchupAvailable") is not None:
        #     del resp["isCatchupAvailable"]
        # if resp.get("channelId") is not None:
        #     del resp["channelId"]
        # executebuiltin("PlayMedia(%s)".format(resp.get("callback")))
        # yield Listitem.from_dict(**resp)
        executebuiltin(
            "PlayMedia(pvr://channels/tv/All channels/pvr.jiotv_{0}.pvr)".format(id))
        return False


# Logout `route` to access from Settings
@Script.register
def logout(plugin):
    LOGGEDIN = False
    urlquick.get(PROXY + "/logout", max_age=-1)


# Log upload `route`
@Script.register
@isLoggedIn
def logupload(plugin, crash=False):
    resp = urlquick.get(
        "{0}/log/upload?crash={1}".format(PROXY, "true" if crash else "false"), raise_for_status=False, max_age=-1)
    if resp.status_code == 200:
        msg = "%sLog uploaded to [B]%s[/B]" % (
            "Crash " if crash else "", resp.text)
    elif resp.status_code == 404:
        msg = "%sLog file missing" % "Crash " if crash else ""
    else:
        msg = "%sLog upload failed" % "Crash " if crash else ""
    Dialog().ok("Jiotv Service Log", msg)
