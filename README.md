# Proxy Location Checker

A simple web UI to check proxy location distance from a target address.

## Features

- 📍 Compare proxy exit location vs any target address
- 📏 Calculate distance in miles and km
- 🔍 Detect if IP is flagged as Proxy/VPN or Hosting/Datacenter
- 🎨 Clean, modern dark UI

## Installation

1. Install Python 3.7+
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Start the app:

```bash
python app.py
```

2. Open your browser to: **http://localhost:5000**

3. Enter your proxy string and target address, then click "Check Proxy Location"

## Example Input

**Proxy String:**
```
username:password@server:port
```

**Target Address:**
```
1208 Wren St, San Diego, CA 92114
```

## What It Shows

- **Distance**: How far the proxy exit IP is from your target address
- **Detection Status**: Whether the IP is detected as a proxy/VPN or datacenter
- **Proxy Location**: Actual city, region, country, ISP, and coordinates
- **Assessment**: Rating from Excellent (< 10 miles) to Bad (> 250 miles)
