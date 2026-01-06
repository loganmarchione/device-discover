# device-discover

[![CI](https://github.com/loganmarchione/device-discover/actions/workflows/main.yml/badge.svg)](https://github.com/loganmarchione/device-discover/actions/workflows/main.yml) ![](https://img.shields.io/badge/Claude%20Assisted-🚀-00a67d?logo=claude)

A highly vibe-coded app to discover SSDP and mDNS devices on your network

## Explanation

- I've been working on setting up VLANs for my IoT devices and needed a "dashboard" to see which devices were broadcasting on my subnet
- This is a Python/Flask web app that discovers devices on your local network using Simple Service Discovery Protocol (SSDP) and Multicast DNS (mDNS)

## Requirements

```
git clone https://github.com/loganmarchione/device-discover.git
cd device-discover
```

### Local Python
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:3001 --reload src.app:app
```

or

### Docker
```
docker-compose up -d
docker logs device-discover --follow
```

Then open: http://localhost:3001

![Screenshot](https://raw.githubusercontent.com/loganmarchione/device-discover/refs/heads/main/screenshots/screenshot.png)

## Troubleshooting

No devices found?
- Make sure devices are on the same network
- Check firewall isn't blocking UDP port 1900
- If using Docker, ensure `network_mode: host` is set

## Development

```
# virtual environment
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements-dev.txt

# update code

# run checks
make check
```
