# IP-details 🌍🔎

**IP-details** is a small Python script that fetches metadata about **your public IP address** (e.g., location, IP type, and related fields) using the **ipstack** IP geolocation API.

---

## What it does

- Queries ipstack’s API to retrieve information about an IP address
- Designed primarily to retrieve **your own public IP details** (the IP making the request)
- Prints (or otherwise displays) the returned response data (typically JSON)

> The exact fields you receive depend on your ipstack plan and the parameters used (free vs paid features).

---

## Repo layout

- `IP details.py` — main script
- `README.md`
- `LICENSE` (GPL-3.0)

---

## Requirements

- Python 3.x
- Internet connection
- An **ipstack API access key**

Optional (common) dependency:
- `requests` (if the script uses Python Requests instead of the standard library)

If you see `ModuleNotFoundError`, install the missing package with `pip install <package>`.

---

## Get an ipstack API key

1. Create an account on ipstack.
2. Copy your **API Access Key** from the dashboard.

ipstack docs:  
- https://ipstack.com/documentation/

---

## Run

### 1) Clone
```bash
git clone https://github.com/kai9987kai/IP-details.git
cd IP-details
