# -*- coding: utf-8 -*-
import os
from kodi_six import xbmc, xbmcaddon

# XBMC
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = ADDON.getAddonInfo("path")

# Urls
PROXY = "http://127.0.0.1:48996"
M3U_SRC = os.path.join(xbmc.translatePath(
    ADDON.getAddonInfo("profile")), "playlist.m3u")
EPG_SRC = "https://kodi.botallen.com/tv/epg.xml"

# Configs
LANGUAGES = ["Hindi", "English", "Marathi", "Telugu", "Kannada",
             "Tamil", "Punjabi", "Gujarati", "Bengali", "Bhojpuri", "Malayalam"]
