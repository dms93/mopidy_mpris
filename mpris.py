#!/usr/bin/env python3

from pydbus import SessionBus
from gi.repository import GLib

import os
import time
import signal
import subprocess
import sys

DEBUG = 0

OBJECT_PATH = '/org/mpris/MediaPlayer2'
BUS_NAME = 'org.mpris.MediaPlayer2.mopidy'
INTERFACE_PROPERTIES = 'org.freedesktop.DBus.Properties'
SIGNAL = 'PropertiesChanged'

SONG_INFO_FILE="/tmp/.song"
status = None

def wait_mopidy(bus):
  if bus == None:
    return

# Waiting for mopidy to start
  while True:
    try:
      mopidy = bus.get(BUS_NAME, OBJECT_PATH)
    except GLib.Error:
      if DEBUG == 1: print("Mopidy service is not running");

      try:
        time.sleep(1)
      except KeyboardInterrupt:
        return None

      continue
    return mopidy


def split_url(xesam_url):
  if xesam_url == None: return None

  split_url = xesam_url.split(":")
  provider = split_url[0]

  if provider == "file":
    url = split_url[1][2:]
  else:
    url = split_url[2]

  return { "provider" : provider, "url" : url }

def update_status(sender, object_path, iface, signal_name, object):
  global status
  update_bar = ['pkill', '-SIGRTMIN+1', 'i3blocks']

  if status == object: return
  if len(object[1]) <= 1: return

  if DEBUG == 1: print("\n\n", object)

  song_info = "MOPIDY_STATUS=\"" + object[1]['PlaybackStatus'] + "\"\n"

  if "Metadata" in object[1]: #and (status == None or object[1]['Metadata'] != status[1]['Metadata']):
    if "xesam:url" in object[1]['Metadata']:
      url = split_url(object[1]['Metadata']['xesam:url'])
      song_info += "MOPIDY_PROVIDER=\"" + url["provider"] + "\"\n"
      song_info += "MOPIDY_URL=\"" + url["url"] + "\"\n"
    if "xesam:trackNumber" in object[1]['Metadata']:
      song_info += "MOPIDY_TRACK=" + str(object[1]['Metadata']['xesam:trackNumber']) + "\n"
    if "xesam:title" in object[1]['Metadata']:
      song_info += "MOPIDY_TITLE=\"" + object[1]['Metadata']['xesam:title'].replace("\"", "\\\"") + "\"\n"
    if "xesam:album" in object[1]['Metadata']:
      song_info += "MOPIDY_ALBUM=\"" + object[1]['Metadata']['xesam:album'] + "\"\n"
    if "xesam:artist" in object[1]['Metadata'] and len(object[1]['Metadata']['xesam:artist']) >= 1:
      song_info += "MOPIDY_ARTIST=\"" + object[1]['Metadata']['xesam:artist'][0] + "\"\n"
    if "xesam:albumArtist" in object[1]['Metadata'] and len(object[1]['Metadata']['xesam:albumArtist']) >= 1:
      song_info += "MOPIDY_ALBUM_ARTIST=\"" + object[1]['Metadata']['xesam:albumArtist'][0] + "\"\n"
    if "mpris:artUrl" in object[1]['Metadata']:
      song_info += "MOPIDY_ART=\"" + object[1]['Metadata']['mpris:artUrl'] + "\"\n"
  else:
    if DEBUG == 1: print("No metadata available")

  status = object
  if DEBUG == 1: print(song_info)

  with open(SONG_INFO_FILE, "w") as info_file:
    info_file.write(song_info)

  subprocess.run(update_bar, capture_output=True)

def main():
  CHECK_RUNNING = ['pgrep', '-cf', 'python.*' + os.path.basename(sys.argv[0])]
  if int(subprocess.run(CHECK_RUNNING, capture_output=True).stdout) > 1:
    exit(os.EX_UNAVAILABLE)

  bus = SessionBus()
  mopidy = wait_mopidy(bus)
  interface = mopidy[INTERFACE_PROPERTIES]
  loop = GLib.MainLoop()

  if DEBUG == 1: print("Mopidy service is active now\n");

  bus.subscribe(None, INTERFACE_PROPERTIES, SIGNAL, OBJECT_PATH, signal_fired=update_status)

  try:
    loop.run()
  except KeyboardInterrupt:
    return


if __name__ == "__main__":
  main()
