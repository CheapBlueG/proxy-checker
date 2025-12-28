from flask import Flask, render_template_string, request, jsonify
import re
import math
import requests
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Location Checker</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v3.0.1/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v3.0.1/mapbox-gl.css" rel="stylesheet" />
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 40px 20px;
            color: #fff;
        }
        
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ccc;
            font-size: 14px;
        }
        
        .label-hint {
            font-weight: normal;
            color: #666;
            font-size: 12px;
        }
        
        input[type="text"], textarea {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-size: 14px;
            transition: all 0.3s ease;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        
        textarea {
            min-height: 80px;
            resize: vertical;
        }
        
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #00d9ff;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
        }
        
        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            color: #1a1a2e;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 217, 255, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .result-section {
            margin-bottom: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
        }
        
        .result-section h3 {
            font-size: 14px;
            color: #00d9ff;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .result-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 14px;
        }
        
        .result-row:last-child {
            border-bottom: none;
        }
        
        .result-label {
            color: #888;
        }
        
        .result-value {
            color: #fff;
            font-family: 'Monaco', 'Menlo', monospace;
            text-align: right;
            max-width: 60%;
            word-break: break-word;
        }
        
        .distance-box {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(0, 255, 136, 0.1));
            border-radius: 12px;
            border: 1px solid rgba(0, 217, 255, 0.3);
        }
        
        .distance-value {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .distance-unit {
            font-size: 18px;
            color: #888;
        }
        
        .distance-km {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        
        .assessment {
            margin-top: 15px;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 500;
            text-align: center;
        }
        
        .assessment.gold { background: rgba(255, 215, 0, 0.3); color: #ffd700; border: 1px solid #ffd700; }
        .assessment.verygood { background: rgba(0, 255, 136, 0.25); color: #00ff88; }
        .assessment.decent { background: rgba(144, 238, 144, 0.25); color: #90ee90; }
        .assessment.notbest { background: rgba(60, 179, 113, 0.25); color: #3cb371; }
        .assessment.donotuse { background: rgba(255, 0, 0, 0.25); color: #ff4444; border: 1px solid #ff4444; }
        
        .detection-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .badge-yes { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        .badge-no { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        
        .error {
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid rgba(255, 71, 87, 0.3);
            color: #ff4757;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .api-link {
            color: #00d9ff;
            text-decoration: none;
        }
        
        .api-link:hover {
            text-decoration: underline;
        }
        
        .save-key {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            font-size: 12px;
            color: #888;
        }
        
        .save-key input[type="checkbox"] {
            width: auto;
        }
        
        #map {
            width: 100%;
            height: 350px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .marker-target {
            width: 30px;
            height: 30px;
            background: #00ff88;
            border: 3px solid #fff;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .marker-proxy {
            width: 30px;
            height: 30px;
            background: #00d9ff;
            border: 3px solid #fff;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .mapboxgl-popup-content {
            background: #1a1a2e;
            color: #fff;
            padding: 12px 16px;
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        
        .mapboxgl-popup-tip {
            border-top-color: #1a1a2e;
        }
        
        .mapboxgl-popup-close-button {
            color: #888;
            font-size: 18px;
        }
        
        .popup-title {
            font-weight: 600;
            margin-bottom: 4px;
            color: #00d9ff;
        }
        
        .map-legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .legend-dot {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid #fff;
        }
        
        .legend-dot.target { background: #00ff88; }
        .legend-dot.proxy { background: #00d9ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Proxy Location Checker</h1>
        <p class="subtitle">Check proxy distance from target address & detection status</p>
        
        <div class="card">
            <div class="form-group">
                <label>
                    Mapbox API Key 
                    <span class="label-hint">— <a href="https://account.mapbox.com/access-tokens/" target="_blank" class="api-link">Get free key</a></span>
                </label>
                <input type="text" id="mapboxKey" placeholder="pk.eyJ1Ijo...">
                <div class="save-key">
                    <input type="checkbox" id="saveKey" checked>
                    <label for="saveKey" style="margin: 0; font-weight: normal;">Remember API key in browser</label>
                </div>
            </div>
            
            <div class="form-group">
                <label>
                    IP2Location API Key 
                    <span class="label-hint">— <a href="https://www.ip2location.io/sign-up" target="_blank" class="api-link">Get free key</a></span>
                </label>
                <input type="text" id="ip2locationKey" placeholder="Your IP2Location.io API key">
                <div class="save-key">
                    <input type="checkbox" id="saveIp2Key" checked>
                    <label for="saveIp2Key" style="margin: 0; font-weight: normal;">Remember API key in browser</label>
                </div>
            </div>
            
            <div class="form-group">
                <label>Proxy String</label>
                <textarea id="proxyString" placeholder="package-327430-country-us-region-california-city-san+diego-sessionid-xxx-sessionlength-600:password@proxy.soax.com:5000"></textarea>
            </div>
            
            <div class="form-group">
                <label>Target Address</label>
                <input type="text" id="targetAddress" placeholder="1208 Wren St, San Diego, CA 92114">
            </div>
            
            <button class="btn" id="checkBtn" onclick="checkProxy()">
                Check Proxy Location
            </button>
        </div>
        
        <div class="results" id="results">
        </div>
    </div>
    
    <script>
        window.onload = function() {
            const savedKey = localStorage.getItem('mapbox_api_key');
            if (savedKey) {
                document.getElementById('mapboxKey').value = savedKey;
            }
            const savedIp2Key = localStorage.getItem('ip2location_api_key');
            if (savedIp2Key) {
                document.getElementById('ip2locationKey').value = savedIp2Key;
            }
        };
        
        async function checkProxy() {
            const mapboxKey = document.getElementById('mapboxKey').value.trim();
            const ip2locationKey = document.getElementById('ip2locationKey').value.trim();
            const proxyString = document.getElementById('proxyString').value.trim();
            const targetAddress = document.getElementById('targetAddress').value.trim();
            const saveKey = document.getElementById('saveKey').checked;
            const saveIp2Key = document.getElementById('saveIp2Key').checked;
            const resultsDiv = document.getElementById('results');
            const btn = document.getElementById('checkBtn');
            
            if (!mapboxKey) {
                alert('Please enter your Mapbox API key');
                return;
            }
            
            if (!ip2locationKey) {
                alert('Please enter your IP2Location API key');
                return;
            }
            
            if (!proxyString || !targetAddress) {
                alert('Please fill in both proxy string and target address');
                return;
            }
            
            if (saveKey) {
                localStorage.setItem('mapbox_api_key', mapboxKey);
            } else {
                localStorage.removeItem('mapbox_api_key');
            }
            
            if (saveIp2Key) {
                localStorage.setItem('ip2location_api_key', ip2locationKey);
            } else {
                localStorage.removeItem('ip2location_api_key');
            }
            
            btn.disabled = true;
            btn.textContent = 'Checking...';
            resultsDiv.className = 'results show';
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Connecting through proxy & checking location...</p>
                    </div>
                </div>
            `;
            
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        proxy_string: proxyString, 
                        target_address: targetAddress,
                        mapbox_key: mapboxKey,
                        ip2location_key: ip2locationKey
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `
                        <div class="card">
                            <div class="error">❌ ${data.error}</div>
                        </div>
                    `;
                } else {
                    displayResults(data, mapboxKey);
                }
            } catch (err) {
                resultsDiv.innerHTML = `
                    <div class="card">
                        <div class="error">❌ Connection error: ${err.message}</div>
                    </div>
                `;
            }
            
            btn.disabled = false;
            btn.textContent = 'Check Proxy Location';
        }
        
        function displayResults(data, mapboxKey) {
            const resultsDiv = document.getElementById('results');
            
            let assessmentClass = 'donotuse';
            let assessmentText = '🚨❌ DO NOT USE - Too far from target ❌🚨';
            
            if (data.distance_miles <= 2) {
                assessmentClass = 'gold';
                assessmentText = '🏆 EXCELLENT - Gold proxy to use (within 2 miles)';
            } else if (data.distance_miles < 5) {
                assessmentClass = 'verygood';
                assessmentText = '✅ VERY GOOD - Great proxy to use (within 5 miles)';
            } else if (data.distance_miles <= 10) {
                assessmentClass = 'decent';
                assessmentText = '👍 DECENT - Usable proxy (within 10 miles)';
            } else if (data.distance_miles <= 15) {
                assessmentClass = 'notbest';
                assessmentText = '⚠️ NOT THE BEST - Recommend trying another proxy';
            }
            
            resultsDiv.innerHTML = `
                <div class="card">
                    <div class="distance-box">
                        <div class="distance-value">${data.distance_miles.toFixed(1)}</div>
                        <div class="distance-unit">miles</div>
                        <div class="distance-km">${data.distance_km.toFixed(1)} km</div>
                        <div class="assessment ${assessmentClass}">${assessmentText}</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="map-legend">
                        <div class="legend-item">
                            <div class="legend-dot target"></div>
                            <span>Target Address</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-dot proxy"></div>
                            <span>Proxy Location</span>
                        </div>
                    </div>
                    <div id="map"></div>
                </div>
                
                <div class="card">
                    <div class="result-section">
                        <h3>🔍 Detection Status (via IP2Location.io)</h3>
                        <div class="result-row">
                            <span class="result-label">Proxy Detected</span>
                            <span class="detection-badge ${data.is_proxy ? 'badge-yes' : 'badge-no'}">
                                ${data.is_proxy ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">VPN</span>
                            <span class="detection-badge ${data.is_vpn ? 'badge-yes' : 'badge-no'}">
                                ${data.is_vpn ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Datacenter/Hosting</span>
                            <span class="detection-badge ${data.is_datacenter ? 'badge-yes' : 'badge-no'}">
                                ${data.is_datacenter ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">TOR</span>
                            <span class="detection-badge ${data.is_tor ? 'badge-yes' : 'badge-no'}">
                                ${data.is_tor ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Public Proxy</span>
                            <span class="detection-badge ${data.is_public_proxy ? 'badge-yes' : 'badge-no'}">
                                ${data.is_public_proxy ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Residential Proxy</span>
                            <span class="detection-badge ${data.is_residential ? 'badge-yes' : 'badge-no'}">
                                ${data.is_residential ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Web Proxy</span>
                            <span class="detection-badge ${data.is_web_proxy ? 'badge-yes' : 'badge-no'}">
                                ${data.is_web_proxy ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Web Crawler</span>
                            <span class="detection-badge ${data.is_web_crawler ? 'badge-yes' : 'badge-no'}">
                                ${data.is_web_crawler ? '🚨 YES' : '✅ NO'}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Proxy Type</span>
                            <span class="result-value">${data.proxy_type}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Usage Type</span>
                            <span class="result-value">${data.usage_type}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Threat</span>
                            <span class="result-value">${data.threat}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Provider</span>
                            <span class="result-value">${data.provider}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Last Seen (days)</span>
                            <span class="result-value">${data.last_seen}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Fraud Score</span>
                            <span class="result-value">${data.fraud_score}</span>
                        </div>
                    </div>
                    
                    <div class="result-section">
                        <h3>🐛 Debug Info</h3>
                        <div class="result-row">
                            <span class="result-label">Has Proxy Object</span>
                            <span class="result-value">${data.debug_has_proxy_obj}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Raw is_proxy</span>
                            <span class="result-value">${data.debug_is_proxy_raw}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Proxy Object</span>
                            <span class="result-value" style="font-size:10px;">${JSON.stringify(data.debug_proxy_obj)}</span>
                        </div>
                    </div>
                    
                    <div class="result-section">
                        <h3>📍 Target Address (via Mapbox)</h3>
                        <div class="result-row">
                            <span class="result-label">Input</span>
                            <span class="result-value">${data.target_input}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Resolved</span>
                            <span class="result-value">${data.target_resolved}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Coordinates</span>
                            <span class="result-value">${data.target_lat.toFixed(6)}, ${data.target_lon.toFixed(6)}</span>
                        </div>
                    </div>
                    
                    <div class="result-section">
                        <h3>🌐 Proxy Exit Location (via IP2Location.io)</h3>
                        <div class="result-row">
                            <span class="result-label">IP Address</span>
                            <span class="result-value">${data.ip}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Location</span>
                            <span class="result-value">${data.city}, ${data.region}, ${data.country}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Coordinates</span>
                            <span class="result-value">${data.actual_lat}, ${data.actual_lon}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">ISP</span>
                            <span class="result-value">${data.isp}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">Organization</span>
                            <span class="result-value">${data.org}</span>
                        </div>
                    </div>
                </div>
            `;
            
            // Initialize Mapbox map
            mapboxgl.accessToken = mapboxKey;
            
            const centerLat = (data.target_lat + data.actual_lat) / 2;
            const centerLon = (data.target_lon + data.actual_lon) / 2;
            
            const map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/dark-v11',
                center: [centerLon, centerLat],
                zoom: 4
            });
            
            map.addControl(new mapboxgl.NavigationControl());
            
            map.on('load', function() {
                map.addSource('route', {
                    'type': 'geojson',
                    'data': {
                        'type': 'Feature',
                        'properties': {},
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': [
                                [data.target_lon, data.target_lat],
                                [data.actual_lon, data.actual_lat]
                            ]
                        }
                    }
                });
                
                map.addLayer({
                    'id': 'route',
                    'type': 'line',
                    'source': 'route',
                    'layout': {
                        'line-join': 'round',
                        'line-cap': 'round'
                    },
                    'paint': {
                        'line-color': '#ff6b6b',
                        'line-width': 3,
                        'line-dasharray': [2, 2]
                    }
                });
                
                const bounds = new mapboxgl.LngLatBounds();
                bounds.extend([data.target_lon, data.target_lat]);
                bounds.extend([data.actual_lon, data.actual_lat]);
                map.fitBounds(bounds, { padding: 60 });
            });
            
            // Target marker (green)
            const targetEl = document.createElement('div');
            targetEl.className = 'marker-target';
            
            new mapboxgl.Marker(targetEl)
                .setLngLat([data.target_lon, data.target_lat])
                .setPopup(new mapboxgl.Popup({ offset: 25 })
                    .setHTML(`<div class="popup-title">📍 Target Address</div>${data.target_resolved}`))
                .addTo(map);
            
            // Proxy marker (blue)
            const proxyEl = document.createElement('div');
            proxyEl.className = 'marker-proxy';
            
            new mapboxgl.Marker(proxyEl)
                .setLngLat([data.actual_lon, data.actual_lat])
                .setPopup(new mapboxgl.Popup({ offset: 25 })
                    .setHTML(`<div class="popup-title">🌐 Proxy Exit</div>${data.city}, ${data.region}<br>IP: ${data.ip}`))
                .addTo(map);
        }
    </script>
</body>
</html>
'''


def parse_proxy_string(proxy_string):
    """Parse a SOAX-style proxy string."""
    result = {
        "claimed_country": None,
        "claimed_region": None,
        "claimed_city": None,
        "username": None,
        "password": None,
        "host": None,
        "port": None,
    }
    
    match = re.match(r'^(.+):(.+)@(.+):(\d+)$', proxy_string)
    if not match:
        raise ValueError("Invalid proxy string format. Expected: username:password@host:port")
    
    result["username"] = match.group(1)
    result["password"] = match.group(2)
    result["host"] = match.group(3)
    result["port"] = int(match.group(4))
    
    username = result["username"]
    
    country_match = re.search(r'country-([a-z]+)', username, re.IGNORECASE)
    if country_match:
        result["claimed_country"] = country_match.group(1).upper()
    
    region_match = re.search(r'region-([a-z\+]+)', username, re.IGNORECASE)
    if region_match:
        result["claimed_region"] = region_match.group(1).replace('+', ' ').title()
    
    city_match = re.search(r'city-([a-z\+]+)', username, re.IGNORECASE)
    if city_match:
        result["claimed_city"] = city_match.group(1).replace('+', ' ').title()
    
    return result


def geocode_with_mapbox(address, api_key):
    """Geocode an address using Mapbox Geocoding API."""
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json".format(
        requests.utils.quote(address)
    )
    params = {
        "access_token": api_key,
        "limit": 1
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if response.status_code == 401:
        raise ValueError("Invalid Mapbox API key")
    
    if "features" not in data or len(data["features"]) == 0:
        return None
    
    feature = data["features"][0]
    coords = feature["geometry"]["coordinates"]
    
    return {
        "lat": coords[1],
        "lon": coords[0],
        "place_name": feature["place_name"],
    }


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in miles."""
    R = 3959
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/check', methods=['POST'])
def check():
    data = request.json
    proxy_string = data.get('proxy_string', '')
    target_address = data.get('target_address', '')
    mapbox_key = data.get('mapbox_key', '')
    ip2location_key = data.get('ip2location_key', '')
    
    try:
        # Parse proxy string
        proxy_info = parse_proxy_string(proxy_string)
        
        # Geocode target address with Mapbox
        target_coords = geocode_with_mapbox(target_address, mapbox_key)
        if not target_coords:
            return jsonify({"error": "Could not geocode the target address. Please check the address and try again."})
        
        # Build proxy URL
        proxy_url = f"http://{proxy_info['username']}:{proxy_info['password']}@{proxy_info['host']}:{proxy_info['port']}"
        proxies = {"http": proxy_url, "https": proxy_url}
        
        # Step 1: Get the proxy's exit IP by making a request through the proxy
        try:
            ip_response = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=30)
            proxy_ip = ip_response.json().get('ip')
        except:
            try:
                ip_response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
                proxy_ip = ip_response.json().get('origin', '').split(',')[0].strip()
            except:
                return jsonify({"error": "Could not connect through proxy"})
        
        if not proxy_ip:
            return jsonify({"error": "Could not determine proxy exit IP"})
        
        # Step 2: Query IP2Location.io with the proxy IP (direct request, not through proxy)
        ip2_response = requests.get(
            f"https://api.ip2location.io/?key={ip2location_key}&ip={proxy_ip}",
            timeout=10
        )
        
        ip_data = ip2_response.json()
        
        if 'error' in ip_data:
            error_msg = ip_data['error'].get('error_message', 'Unknown error') if isinstance(ip_data['error'], dict) else ip_data['error']
            return jsonify({"error": f"IP2Location error: {error_msg}"})
        
        # Get the proxy object from response
        proxy_obj = ip_data.get('proxy') if ip_data.get('proxy') else {}
        
        # Read boolean values - handle both True/False and truthy values
        def get_bool(obj, key):
            val = obj.get(key)
            if val is True:
                return True
            if val is False:
                return False
            if val is None:
                return False
            if isinstance(val, str):
                return val.lower() in ['true', 'yes', '1']
            return bool(val)
        
        is_proxy = get_bool(ip_data, 'is_proxy')
        is_vpn = get_bool(proxy_obj, 'is_vpn')
        is_tor = get_bool(proxy_obj, 'is_tor')
        is_datacenter = get_bool(proxy_obj, 'is_data_center')
        is_public_proxy = get_bool(proxy_obj, 'is_public_proxy')
        is_residential = get_bool(proxy_obj, 'is_residential_proxy')
        is_web_proxy = get_bool(proxy_obj, 'is_web_proxy')
        is_web_crawler = get_bool(proxy_obj, 'is_web_crawler')
        
        proxy_type = proxy_obj.get('proxy_type') or '-'
        threat = proxy_obj.get('threat') or '-'
        provider = proxy_obj.get('provider') or '-'
        last_seen = proxy_obj.get('last_seen') if proxy_obj.get('last_seen') is not None else '-'
        fraud_score = ip_data.get('fraud_score') if ip_data.get('fraud_score') is not None else '-'
        usage_type = ip_data.get('usage_type') or '-'
        
        lat = ip_data.get('latitude', 0)
        lon = ip_data.get('longitude', 0)
        
        # Calculate distance
        distance = haversine_distance(
            target_coords['lat'], target_coords['lon'],
            lat, lon
        )
        
        return jsonify({
            "target_input": target_address,
            "target_resolved": target_coords['place_name'],
            "target_lat": target_coords['lat'],
            "target_lon": target_coords['lon'],
            "ip": proxy_ip,
            "country": ip_data.get('country_name', 'Unknown'),
            "region": ip_data.get('region_name', 'Unknown'),
            "city": ip_data.get('city_name', 'Unknown'),
            "actual_lat": lat,
            "actual_lon": lon,
            "isp": ip_data.get('isp', 'Unknown'),
            "org": ip_data.get('as', 'Unknown'),
            "is_proxy": is_proxy,
            "is_vpn": is_vpn,
            "is_tor": is_tor,
            "is_datacenter": is_datacenter,
            "is_public_proxy": is_public_proxy,
            "is_residential": is_residential,
            "is_web_proxy": is_web_proxy,
            "is_web_crawler": is_web_crawler,
            "proxy_type": proxy_type,
            "usage_type": usage_type,
            "threat": threat,
            "provider": provider,
            "last_seen": last_seen,
            "fraud_score": fraud_score,
            "distance_miles": distance,
            "distance_km": distance * 1.60934,
            "debug_has_proxy_obj": 'proxy' in ip_data,
            "debug_is_proxy_raw": ip_data.get('is_proxy'),
            "debug_proxy_obj": proxy_obj
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)})
    except requests.exceptions.Timeout:
        return jsonify({"error": "Connection timeout - proxy may be unreachable"})
    except requests.exceptions.ProxyError as e:
        return jsonify({"error": f"Proxy connection failed - check your proxy credentials"})
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
