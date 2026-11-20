#!/usr/bin/env python3
"""Refresh now_building.episodes in content/site.json from the YouTube playlist.

    ~/.claude/youtube-venv/bin/python scripts/update_home_videos.py

Uses the Morebyt channel token (~/.claude/.tmp/youtube_tokens/coding.json). Titles are
taken from YouTube with the " | <series> #N" suffix removed. Review the diff, then rebuild:
the site build itself never calls YouTube.
"""
import json
import os
import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "content" / "site.json"


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    playlist = data["now_building"]["playlist_id"]
    creds = Credentials.from_authorized_user_file(os.path.expanduser("~/.claude/.tmp/youtube_tokens/coding.json"))
    if not creds.valid:
        creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)
    items, token = [], None
    while True:
        r = yt.playlistItems().list(part="snippet,status", playlistId=playlist, maxResults=50, pageToken=token).execute()
        items += r["items"]
        token = r.get("nextPageToken")
        if not token:
            break
    episodes = []
    for it in sorted(items, key=lambda i: i["snippet"]["position"]):
        if it["status"].get("privacyStatus") != "public":
            continue
        title = re.sub(r"\s*\|.*$", "", it["snippet"]["title"]).strip()
        title = title[0].upper() + title[1:].lower() if title.isupper() else title
        episodes.append({"id": it["snippet"]["resourceId"]["videoId"], "title": title})
    data["now_building"]["episodes"] = episodes
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(episodes)} public episodes written to {DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
