# made by https://rip.linkvertise.lol -> https://trw.lat/ds
# warning : this code works fine for some links / min but for mass solving its blocked by platoboost system with a really good message "get a job"
# you can make it better, idk how plato is detecting it tbh (or if its detected or my proxies are detected)
# maybe when i tried the issues was my proxies getting detected, maybe works for mass solvig, maybe not

# Thanks to the bbg Verity for the help (https://discord.com/user/1517355254117568595) <@1517355254117568595>
# sorry for my bad english and lack of comments, bing.ai is retarded and i don't want to waste my time explaining this code, if you want to understand it, read it and understand it yourself

from curl_cffi import requests as cffi_requests
import requests as stdlib_requests
import re, urllib.parse, hashlib, random, traceback, uuid, json, time, base64, math 

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Util import Counter


# FP Generator

CHROME_VERSIONS = [120, 123, 124, 131, 136, 142]
IMPERSONATE_MAP = {
    120: "chrome120", 123: "chrome123", 124: "chrome124",
    131: "chrome131", 136: "chrome136", 142: "chrome142",
}

SCREEN_RESOLUTIONS = [
    "1920x1080", "1366x768", "1536x864", "1440x900", "1280x720",
    "1600x900", "2560x1440", "1920x1200",
]

PLATFORMS = {
    "Windows": {
        "ua":  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36",
        "nav": "Win32",
        "sec": '"Windows"',
    },
    "Linux": {
        "ua":  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36",
        "nav": "Linux x86_64",
        "sec": '"Linux"',
    },
    "macOS": {
        "ua":  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36",
        "nav": "MacIntel",
        "sec": '"macOS"',
    },
}

LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8",
    "en-US,en;q=0.9,es;q=0.7",
]


def _random_fingerprint():
    plat_name = random.choice(list(PLATFORMS))
    plat = PLATFORMS[plat_name]
    v = random.choice(CHROME_VERSIONS)
    res = random.choice(SCREEN_RESOLUTIONS)

    brand_orders = [
        f'"Chromium";v="{v}", "Not:A-Brand";v="24", "Google Chrome";v="{v}"',
        f'"Google Chrome";v="{v}", "Chromium";v="{v}", "Not:A-Brand";v="24"',
    ]

    return {
        "user_agent":        plat["ua"].format(v=v),
        "platform":          plat_name,
        "navigator_platform": plat["nav"],
        "sec_ch_ua":         random.choice(brand_orders),
        "sec_ch_ua_platform": plat["sec"],
        "language":          random.choice(LANGUAGES),
        "resolution":        res,
        "chrome_version":    v,
    }


def _build_session(fp):
    impersonate = IMPERSONATE_MAP[fp["chrome_version"]]
    session = cffi_requests.Session(impersonate=impersonate)

    session.headers.update({
        "User-Agent":                fp["user_agent"],
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language":           fp["language"],
        "Accept-Encoding":           "gzip, deflate, br, zstd",
        "Connection":                "keep-alive",
        "Sec-CH-UA":                 fp["sec_ch_ua"],
        "Sec-CH-UA-Mobile":          "?0",
        "Sec-CH-UA-Platform":        fp["sec_ch_ua_platform"],
        "Sec-Fetch-Dest":            "document",
        "Sec-Fetch-Mode":            "navigate",
        "Sec-Fetch-Site":            "none",
        "Sec-Fetch-User":            "?1",
        "Upgrade-Insecure-Requests": "1",
    })

    return session


def _get_param(url, param):
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    values = params.get(param, [])
    return values[0] if values else None


