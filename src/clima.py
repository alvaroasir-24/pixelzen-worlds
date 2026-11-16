#!/usr/bin/env python3
"""PixelZen - clima real via Open-Meteo con cache en ~/.config/pixelzen/clima_real.json."""
import datetime
import json
import os
import subprocess
import sys
import urllib.request

CACHE_PATH = os.path.expanduser('~/.config/pixelzen/clima_real.json')
CACHE_MAX_AGE_S = 600

WMO_MAP = {
    0: ('Despejado', 'normal'),
    1: ('Mayormente despejado', 'normal'),
    2: ('Parcialmente nublado', 'normal'),
    3: ('Nublado', 'normal'),
    45: ('Niebla', 'niebla'),
    48: ('Niebla densa', 'niebla'),
    51: ('Llovizna', 'lluvia'),
    53: ('Llovizna', 'lluvia'),
    55: ('Llovizna', 'lluvia'),
    56: ('Llovizna helada', 'lluvia'),
    57: ('Llovizna helada', 'lluvia'),
    61: ('Lluvia', 'lluvia'),
    63: ('Lluvia', 'lluvia'),
    65: ('Lluvia fuerte', 'lluvia'),
    66: ('Lluvia helada', 'lluvia'),
    67: ('Lluvia helada', 'lluvia'),
    71: ('Nieve', 'nieve'),
    73: ('Nieve', 'nieve'),
    75: ('Nieve', 'nieve'),
    77: ('Nieve', 'nieve'),
    80: ('Chubascos', 'lluvia'),
    81: ('Chubascos', 'lluvia'),
    82: ('Chubascos', 'lluvia'),
    85: ('Nieve', 'nieve'),
    86: ('Nieve', 'nieve'),
    95: ('Tormenta', 'tormenta'),
    96: ('Tormenta', 'tormenta'),
    99: ('Tormenta', 'tormenta'),
}


def _leer_json(url, timeout=3):
    req = urllib.request.Request(url, headers={'User-Agent': 'PixelZenWorlds'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _leer_cache():
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('ok') and data.get('updatedUtc'):
            dt = datetime.datetime.fromisoformat(data['updatedUtc'].replace('Z', '+00:00'))
            age = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds()
            return data, age < CACHE_MAX_AGE_S
    except Exception:
        pass
    return None, False


def _ubicacion_local():
    here = os.path.dirname(os.path.abspath(__file__))
    ubi_py = os.path.join(here, 'ubicacion.py')
    lat, lon, city = 40.4, -3.7, ''
    if os.path.isfile(ubi_py):
        try:
            out = subprocess.run([sys.executable, '-I', ubi_py], capture_output=True, text=True, timeout=3).stdout
            u = json.loads(out)
            lat = float(u.get('lat', lat))
            lon = float(u.get('lon', lon))
            tz = str(u.get('tz') or '')
            if '/' in tz:
                city = tz.split('/')[-1].replace('_', ' ')
            origen = str(u.get('origen') or '')
            if origen.startswith('casa: ') and origen[6:].strip():
                city = origen[6:].strip()
        except Exception:
            pass
    return lat, lon, city


def obtener_clima(forzar=False):
    cached, fresh = _leer_cache()
    if cached and fresh and not forzar:
        return cached

    lat, lon, city = _ubicacion_local()
    country = ''
    try:
        g1 = _leer_json('http://ip-api.com/json/?fields=status,country,city,lat,lon', timeout=2)
        if g1.get('status') == 'success' and g1.get('lat') is not None:
            lat = float(g1['lat'])
            lon = float(g1['lon'])
            city = str(g1.get('city') or city)
            country = str(g1.get('country') or '')
    except Exception:
        try:
            g2 = _leer_json('https://ipwho.is/', timeout=2)
            if g2.get('success') and g2.get('latitude') is not None:
                lat = float(g2['latitude'])
                lon = float(g2['longitude'])
                city = str(g2.get('city') or city)
                country = str(g2.get('country') or '')
        except Exception:
            pass

    try:
        url = (
            f'https://api.open-meteo.com/v1/forecast?latitude={lat:.4f}&longitude={lon:.4f}'
            '&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day&timezone=auto'
        )
        om = _leer_json(url, timeout=3)
        cur = om.get('current') or {}
        if 'temperature_2m' in cur:
            code = int(cur.get('weather_code', 0))
            desc, efecto = WMO_MAP.get(code, ('Despejado', 'normal'))
            res = {
                'ok': True,
                'city': city or 'Tu ubicación',
                'country': country,
                'lat': lat,
                'lon': lon,
                'temp': round(float(cur['temperature_2m']), 1),
                'apparent': round(float(cur.get('apparent_temperature', cur['temperature_2m'])), 1),
                'hum': int(round(float(cur.get('relative_humidity_2m', 0)))),
                'wind': round(float(cur.get('wind_speed_10m', 0)), 0),
                'code': code,
                'desc': desc,
                'efecto': efecto,
                'isDay': int(cur.get('is_day', 1)),
                'updatedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False)
            return res
    except Exception:
        pass

    if cached:
        return cached
    return {'ok': False, 'city': city or 'Madrid', 'lat': lat, 'lon': lon, 'efecto': 'normal'}


if __name__ == '__main__':
    force = '--force' in sys.argv
    print(json.dumps(obtener_clima(forzar=force), ensure_ascii=False))
