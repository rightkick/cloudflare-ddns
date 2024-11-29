#!/bin/bash
python3 -m pip install python-dotenv
cp cloudflare-ddns.py /usr/local/bin
cp cloudflare-ddns.service /etc/systemd/system/
cp cloudflare-ddns.timer /etc/systemd/system/
systemctl daemon-reload
systemctl restart cloudflare-ddns.service