def encrypt_ctr(plain: str, key: bytes, iv: bytes) -> str:
    cipher = Cipher(
        algorithms.AES(key),
        modes.CTR(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ct = encryptor.update(plain.encode('utf-8')) + encryptor.finalize()
    return ct.hex()


def generate_stream(ticket: str) -> str:
    now = int(time.time() * 1000)
    events = []

    click_time = now - random.randint(80, 400)
    click_x = random.randint(350, 550)
    click_y = random.randint(280, 420)

    events.append({"event": 1, "data": {"x": click_x, "y": click_y, "target": "BUTTON", "time": click_time}})
    events.append({"event": 1, "data": {"x": click_x, "y": click_y, "target": "BUTTON", "time": click_time}})
    events.append({"event": 0, "data": {
        "x": click_x + random.randint(-15, 15),
        "y": click_y + random.randint(-15, 15),
        "target": "BUTTON",
        "time": click_time - random.randint(30, 150),
    }})
    events.append({"event": 5, "data": {"time": now, "length": 0}})

    payload = json.dumps({"events": events}, separators=(",", ":"))

    key = bytes(ord(c) for c in ticket[1:17])
    counter = bytes(ord(c) for c in ticket[17:33])
    ctr = Counter.new(128, initial_value=int.from_bytes(counter, "big"))
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return cipher.encrypt(payload.encode("utf-8")).hex() # what the fuck is this shit


# Captcha solver (frfr (it works)).

def solve_captcha():
    for _ in range(37):
        cap_session = None
        try:
            fp = _random_fingerprint()
            cap_session = _build_session(fp)

            cap_session.headers.update({
                "Accept": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "Origin": "https://auth.platorelay.com",
                "Referer": "https://auth.platorelay.com/",
            })
            cap_session.headers.pop("Upgrade-Insecure-Requests", None)
            cap_session.headers.pop("Sec-Fetch-User", None)

            orchesta = cap_session.get("https://captcha.platorelay.com/api/challenge").json()
            chalid = orchesta.get("challenge_id")

            # platoboost captcha always sends the same challenges, to bypass it you only need to send one till it works!
            # the ramdon.randint shit is retarded but i feel like it helps, i know it isn't helping but sasudiqw'0ai0qh

            if random.randint(1, 2) == 1:
                x, y = 285.8291457286432, 88.97690559924033
            else:
                x, y = 209.84924623115577, 152.5210684836765

            dead = cap_session.post(
                "https://captcha.platorelay.com/api/answer",
                json={"challenge_id": chalid, "x": x, "y": y}, # x y :nerd_tone5:
            ).json()

            if dead.get("success", False):
                debug.custom("DeltaXP", f"CID : {chalid} - SOLVED!", "BLUE", "🥷")
                return dead.get("token")
        except Exception:
            pass
        finally:
            if cap_session:
                try:
                    cap_session.close()
                except Exception:
                    pass

    return "loop ended, maybe a proxy fail?"



def checkKey(ticket, session):
    return session.get(
        f"https://auth.platorelay.com/api/session/status?ticket={ticket}"
    ).json().get("data", {}).get("key")


def trw_sse(url, **kwargs):
    with stdlib_requests.get(url, stream=True, **kwargs) as r:
        for line in r.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")

            if line.startswith("data: "):
                line = line[6:]

            data = json.loads(line)
            if data["status"] == "success":
                return data["result"]


# verbose is a option for TRW-API, ignore it ngl i'm just too lazy to remove it

def getKey(url, verbose_cb=None):
    vcb = verbose_cb or (lambda msg: None)
    vcb("Obtaining DeltaX session with Chrome TLS fingerprint...")

    fp = _random_fingerprint()
    session = _build_session(fp)

    session.headers.update({
        "Accept":            "application/json",
        "X-Client-Name":     "platoboost webclient",
        "X-Client-Version":  "5.3.2",
        "Sec-Fetch-Dest":    "empty",
        "Sec-Fetch-Mode":    "cors",
        "Sec-Fetch-Site":    "same-origin",
    })
    session.headers.pop("Sec-Fetch-User", None)
    session.headers.pop("Upgrade-Insecure-Requests", None)

    try:
        ticket = _get_param(url, "d")
        hash_param = _get_param(url, "hash")

        session.headers["Referer"] = f"https://auth.platorelay.com/{ticket}/"

        if checkKey(ticket, session) != "KEY_NOT_FOUND":
            vcb("Key already available, no bypass needed")
            return checkKey(ticket, session)

        vcb("Key not found, starting DeltaX bypass flow...")

        def getMeta(tk):
            if not tk or len(tk) < 32:
                return "empty"

            key = tk[:16].encode("utf-8")
            iv  = tk[16:32].encode("utf-8")

            screen = fp["resolution"].split("x")
            nav_platform = fp["navigator_platform"]

            info = [
                {
                    "name": "screen",
                    "data": {
                        "width": int(screen[0]), "height": int(screen[1]),
                        "availWidth": int(screen[0]), "availHeight": int(screen[1]),
                        "colorDepth": 24, "pixelDepth": 24,
                        "orientation": {"type": "landscape-primary", "angle": 0},
                    },
                },
                {
                    "name": "navigator",
                    "data": {
                        "userAgent": session.headers.get("User-Agent", ""),
                        "platform": nav_platform,
                        "maxTouchPoints": 0,
                        "plugins": {
                            "length": 5,
                            "item": [
                                {"name": "PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                                {"name": "Chrome PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                                {"name": "Chromium PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                                {"name": "Microsoft Edge PDF Viewer", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                                {"name": "WebKit built-in PDF", "filename": "internal-pdf-viewer", "description": "Portable Document Format"},
                                # ngl i should make this better but i don't care, its YOUR script now
                            ],
                        },
                        "mimeTypes": {
                            "length": 2,
                            "item": [
                                {"type": "application/pdf", "description": "Portable Document Format", "suffixes": "pdf"},
                                {"type": "text/pdf", "description": "Portable Document Format", "suffixes": "pdf"},
                            ],
                        },
                    },
                },
                {"name": "performance", "data": int(time.time() * 1000)},
                {"name": "history", "data": {"length": random.randint(1, 4)}},
                {"name": "webdriver", "webdriver": False},
                {
                    "name": "connection",
                    "data": {
                        "effectiveType": "4g",
                        "downlink": round(random.uniform(1.5, 10.0), 1),
                        "rtt": random.choice([50, 100, 150, 200]),
                        "saveData": False,
                    },
                },
            ]

            payload = json.dumps({"browserInfo": info}, separators=(",", ":"))
            try:
                return encrypt_ctr(payload, key, iv)
            except Exception:
                return "empty"

        resolved = True

        session.get(f"https://auth.platorelay.com/api/session/metadata?ticket={ticket}").close()

        meta = getMeta(ticket)
        time.sleep(5)

        for i in range(3):
            vcb(f"DeltaX step attempt {i + 1}/3...")

            payload = {
                "captcha": None,
                "meta": meta,
                "stream": generate_stream(ticket),
                "resolved": resolved,
            }

            step_url = f"https://auth.platorelay.com/api/session/step?ticket={ticket}&service=2"
            if hash_param:
                step_url += f"&hash={hash_param}"

            stepsis = session.put(step_url, json=payload).json()

            if stepsis.get("data", {}).get("url"):
                break

            vcb("Solving DeltaX captcha...")
            cap = solve_captcha()

            payload["captcha"] = cap
            payload["stream"] = generate_stream(ticket)

            stepsis = session.put(step_url, json=payload).json()
            if "please complete" in str(stepsis):
                continue
            break
        else:
            return "bypass fail! error solving captcha!"

        vcb("DeltaX step completed, obtained loot-link URL")
        debug.custom("DeltaXP", "Obtained loot-link, bypassing...", "BLUE", "🥷")
        loot_url = stepsis.get("data", {}).get("url")
        vcb("Bypassing inner loot-link...")

        # we using the BEST api for this, trw-api bypasses loot-links better than any other api out there (it isn't working 90% of the time but when it works its fast as fuck (30s (or less  (fr))))

        with stdlib_requests.get("https://trw.lat/api/lvlol/captchaLess") as apikey_resp:
            apikey = apikey_resp.json()["freeKey"]

        try:
            result = trw_sse(
                f"https://trw.lat/api/bypass?url={urllib.parse.quote(loot_url)}&mode=stream&verbose=true",
                headers={"x-api-key": apikey},
            )
        except Exception:
            return "bypass fail! trw-api didn't solve the loot-link url properly"

        ticket = _get_param(result, "d")
        hash_param = _get_param(result, "hash")

        session.headers["Referer"] = f"https://auth.platorelay.com/{ticket}/"

        if checkKey(ticket, session) != "KEY_NOT_FOUND":
            return checkKey(ticket, session)

        session.get(f"https://auth.platorelay.com/api/session/status?ticket={ticket}").close()
        session.get(f"https://auth.platorelay.com/api/session/metadata?ticket={ticket}").close()

        meta = getMeta(ticket)
        time.sleep(5)

        payload = {
            "captcha": None,
            "meta": meta,
            "stream": generate_stream(ticket),
            "resolved": resolved,
        }

        step_url = f"https://auth.platorelay.com/api/session/step?ticket={ticket}&service=2"
        if hash_param:
            step_url += f"&hash={hash_param}"

        session.put(step_url, json=payload).json()

        if checkKey(ticket, session) != "KEY_NOT_FOUND":
            return checkKey(ticket, session)

        return "bypass fail! nok ey found"
    except Exception:
        debug.custom("DeltaXP", f"{traceback.format_exc()}", "RED", "💀")

        return "bypass fail! traceback found!"
    finally: 
        try:
            session.close()
        except Exception:
            pass
