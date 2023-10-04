# Play

Extract video from website and play it in VLC Media Player.

## Requirements

- Python 3.6+
- VLC Media Player

## Installation

```bash
pip install git+https://github.com/shhossain/play.git
```

## Usage

```bash
usage: play [-h] url [range]

positional arguments:
  url         URL to get video URLs from
  range       Range of URLs to get (e.g. 1-5 or 1)
```

## Example
Play videos 1 to 5
```bash
play https://some-website.com/videos 1-5
```

Play video 1 to last
```bash
play https://some-website.com/videos 1
```

Play all videos
```bash
play https://some-website.com/videos
```
