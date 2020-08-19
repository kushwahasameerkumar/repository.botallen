# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urlquick
import time
import socket
from functools import wraps
from distutils.version import LooseVersion
from codequick import Script
from resources.lib.constants import PROXY
from xbmc import executebuiltin
from xbmcgui import Dialog, DialogProgress

LOGGEDIN = False


def isLoggedIn(func):
    """
    Decorator to ensure that a valid login is present when calling a method
    """
    @wraps(func)
    def login_wrapper(*args, **kwargs):
        global LOGGEDIN
        if LOGGEDIN is True:
            return func(*args, **kwargs)
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if a_socket.connect_ex(("127.0.0.1", 48996)):
            pDialog = DialogProgress()
            pDialog.create('Jiotv Service', 'Waiting for service to start...')
            for i in range(100):
                if a_socket.connect_ex(("127.0.0.1", 48996)) == 0:
                    break
                if pDialog.iscanceled():
                    return False
                pDialog.update(i)
                time.sleep(1)
            pDialog.close()
        a_socket.close()
        if urlquick.get(PROXY + "/login", max_age=-1, raise_for_status=False).status_code == 200:
            LOGGEDIN = True
            return func(*args, **kwargs)
        else:
            Script.notify(
                'Login Error', 'You need to login with Jio Username and password to use this add-on')
            return False
    return login_wrapper


def check_addon(addonid, minVersion=False):
    """Checks if selected add-on is installed."""
    try:
        curVersion = Script.get_info("version", addonid)
        if minVersion and LooseVersion(curVersion) < LooseVersion(minVersion):
            Script.log('{addon} {curVersion} doesn\'t setisfy required version {minVersion}.'.format(
                addon=addonid, curVersion=curVersion, minVersion=minVersion))
            Dialog().ok("Error", "{minVersion} version of {addon} is required to play this content.".format(
                addon=addonid, minVersion=minVersion))
            return False
        return True
    except RuntimeError:
        Script.log('{addon} is not installed.'.format(addon=addonid))
        if not _install_addon(addonid):
            Dialog().ok("Error",
                        "[B]{addon}[/B] is missing on your Kodi install. This add-on is required to play this content.".format(addon=addonid))
            return False
        return True


def _install_addon(addonid):
    """Install addon."""
    try:
        # See if there's an installed repo that has it
        executebuiltin('InstallAddon({})'.format(addonid), wait=True)

        # Check if add-on exists!
        version = Script.get_info("version", addonid)

        Script.log(
            '{addon} {version} add-on installed from repo.'.format(addon=addonid, version=version))
        return True
    except RuntimeError:
        Script.log('{addon} add-on not installed.'.format(addon=addonid))
        return False
