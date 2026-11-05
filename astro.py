"""低精度の天文計算（Meeus『Astronomical Algorithms』の主要項）。
太陽黄経は約0.01度、月黄経は約0.3度の精度。星座（30度区切り）の判定と月齢には十分。"""
import math
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
UTC = timezone.utc

def jd(dt):
    dt = dt.astimezone(UTC)
    return 2440587.5 + dt.timestamp() / 86400.0

def _s(x):
    return math.sin(math.radians(x))

def sun_lon(dt):
    T = (jd(dt) - 2451545.0) / 36525
    L0 = 280.46646 + 36000.76983 * T
    M = 357.52911 + 35999.05029 * T
    C = (1.914602 - 0.004817 * T) * _s(M) + (0.019993 - 0.000101 * T) * _s(2 * M) + 0.000289 * _s(3 * M)
    om = 125.04 - 1934.136 * T
    return (L0 + C - 0.00569 - 0.00478 * _s(om)) % 360

def moon_lon(dt):
    T = (jd(dt) - 2451545.0) / 36525
    Lp = 218.3164477 + 481267.88123421 * T
    D = 297.8501921 + 445267.1114034 * T
    M = 357.5291092 + 35999.0502909 * T
    Mp = 134.9633964 + 477198.8675055 * T
    F = 93.2720950 + 483202.0175233 * T
    lon = (Lp + 6.288774 * _s(Mp) + 1.274027 * _s(2 * D - Mp) + 0.658314 * _s(2 * D)
           + 0.213618 * _s(2 * Mp) - 0.185116 * _s(M) - 0.114332 * _s(2 * F)
           + 0.058793 * _s(2 * D - 2 * Mp) + 0.057066 * _s(2 * D - M - Mp)
           + 0.053322 * _s(2 * D + Mp) + 0.045758 * _s(2 * D - M)
           - 0.040923 * _s(M - Mp) - 0.034720 * _s(D) - 0.030383 * _s(M + Mp))
    return lon % 360

def elongation(dt):
    """月と太陽の黄経差（0=新月、180=満月）"""
    return (moon_lon(dt) - sun_lon(dt)) % 360

def last_new_moon(dt):
    """dt直前の新月の時刻（10分単位）"""
    t = dt - timedelta(days=elongation(dt) / 12.19)
    for _ in range(5):  # 補正
        e = elongation(t)
        if e > 180:
            e -= 360
        t -= timedelta(days=e / 12.19)
    return t

def moon_age(dt):
    return (dt - last_new_moon(dt)).total_seconds() / 86400

def sign_changes(start, end, func, step_min=10):
    """[start,end) の間に func の星座（30度区切り）が変わる時刻の一覧"""
    out = []
    t = start
    prev = int(func(t) // 30)
    while t < end:
        t2 = t + timedelta(minutes=step_min)
        cur = int(func(t2) // 30)
        if cur != prev:
            # 二分法で1分単位に
            a, b = t, t2
            while (b - a) > timedelta(minutes=1):
                m = a + (b - a) / 2
                if int(func(m) // 30) == prev:
                    a = m
                else:
                    b = m
            out.append((b, prev, cur))
            prev = cur
        t = t2
    return out
