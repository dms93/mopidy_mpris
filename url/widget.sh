#!/usr/bin/env bash

## - - - Environment information - - - - - - - - - - - - - - - - - - - - - - - -

DS_HOME="$(dirname $0)/../../.."
SONG_DATA="/tmp/.song"

## - - - Importing some library scripts  - - - - - - - - - - - - - - - - - - - -

source $DS_HOME/base/rofi.sh
[ -f $SONG_DATA ] && source "$SONG_DATA"

## - - - Variables and Constants - - - - - - - - - - - - - - - - - - - - - - - -

ROFI_THEME="topbar/mopidy_url"

WIDGET_TYPE="menu"
WIDGET_NAME="URL from Mopidy"
WIDGET_MAIN_ARGS="copy ."

PROMPT_ICON=""
PROMPT_TITLE="$WIDGET_NAME"

## - - - Functions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

copy()
{
  local url
  local prefix

  case $MOPIDY_PROVIDER in
    "youtube")
      url="https://www.youtube.com/watch?v=$MOPIDY_URL\n"
      PROMPT_SUBTITLE="YouTube"
      prefix="Video"
      ;;

    "spotify")
      url="https://open.spotify.com/track/$MOPIDY_URL\n"
      PROMPT_SUBTITLE="Spotify"
      prefix="Track"
      ;;

    *)
      PROMPT_SUBTITLE="Not Found"
      WIDGET_CONTENT="\n"
      ;;
  esac

  [ -n "$url" ] && \
  WIDGET_CONTENT="$prefix: $($DS_HOME/music/labels/song.sh get_data .)\nURL: $url"

  printf "$url" | xclip -selection clipboard
  rofi_exec
}

## - - - Start Point - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

  ## Uncomment this if the scripts needs parameters to be executed
    source "$DS_HOME/base/parameters.sh"

## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
