import requests
from dotenv import load_dotenv
import os
import logging
import logging.handlers

# This script can update a DNS record at CloudFlare.
# Author: AlexK
# Revision date: 27 Nov 2024

# Requirements: 
# python3 -m pip install python-dotenv

# Define the program name
PROGRAM_NAME = "cloudflare-ddns"

# Configure logging
syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
formatter = logging.Formatter(f"{PROGRAM_NAME}: %(levelname)s - %(message)s")
syslog_handler.setFormatter(formatter)
logger = logging.getLogger(PROGRAM_NAME)
logger.setLevel(logging.INFO)
logger.addHandler(syslog_handler)

# Load environment variables from .env file
load_dotenv()

# Get API details from environment variables
API_TOKEN = os.getenv("API_TOKEN")
ZONE_ID = os.getenv("ZONE_ID")
DNS_RECORD_NAME = os.getenv("DNS_RECORD_NAME")

# API headers
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def get_public_ipv4():
    """Fetch the public IPv4 address using ipinfo.io."""
    try:
        response = requests.get("https://ipinfo.io/ip")
        response.raise_for_status()
        public_ip = response.text.strip()
        logger.info(f"Current Public IP fetched successfully: {public_ip}")
        return public_ip
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        logger.error(f"Error fetching public IP: {e}")
        return None

def get_a_record_ip(zone_id, record_name):
    """Fetch the current public IP of record_name."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    params = {"name": record_name, "type": "A"}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if data["success"] and data["result"]:
            # Assume the first result is the correct one for the given name
            record = data["result"][0]
            record_ip = record["content"]
            logger.info(f"DNS record fetched successfully: {record_ip}")
            return record_ip  # The IP address of the A record
        else:
            print(f"No A record found for {record_name}.")
            logger.warning(f"No A record found for {record_name}.")
    except requests.RequestException as e:
        print(f"Error fetching DNS records: {e}")
        logger.error(f"Error fetching DNS records: {e}")

    return None
  
def get_dns_record_id(zone_id, record_name):
    """Fetch the ID of a specific DNS record."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    params = {"name": record_name}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    data = response.json()

    if data["success"]:
        records = data["result"]
        if records:
            return records[0]["id"]
        else:
            print(f"No DNS record found for {record_name}.")
            logger.warning(f"No DNS record found for {record_name}.")
    else:
        print("Failed to fetch DNS records:", data["errors"])
        logger.error(f"Failed to fetch DNS records:", data["errors"])
    return None

def update_dns_record(zone_id, record_id, record_name, new_ip):
    """Update a DNS record with a new IP address."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    payload = {
        "type": "A",  # Change this if you're updating a different type of record
        "name": record_name,
        "content": new_ip,
        "ttl": 1,  # Auto TTL
        "proxied": False,  # Set True if you want Cloudflare proxy
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()

    if data["success"]:
        print(f"DNS record {record_name} updated successfully.")
        logger.info(f"DNS record {record_name} updated successfully.")
    else:
        print("Failed to update DNS record:", data["errors"])
        logger.error("Failed to update DNS record:", data["errors"])
        

def main():
    dns_record_ip = get_a_record_ip(ZONE_ID, DNS_RECORD_NAME)
    public_ip = get_public_ipv4()
    if public_ip.strip() == dns_record_ip.strip():
        logger.info(f"DNS record up to date")
    else:
        logger.info(f"Updating DNS record for {DNS_RECORD_NAME} to {public_ip}")
        record_id = get_dns_record_id(ZONE_ID, DNS_RECORD_NAME)
        if record_id:
            update_dns_record(ZONE_ID, record_id, DNS_RECORD_NAME, get_public_ipv4())

if __name__ == "__main__":
    main()

