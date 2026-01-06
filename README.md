# device-discover

![](https://img.shields.io/badge/Claude%20Assisted-90%25-00a67d?logo=claude)

A higly vibe-coded app to discover SSDP and mDNS devices on your network

## Explanation

A Python/Flask web app that discovers devices on your local network using Simple Service Discovery Protocol (SSDP) and Multicast DNS (mDNS).

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

### Docker
```
docker-compose up -d
```

Then open: **http://localhost:3001**

## Troubleshooting

**No devices found?**
- Make sure devices are on the same network
- Check firewall isn't blocking UDP port 1900
- If using Docker, ensure `network_mode: host` is set

**Port already in use?**
Change the port in `app.py` and `docker-compose.yml`



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
