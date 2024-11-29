# Cloudflare-ddns
A simple python script `cloudflare-ddns.py` that can be used with systemd to periodically update your Cloudflare DNS records.

## Requirements
- `python3 -m pip install python-dotenv`
- `./env` file with your API and DNS zone details located at the working directory of the python script which is assumed to be `/usr/local/bin`. See example `.env.example` file. 

## Installation
```
sudo ./install-ddns.sh
```

## Details
- The script will run every 30 mins, as configured from the systemd timer. You can change it as needed. 
- The script will log at syslog. 
- The script works with IPv4 but it can be easily adjusted to use IPv6. 