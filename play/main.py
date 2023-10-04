import os
from urllib.parse import urlparse
import requests
import re
import asyncio
import aiohttp
import argparse
import subprocess
import platform
from pathlib import Path

accepted_content_types = [
    "video",
    "audio",
    "ogg",
    "octet-stream",
]
vlc_path_file = Path.home() / ".vlc_path"


async def is_video_url(url, session):
    for _ in range(3):
        try:
            async with session.head(url) as response:
                content_type = response.headers.get("content-type", "")
                return any([x in content_type for x in accepted_content_types])
        except Exception as e:
            print("Error: ", e)
    return False


async def is_video_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [is_video_url(url, session) for url in urls]
        return await asyncio.gather(*tasks)


def is_video_url_sync(url):
    for _ in range(3):
        try:
            res = requests.head(url)
            content_type = res.headers.get("content-type", "")
            return any([x in content_type for x in accepted_content_types])
        except Exception as e:
            print("Error: ", e)
    return False


def get_urls(text):
    return re.findall(r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+", text)


def get_vlc_cmd():
    if vlc_path_file.exists():
        with open(vlc_path_file, "r") as f:
            return f.read()

    vlc_path = None
    try:
        cmd = "which vlc"
        if platform.system() == "Windows":
            cmd = "where vlc"
        subprocess.check_output(cmd.split(), stderr=subprocess.DEVNULL)
        vlc_path = "vlc"
    except Exception:
        pass

    if not vlc_path:
        if platform.system() == "Windows":
            posible_paths = [
                "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
                "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe",
            ]
            for path in posible_paths:
                if Path(path).exists():
                    vlc_path = path
        else:
            posible_paths = [
                "/usr/bin/vlc",
                "/usr/local/bin/vlc",
            ]
            for path in posible_paths:
                if Path(path).exists():
                    vlc_path = path
    if not vlc_path:
        print("VLC not found")
        return None
    else:
        with open(vlc_path_file, "w") as f:
            f.write(vlc_path)
        return vlc_path


def get_video_urls(vurl: str):
    if vurl.endswith("/"):
        vurl = vurl[:-1]

    if is_video_url_sync(vurl):
        return [vurl]

    res = None
    for _ in range(3):
        try:
            res = requests.get(vurl)
            break
        except Exception as e:
            print("Error: ", e)
    if not res:
        print(f"Could not get {vurl}")
        return []

    urls = get_urls(res.text)
    urlp = urlparse(vurl)

    nurls = []
    for url in urls:
        if url.startswith("/"):
            nurls.append(urlp.scheme + "://" + urlp.netloc + url)
        elif url.startswith("http"):
            nurls.append(url)
        else:
            nurls.append(vurl + "/" + url)

    result = asyncio.run(is_video_urls(nurls))
    return [url for url, is_video in zip(nurls, result) if is_video]


def play_videos(urls, vlc_cmd):
    try:
        pr = subprocess.Popen(
            [vlc_cmd, "--playlist-enqueue", "--play-and-exit"] + urls,
            stderr=subprocess.DEVNULL,
        )
        pr.wait(3)
    except FileNotFoundError:
        if os.path.exists(vlc_path_file):
            os.remove(vlc_path_file)
        vlc_cmd = get_vlc_cmd()
        if vlc_cmd:
            play_videos(urls, vlc_cmd)
        else:
            print("No VLC found")
    except subprocess.TimeoutExpired:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to get video URLs from")
    parser.add_argument("range", nargs="?", help="Range of URLs to get")
    args = parser.parse_args()

    urls = get_video_urls(args.url)
    s = 0
    e = len(urls) - 1
    if args.range:
        if "-" in args.range:
            s, e = args.range.split("-")
            s = int(s) - 1
            e = int(e) - 1
        else:
            s = int(args.range) - 1
    if s < 0:
        s = 0
    if e >= len(urls):
        e = len(urls) - 1

    video_urls = urls[s : e + 1]
    vlc_cmd = get_vlc_cmd()
    if vlc_cmd:
        print("Playing", len(video_urls), "videos")
        play_videos(video_urls, vlc_cmd)
    else:
        print("No VLC found")


if __name__ == "__main__":
    main()
