"""
MR TRADE v6.0 - Legendary Edition
Pydroid 3 ready
pip install kivymd==1.1.1 kivy requests
"""

import os, sys, time, uuid, threading, webbrowser
import xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.label import Label as KVLabel
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.properties import ListProperty

Window.softinput_mode = 'below_target'

try:
    from kivymd.app import MDApp
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.screenmanager import MDScreenManager
    from kivymd.uix.scrollview import MDScrollView
    from kivymd.uix.button import MDFlatButton, MDIconButton
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.snackbar import Snackbar
    from kivymd.uix.selectioncontrol import MDSwitch
except Exception as e:
    print(f"KIVYMD ERROR: {e}"); sys.exit(1)


# ============================================================
# THEME
# ============================================================

LIGHT = {
    "bg": [0.97, 0.97, 0.98, 1], "card": [1, 1, 1, 1],
    "text": [0.08, 0.08, 0.10, 1], "dim": [0.50, 0.50, 0.55, 1],
    "faint": [0.72, 0.72, 0.76, 1], "header": [0.06, 0.08, 0.14, 1],
    "accent": [0.18, 0.48, 0.80, 1], "up": [0.10, 0.72, 0.28, 1],
    "down": [0.88, 0.22, 0.22, 1], "neutral": [0.55, 0.55, 0.58, 1],
    "line": [0.88, 0.88, 0.90, 1], "chip": [0.93, 0.95, 0.98, 1],
    "bubble_me": [0.82, 0.93, 1.0, 1], "bubble_other": [1, 1, 1, 1],
    "chat_bg": [0.88, 0.91, 0.94, 1],
}
DARK = {
    "bg": [0.05, 0.06, 0.09, 1], "card": [0.11, 0.13, 0.18, 1],
    "text": [0.93, 0.94, 0.96, 1], "dim": [0.58, 0.60, 0.65, 1],
    "faint": [0.40, 0.42, 0.47, 1], "header": [0.03, 0.04, 0.07, 1],
    "accent": [0.25, 0.58, 0.92, 1], "up": [0.22, 0.85, 0.42, 1],
    "down": [0.95, 0.38, 0.38, 1], "neutral": [0.62, 0.62, 0.65, 1],
    "line": [0.18, 0.20, 0.26, 1], "chip": [0.15, 0.17, 0.23, 1],
    "bubble_me": [0.12, 0.32, 0.50, 1], "bubble_other": [0.15, 0.17, 0.23, 1],
    "chat_bg": [0.04, 0.05, 0.08, 1],
}


def colors(dark):
    return DARK if dark else LIGHT


AVATAR_COLORS = [
    [0.85, 0.35, 0.35, 1], [0.35, 0.65, 0.85, 1], [0.35, 0.80, 0.55, 1],
    [0.90, 0.60, 0.25, 1], [0.65, 0.40, 0.85, 1], [0.25, 0.75, 0.75, 1],
    [0.85, 0.45, 0.65, 1], [0.55, 0.55, 0.90, 1], [0.75, 0.65, 0.35, 1],
    [0.40, 0.70, 0.90, 1], [0.90, 0.50, 0.40, 1], [0.30, 0.60, 0.50, 1],
]


def avatar_color(name):
    if not name: return AVATAR_COLORS[0]
    return AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]


def initials(name):
    if not name: return "?"
    p = name.strip().split()
    if len(p) >= 2: return (p[0][0] + p[1][0]).upper()
    return name[:2].upper()


def time_ago(ts):
    if not ts: return ""
    d = time.time() - ts
    if d < 60: return "now"
    if d < 3600: return f"{int(d/60)}m"
    if d < 86400: return f"{int(d/3600)}h"
    return datetime.fromtimestamp(ts).strftime("%H:%M")


def loading_box(text="Loading...", dark=False):
    c = colors(dark)
    box = MDBoxLayout(orientation="vertical", size_hint_y=None,
                      height=dp(70), padding=dp(10))
    box.add_widget(MDLabel(text=text, halign="center", font_style="Body2",
                           theme_text_color="Custom", text_color=c["dim"]))
    return box


def empty_state(text, dark=False):
    c = colors(dark)
    box = MDBoxLayout(orientation="vertical", size_hint_y=None,
                      height=dp(100), padding=dp(14))
    box.add_widget(MDLabel(text=text, font_style="Body2", halign="center",
                           theme_text_color="Custom", text_color=c["faint"]))
    return box


def animate_in(w, delay=0, dur=0.25):
    w.opacity = 0
    if delay <= 0:
        Animation(opacity=1, duration=dur, t="out_cubic").start(w)
    else:
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=dur, t="out_cubic").start(w),
            delay)


# ============================================================
# ASSET AVATAR - FIXED CENTERING
# ============================================================

class AssetAvatar(Widget):
    """Circle with initials - FIXED centering using plain KV Label"""

    def __init__(self, name, size=dp(42), font=dp(14), **kw):
        super().__init__(**kw)
        self.size_hint = (None, None)
        self.size = (size, size)
        col = avatar_color(name)
        with self.canvas:
            self._c = Color(*col)
            self._r = RoundedRectangle(pos=self.pos, size=self.size,
                                       radius=[size / 2])
        self.bind(pos=self._upd, size=self._upd)

        # Plain Label - centers automatically
        lbl = KVLabel(
            text=initials(name),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=font,
            halign="center",
            valign="middle",
            size=self.size,
            pos=self.pos,
            size_hint=(None, None),
            markup=False)
        # Center text inside label
        lbl.bind(size=lambda s, v: setattr(s, "text_size", v))
        self._lbl = lbl
        self.add_widget(lbl)

    def _upd(self, *a):
        self._r.pos = self.pos
        self._r.size = self.size
        # Center label in widget
        self._lbl.pos = self.pos
        self._lbl.size = self.size


# ============================================================
# SPARKLINE - 30 days, 1/4 screen width
# ============================================================

class Sparkline(Widget):
    def __init__(self, width=None, height=dp(34), show_fill=True, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None)
        if width is None:
            width = Window.width * 0.25  # 1/4 of screen
        self.size = (width, height)
        self.show_fill = show_fill
        self._values = []
        with self.canvas:
            self._fill_c = Color(0.2, 0.7, 0.3, 0.12)
            self._fill = Line(width=0)
            self._line_c = Color(0.2, 0.7, 0.3, 1)
            self._line = Line(width=1.8)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_data(self, values, positive=True):
        self._values = values or []
        if positive:
            col = (0.15, 0.80, 0.35, 1)
            fill = (0.15, 0.80, 0.35, 0.12)
        else:
            col = (0.95, 0.30, 0.30, 1)
            fill = (0.95, 0.30, 0.30, 0.12)
        self._line_c.rgba = col
        self._fill_c.rgba = fill
        self._redraw()

    def _redraw(self, *a):
        if len(self._values) < 2:
            self._line.points = []
            self._fill.points = []
            return
        mn, mx = min(self._values), max(self._values)
        rng = (mx - mn) or 1
        w = self.width - dp(4)
        h = self.height - dp(6)
        x0 = self.x + dp(2)
        y0 = self.y + dp(3)
        pts = []
        n = len(self._values) - 1
        for i, v in enumerate(self._values):
            x = x0 + (i / n) * w
            y = y0 + ((v - mn) / rng) * h
            pts.extend([x, y])
        self._line.points = pts
        if self.show_fill and len(pts) >= 4:
            fill_pts = list(pts) + [x0 + w, y0, x0, y0]
            self._fill.points = fill_pts
        else:
            self._fill.points = []


# ============================================================
# CONFIG
# ============================================================

ALL_SOURCES = [
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", "world"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "finance"),
    ("BBC Tech", "http://feeds.bbci.co.uk/news/technology/rss.xml", "world"),
    ("CNN Top", "http://rss.cnn.com/rss/cnn_topstories.rss", "world"),
    ("CNN World", "http://rss.cnn.com/rss/cnn_world.rss", "world"),
    ("CNN Business", "http://rss.cnn.com/rss/money_latest.rss", "finance"),
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", "crypto"),
    ("Cointelegraph", "https://cointelegraph.com/rss", "crypto"),
    ("Bitcoin Magazine", "https://bitcoinmagazine.com/.rss/full/", "crypto"),
    ("CryptoSlate", "https://cryptoslate.com/feed/", "crypto"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex", "finance"),
    ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/topstories/", "finance"),
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews", "finance"),
    ("Reuters Tech", "https://feeds.reuters.com/reuters/technologyNews", "world"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "world"),
    ("TechCrunch", "https://techcrunch.com/feed/", "world"),
    ("CNBC Markets", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", "finance"),
    ("Investing.com Forex", "https://www.investing.com/rss/news_1.rss", "finance"),
    ("Investing.com Crypto", "https://www.investing.com/rss/news_301.rss", "crypto"),
    ("ForexLive", "https://www.forexlive.com/feed/news", "finance"),
    ("ZeroHedge", "https://feeds.feedburner.com/zerohedge/feed", "finance"),
    ("Nasdaq News", "https://www.nasdaq.com/feed/rssoutbound?category=Markets", "finance"),
]

ASSET_KEYWORDS = {
    "BITCOIN": ["bitcoin", "btc", "satoshi"], "ETHEREUM": ["ethereum", "vitalik"],
    "RIPPLE": ["ripple", " xrp"], "CARDANO": ["cardano"], "BINANCE COIN": ["binance coin"],
    "SOLANA": ["solana"], "POLKADOT": ["polkadot"], "LITECOIN": ["litecoin"],
    "CHAINLINK": ["chainlink"], "DOGECOIN": ["dogecoin", "doge"], "TRON": ["tron"],
    "POLYGON": ["polygon", "matic"], "AVALANCHE": ["avalanche", "avax"],
    "SHIBA INU": ["shiba inu"], "STELLAR": ["stellar", " xlm"], "UNISWAP": ["uniswap"],
    "COSMOS": ["cosmos"], "MONERO": ["monero"], "EOS": ["eos token"],
    "FILECOIN": ["filecoin"], "NEAR": ["near protocol"], "APTOS": ["aptos"],
    "ARBITRUM": ["arbitrum"], "OPTIMISM": ["optimism"], "HEDERA": ["hedera"],
    "ALGORAND": ["algorand"], "FANTOM": ["fantom"], "THE GRAPH": ["the graph"],
    "INJECTIVE": ["injective"], "SUI": ["sui network"], "VECHAIN": ["vechain"],
    "THETA": ["theta network"],
    "APPLE": ["apple", "iphone", "aapl"], "TESLA": ["tesla", "elon musk", "tsla"],
    "AMAZON": ["amazon", "amzn"], "GOOGLE": ["google", "alphabet", "googl"],
    "MICROSOFT": ["microsoft", "msft"], "META": ["meta platforms", "facebook"],
    "NVIDIA": ["nvidia", "nvda"], "NETFLIX": ["netflix", "nflx"],
    "AMD": ["advanced micro"], "INTEL": ["intel", "intc"],
    "COCA-COLA": ["coca-cola", "coca cola"], "DISNEY": ["disney"],
    "ADOBE": ["adobe", "adbe"], "SALESFORCE": ["salesforce"], "ORACLE": ["oracle corp"],
    "IBM": [" ibm "], "QUALCOMM": ["qualcomm"], "BROADCOM": ["broadcom"],
    "TEXAS INSTRUMENTS": ["texas instruments"], "MICRON": ["micron"],
    "JPMORGAN": ["jpmorgan"], "BANK OF AMERICA": ["bank of america"],
    "VISA": ["visa inc"], "MASTERCARD": ["mastercard"], "GOLDMAN SACHS": ["goldman sachs"],
    "JOHNSON & JOHNSON": ["johnson & johnson"], "PFIZER": ["pfizer"],
    "MERCK": ["merck"], "WALMART": ["walmart"], "NIKE": ["nike"],
    "MCDONALDS": ["mcdonald"], "PAYPAL": ["paypal"], "UBER": ["uber"],
    "GOLD": ["gold price", " xau", "bullion"], "OIL": ["oil price", "crude", "brent", "wti"],
    "SILVER": ["silver price", " xag"], "NATURAL GAS": ["natural gas"],
    "COPPER": ["copper price"], "PLATINUM": ["platinum"], "PALLADIUM": ["palladium"],
    "COFFEE": ["coffee price"], "SUGAR": ["sugar price"], "COTTON": ["cotton price"],
    "S&P 500": ["s&p 500", "s&p500", "sp500"], "NASDAQ": ["nasdaq", "ixic"],
    "DOW JONES": ["dow jones", "djia"], "FTSE 100": ["ftse 100"],
    "DAX": ["dax index"], "NIKKEI": ["nikkei"], "CAC 40": ["cac 40"],
    "RUSSELL 2000": ["russell 2000"], "VIX": ["vix index", "fear index"],
    "HANG SENG": ["hang seng"], "ASX 200": ["asx 200"],
}

MARKETS_CONFIG = {
    "CRYPTO CURRENCY": {"type": "CRYPTO", "assets": [
        "BITCOIN", "ETHEREUM", "RIPPLE", "CARDANO", "BINANCE COIN",
        "SOLANA", "POLKADOT", "LITECOIN", "CHAINLINK", "DOGECOIN",
        "TRON", "POLYGON", "AVALANCHE", "SHIBA INU", "STELLAR",
        "UNISWAP", "COSMOS", "MONERO", "EOS", "FILECOIN",
        "NEAR", "APTOS", "ARBITRUM", "OPTIMISM", "HEDERA",
        "ALGORAND", "FANTOM", "THE GRAPH", "INJECTIVE", "SUI",
        "VECHAIN", "THETA"]},
    "FOREX MARKET": {"type": "FOREX", "assets": [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
        "USD/CHF", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY",
        "EUR/CHF", "EUR/AUD", "EUR/CAD", "EUR/NZD",
        "GBP/CHF", "GBP/AUD", "GBP/CAD", "GBP/NZD",
        "AUD/JPY", "AUD/CAD", "AUD/CHF", "AUD/NZD",
        "CAD/JPY", "CAD/CHF", "CHF/JPY",
        "USD/MXN", "USD/ZAR", "USD/TRY"]},
    "STOCKS": {"type": "STOCKS", "assets": [
        "APPLE", "TESLA", "AMAZON", "GOOGLE", "MICROSOFT", "META",
        "NVIDIA", "NETFLIX", "AMD", "INTEL", "COCA-COLA", "DISNEY",
        "ADOBE", "SALESFORCE", "ORACLE", "IBM", "QUALCOMM",
        "BROADCOM", "TEXAS INSTRUMENTS", "MICRON",
        "JPMORGAN", "BANK OF AMERICA", "VISA", "MASTERCARD",
        "GOLDMAN SACHS", "JOHNSON & JOHNSON", "PFIZER", "MERCK",
        "WALMART", "NIKE", "MCDONALDS", "PAYPAL", "UBER"]},
    "COMMODITIES": {"type": "COMMODITIES", "assets": [
        "GOLD", "OIL", "SILVER", "NATURAL GAS", "COPPER",
        "PLATINUM", "PALLADIUM", "COFFEE", "SUGAR", "COTTON"]},
    "INDICES": {"type": "INDICES", "assets": [
        "S&P 500", "NASDAQ", "DOW JONES", "FTSE 100", "DAX",
        "NIKKEI", "CAC 40", "RUSSELL 2000", "VIX", "HANG SENG",
        "ASX 200"]},
    "FUTURES": {"type": "FUTURES", "assets": [
        "S&P 500", "OIL", "GOLD", "NASDAQ", "SILVER", "COPPER"]},
}

# Ticker assets for Live screen
TICKER_ASSETS = [
    ("BITCOIN", "CRYPTO"), ("ETHEREUM", "CRYPTO"), ("SOLANA", "CRYPTO"),
    ("BINANCE COIN", "CRYPTO"), ("RIPPLE", "CRYPTO"), ("CARDANO", "CRYPTO"),
    ("DOGECOIN", "CRYPTO"), ("AVALANCHE", "CRYPTO"), ("POLYGON", "CRYPTO"),
    ("CHAINLINK", "CRYPTO"), ("LITECOIN", "CRYPTO"), ("POLKADOT", "CRYPTO"),
    ("GOLD", "COMMODITIES"), ("SILVER", "COMMODITIES"), ("OIL", "COMMODITIES"),
    ("PLATINUM", "COMMODITIES"), ("NATURAL GAS", "COMMODITIES"),
    ("COPPER", "COMMODITIES"), ("PALLADIUM", "COMMODITIES"),
]

CRYPTO_BINANCE = {
    "BITCOIN": "BTCUSDT", "ETHEREUM": "ETHUSDT", "RIPPLE": "XRPUSDT",
    "CARDANO": "ADAUSDT", "BINANCE COIN": "BNBUSDT", "SOLANA": "SOLUSDT",
    "POLKADOT": "DOTUSDT", "LITECOIN": "LTCUSDT", "CHAINLINK": "LINKUSDT",
    "DOGECOIN": "DOGEUSDT", "TRON": "TRXUSDT", "POLYGON": "MATICUSDT",
    "AVALANCHE": "AVAXUSDT", "SHIBA INU": "SHIBUSDT", "STELLAR": "XLMUSDT",
    "UNISWAP": "UNIUSDT", "COSMOS": "ATOMUSDT", "MONERO": "XMRUSDT",
    "EOS": "EOSUSDT", "FILECOIN": "FILUSDT", "NEAR": "NEARUSDT",
    "APTOS": "APTUSDT", "ARBITRUM": "ARBUSDT", "OPTIMISM": "OPUSDT",
    "HEDERA": "HBARUSDT", "ALGORAND": "ALGOUSDT", "FANTOM": "FTMUSDT",
    "THE GRAPH": "GRTUSDT", "INJECTIVE": "INJUSDT", "SUI": "SUIUSDT",
    "VECHAIN": "VETUSDT", "THETA": "THETAUSDT",
}

FOREX_YAHOO = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "USDCAD=X", "USD/CHF": "USDCHF=X",
    "NZD/USD": "NZDUSD=X", "EUR/GBP": "EURGBP=X", "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X", "EUR/CHF": "EURCHF=X", "EUR/AUD": "EURAUD=X",
    "EUR/CAD": "EURCAD=X", "EUR/NZD": "EURNZD=X", "GBP/CHF": "GBPCHF=X",
    "GBP/AUD": "GBPAUD=X", "GBP/CAD": "GBPCAD=X", "GBP/NZD": "GBPNZD=X",
    "AUD/JPY": "AUDJPY=X", "AUD/CAD": "AUDCAD=X", "AUD/CHF": "AUDCHF=X",
    "AUD/NZD": "AUDNZD=X", "CAD/JPY": "CADJPY=X", "CAD/CHF": "CADCHF=X",
    "CHF/JPY": "CHFJPY=X", "USD/MXN": "USDMXN=X", "USD/ZAR": "USDZAR=X",
    "USD/TRY": "USDTRY=X",
}

YAHOO_TICKERS = {
    "APPLE": "AAPL", "TESLA": "TSLA", "AMAZON": "AMZN", "GOOGLE": "GOOGL",
    "MICROSOFT": "MSFT", "META": "META", "NVIDIA": "NVDA", "NETFLIX": "NFLX",
    "AMD": "AMD", "INTEL": "INTC", "COCA-COLA": "KO", "DISNEY": "DIS",
    "ADOBE": "ADBE", "SALESFORCE": "CRM", "ORACLE": "ORCL", "IBM": "IBM",
    "QUALCOMM": "QCOM", "BROADCOM": "AVGO", "TEXAS INSTRUMENTS": "TXN",
    "MICRON": "MU", "JPMORGAN": "JPM", "BANK OF AMERICA": "BAC",
    "VISA": "V", "MASTERCARD": "MA", "GOLDMAN SACHS": "GS",
    "JOHNSON & JOHNSON": "JNJ", "PFIZER": "PFE", "MERCK": "MRK",
    "WALMART": "WMT", "NIKE": "NKE", "MCDONALDS": "MCD",
    "PAYPAL": "PYPL", "UBER": "UBER",
    "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DOW JONES": "^DJI",
    "FTSE 100": "^FTSE", "DAX": "^GDAXI", "NIKKEI": "^N225",
    "CAC 40": "^FCHI", "RUSSELL 2000": "^RUT", "VIX": "^VIX",
    "HANG SENG": "^HSI", "ASX 200": "^AXJO",
    "GOLD": "GC=F", "OIL": "CL=F", "SILVER": "SI=F",
    "NATURAL GAS": "NG=F", "COPPER": "HG=F", "PLATINUM": "PL=F",
    "PALLADIUM": "PA=F", "COFFEE": "KC=F", "SUGAR": "SB=F",
    "COTTON": "CT=F",
}


def make_screen_key(prefix, name):
    return f"{prefix}_{name.lower().replace(' ', '_').replace('/', '_').replace('&', 'and')}"


def is_market_open(mt):
    now = datetime.utcnow(); wd = now.weekday()
    if mt == "CRYPTO": return True
    if mt == "FOREX":
        if wd == 5: return False
        if wd == 6 and now.hour < 21: return False
        if wd == 4 and now.hour >= 21: return False
        return True
    if mt in ("STOCKS", "INDICES", "COMMODITIES", "FUTURES"): return wd <= 4
    return True


def fmt_price(p):
    if p >= 1000: return f"${p:,.0f}"
    if p >= 100: return f"${p:,.2f}"
    if p >= 1: return f"${p:,.3f}"
    return f"${p:.5f}"


# ============================================================
# DATA MANAGER
# ============================================================

class DataManager:
    def __init__(self, store, chat_store):
        self.store = store
        self.chat_store = chat_store
        self.price_cache = {}
        self.price_time = {}
        self.spark_cache = {}
        self.is_online = True
        self.last_check = 0
        self._lock = threading.Lock()
        self.all_articles = []
        self.asset_news_index = {}
        self.news_fetched_at = 0
        self.news_loading = False
        self.news_ready = False
        self._news_lock = threading.Lock()
        # Fear & Greed
        self.fear_greed = None
        self.fear_greed_fetched = 0

        if not self.store.exists("watchlist"):
            self.store.put("watchlist", items=[])
        if not self.store.exists("settings"):
            self.store.put("settings", dark=False)
        if not self.store.exists("user"):
            self.store.put("user", uid=str(uuid.uuid4())[:8], name="")
        if not self.chat_store.exists("messages"):
            self.chat_store.put("messages", items=[])

    def get_uid(self): return self.store.get("user")["uid"]
    def get_uname(self): return self.store.get("user")["name"] or "Me"
    def set_uname(self, name):
        u = self.store.get("user"); u["name"] = name
        self.store.put("user", **u)

    def get_watchlist(self): return list(self.store.get("watchlist")["items"])
    def add_watch(self, a, mt):
        wl = self.get_watchlist(); e = {"asset": a, "type": mt}
        if e not in wl:
            wl.append(e); self.store.put("watchlist", items=wl); return True
        return False
    def remove_watch(self, a):
        wl = [w for w in self.get_watchlist() if w["asset"] != a]
        self.store.put("watchlist", items=wl)
    def is_watched(self, a):
        return any(w["asset"] == a for w in self.get_watchlist())

    def get_dark(self): return self.store.get("settings").get("dark", False)
    def set_dark(self, v):
        s = self.store.get("settings"); s["dark"] = v
        self.store.put("settings", **s)

    def add_message(self, author, text):
        msgs = self.chat_store.get("messages")["items"]
        msg = {"id": str(uuid.uuid4())[:8], "uid": self.get_uid(),
               "author": author or "Anonymous", "text": text or "",
               "ts": time.time()}
        msgs.append(msg)
        if len(msgs) > 10000: msgs = msgs[-10000:]
        self.chat_store.put("messages", items=msgs)
        return msg
    def get_messages(self, limit=500):
        msgs = self.chat_store.get("messages")["items"]
        return sorted(msgs, key=lambda x: x.get("ts", 0))[-limit:]

    def check_internet(self):
        now = time.time()
        if now - self.last_check < 30: return self.is_online
        self.last_check = now
        try:
            requests.get("https://api.binance.com/api/v3/ping", timeout=3)
            self.is_online = True
        except Exception:
            self.is_online = False
        return self.is_online

    def get_price(self, symbol, mt):
        if not self.check_internet(): return 0, 0, "Offline"
        key = f"{symbol}|{mt}"
        now = time.time()
        with self._lock:
            if key in self.price_cache and now - self.price_time.get(key, 0) < 30:
                return self.price_cache[key]
        price, change, source = 0, 0, "N/A"
        try:
            if mt == "CRYPTO":
                price, change, source = self._binance(symbol)
            elif mt == "FOREX":
                price, change, source = self._yahoo(FOREX_YAHOO.get(symbol), "Yahoo FX")
            elif mt in ("STOCKS", "INDICES", "COMMODITIES", "FUTURES"):
                price, change, source = self._yahoo(YAHOO_TICKERS.get(symbol), "Yahoo")
        except Exception as e:
            print(f"[Price] {symbol}: {e}")
        if price > 0:
            with self._lock:
                self.price_cache[key] = (price, change, source)
                self.price_time[key] = now
        return price, change, source

    def _binance(self, s):
        p = CRYPTO_BINANCE.get(s)
        if not p: return 0, 0, "N/A"
        try:
            r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={p}",
                             timeout=6)
            if r.status_code == 200:
                d = r.json()
                return float(d["lastPrice"]), float(d["priceChangePercent"]), "Binance"
        except Exception as e: print(f"[BNB] {e}")
        return 0, 0, "failed"

    def _yahoo(self, t, label):
        if not t: return 0, 0, "N/A"
        try:
            r = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{t}"
                f"?interval=1d&range=5d", timeout=8,
                headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                res = r.json().get("chart", {}).get("result", [])
                if res:
                    m = res[0].get("meta", {})
                    p = m.get("regularMarketPrice")
                    prev = m.get("chartPreviousClose") or m.get("previousClose")
                    if p and prev: return p, ((p - prev) / prev) * 100, label
                    if p: return p, 0, label
        except Exception as e: print(f"[{label}] {e}")
        return 0, 0, "failed"

    # 30-DAY SPARKLINE
    def get_sparkline(self, symbol, mt):
        key = f"{symbol}|{mt}"
        if key in self.spark_cache: return self.spark_cache[key]
        values = []
        try:
            if mt == "CRYPTO":
                pair = CRYPTO_BINANCE.get(symbol)
                if pair:
                    r = requests.get(
                        f"https://api.binance.com/api/v3/klines"
                        f"?symbol={pair}&interval=1d&limit=30", timeout=8)
                    if r.status_code == 200:
                        values = [float(k[4]) for k in r.json()]
            else:
                t = YAHOO_TICKERS.get(symbol) or FOREX_YAHOO.get(symbol)
                if t:
                    r = requests.get(
                        f"https://query1.finance.yahoo.com/v8/finance/chart/{t}"
                        f"?interval=1d&range=1mo", timeout=8,
                        headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200:
                        res = r.json().get("chart", {}).get("result", [])
                        if res:
                            q = res[0].get("indicators", {}).get("quote", [{}])[0]
                            values = [v for v in q.get("close", []) if v is not None]
        except Exception as e:
            print(f"[Spark] {symbol}: {e}")
        self.spark_cache[key] = values
        return values

    # Fear & Greed
    def get_fear_greed(self):
        if self.fear_greed and time.time() - self.fear_greed_fetched < 3600:
            return self.fear_greed
        try:
            r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
            if r.status_code == 200:
                d = r.json().get("data", [{}])[0]
                self.fear_greed = {
                    "value": int(d.get("value", 50)),
                    "label": d.get("value_classification", "Neutral")
                }
                self.fear_greed_fetched = time.time()
                return self.fear_greed
        except Exception as e:
            print(f"[FNG] {e}")
        return self.fear_greed or {"value": 50, "label": "Neutral"}

    # News
    def _parse_rss(self, url):
        try:
            r = requests.get(url, timeout=6, headers={
                "User-Agent": "Mozilla/5.0 (MRTrade/6.0)"})
            if r.status_code != 200: return []
            root = ET.fromstring(r.content); items = []
            for item in root.iter("item"):
                t = (item.findtext("title") or "").strip()
                l = (item.findtext("link") or "").strip()
                p = (item.findtext("pubDate") or "").strip()
                d = (item.findtext("description") or "").strip()
                if t:
                    items.append({"title": t, "link": l, "published": p,
                                  "summary": d[:400]})
            if not items:
                ns = {"a": "http://www.w3.org/2005/Atom"}
                for e in root.findall(".//a:entry", ns):
                    te = e.find("a:title", ns); le = e.find("a:link", ns)
                    pe = e.find("a:updated", ns) or e.find("a:published", ns)
                    t = te.text.strip() if te is not None and te.text else ""
                    l = le.get("href", "") if le is not None else ""
                    p = pe.text.strip() if pe is not None and pe.text else ""
                    if t:
                        items.append({"title": t, "link": l, "published": p, "summary": ""})
            return items[:25]
        except Exception as e:
            print(f"[RSS] {url}: {e}"); return []

    def _classify(self, art):
        txt = (art["title"] + " " + art.get("summary", "")).lower()
        return [a for a, kws in ASSET_KEYWORDS.items() if any(k in txt for k in kws)]

    def ensure_news(self, force=False):
        with self._news_lock:
            if self.news_loading: return
            if not force and time.time() - self.news_fetched_at < 600: return
            self.news_loading = True
        def worker():
            try:
                arts = []
                with ThreadPoolExecutor(max_workers=4) as ex:
                    futs = [ex.submit(self._parse_feed, n, u, c)
                            for n, u, c in ALL_SOURCES]
                    for f in as_completed(futs): arts.extend(f.result())
                arts.sort(key=lambda x: x.get("published", ""), reverse=True)
                idx = {}
                for a in arts:
                    for asset in self._classify(a):
                        idx.setdefault(asset, []).append(a)
                with self._news_lock:
                    self.all_articles = arts
                    self.asset_news_index = idx
                    self.news_fetched_at = time.time()
                    self.news_loading = False
                    self.news_ready = True
                print(f"[News] {len(arts)} articles")
            except Exception as e:
                print(f"[News] {e}")
                with self._news_lock:
                    self.news_loading = False; self.news_ready = True
        threading.Thread(target=worker, daemon=True).start()

    def _parse_feed(self, n, u, c):
        a = self._parse_rss(u)
        for x in a:
            x["source"] = n; x["default_category"] = c
        return a

    def get_asset_news(self, a, limit=15):
        with self._news_lock:
            return list(self.asset_news_index.get(a, []))[:limit]
    def get_cat_news(self, c, limit=40):
        with self._news_lock:
            return [a for a in self.all_articles if a.get("default_category") == c][:limit]
    def get_top_news(self, limit=5):
        with self._news_lock:
            return self.all_articles[:limit]
    def search_assets(self, q):
        q = q.strip().lower()
        if not q: return []
        out = []
        for mn, cfg in MARKETS_CONFIG.items():
            for a in cfg["assets"]:
                if q in a.lower(): out.append((a, cfg["type"], mn))
        return out
    def search_news(self, q, limit=40):
        q = q.strip().lower()
        if not q: return []
        with self._news_lock:
            return [a for a in self.all_articles
                    if q in a["title"].lower() or q in a.get("summary", "").lower()][:limit]


# ============================================================
# BOTTOM BAR
# ============================================================

class BottomBar(MDBoxLayout):
    def __init__(self, tabs, on_tab, dark=False, **kw):
        super().__init__(**kw)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(54)
        self.padding = [dp(2)] * 4
        self.spacing = dp(2)
        self.dark = dark
        self.on_tab = on_tab
        self.buttons = {}
        self.active = None
        self._build(tabs)

    def _build(self, tabs):
        c = colors(self.dark)
        for key, icon, label in tabs:
            box = MDBoxLayout(orientation="vertical", size_hint_x=1,
                              padding=[0, dp(4), 0, dp(2)])
            ico = MDIconButton(icon=icon, theme_text_color="Custom",
                               text_color=c["faint"], pos_hint={"center_x": .5},
                               size_hint_y=0.65)
            ico.bind(on_release=lambda x, k=key: self.on_tab(k))
            lbl = MDLabel(text=label, font_style="Caption",
                          halign="center", valign="middle",
                          theme_text_color="Custom",
                          text_color=c["faint"], size_hint_y=0.35)
            box.add_widget(ico); box.add_widget(lbl)
            box._ico = ico; box._lbl = lbl
            self.buttons[key] = box
            self.add_widget(box)

    def set_active(self, key):
        self.active = key
        c = colors(self.dark)
        for k, box in self.buttons.items():
            active = (k == key)
            box._ico.text_color = c["accent"] if active else c["faint"]
            box._lbl.text_color = c["accent"] if active else c["faint"]

    def update_theme(self, dark):
        self.dark = dark
        self.md_bg_color = colors(dark)["card"]
        if self.active: self.set_active(self.active)


# ============================================================
# PRICE CARD - with big sparkline
# ============================================================

class PriceCard(MDCard):
    def __init__(self, asset, market_type, watched, on_press, on_star,
                 dark=False, **kw):
        super().__init__(**kw)
        self.asset = asset
        self.market_type = market_type
        self.dark = dark
        self.orientation = "horizontal"
        self.padding = dp(8)
        self.size_hint_y = None
        self.height = dp(66)
        self.elevation = dp(1)
        self.spacing = dp(8)
        c = colors(dark)
        self.md_bg_color = c["card"]
        self.radius = [dp(12)] * 4
        self._last_price = 0
        self._flash_state = False

        # Avatar
        self.avatar = AssetAvatar(asset, size=dp(40), font=dp(14))
        self.avatar.pos_hint = {"center_y": .5}
        self.add_widget(self.avatar)

        # Name
        left = MDBoxLayout(orientation="vertical", size_hint_x=None, width=dp(85))
        self.name_l = MDLabel(text=asset, font_style="Body1", bold=True,
                              theme_text_color="Custom", text_color=c["text"],
                              size_hint_y=1, shorten=True, valign="middle")
        left.add_widget(self.name_l)
        self.add_widget(left)

        # Sparkline - 1/4 screen
        self.spark = Sparkline(height=dp(38))
        self.spark.pos_hint = {"center_y": .5}
        self.add_widget(self.spark)

        # Price + change
        right = MDBoxLayout(orientation="vertical", size_hint_x=1,
                            padding=[dp(4), 0, 0, 0])
        self.price_l = MDLabel(text="—", font_style="Body1", bold=True,
                               halign="right", theme_text_color="Custom",
                               text_color=c["text"], size_hint_y=0.55)
        self.chg_l = MDLabel(text="", font_style="Caption", halign="right",
                             theme_text_color="Custom", text_color=c["dim"],
                             size_hint_y=0.45)
        right.add_widget(self.price_l); right.add_widget(self.chg_l)
        self.add_widget(right)

        # Star
        self.star = MDIconButton(
            icon="star" if watched else "star-outline",
            theme_text_color="Custom",
            text_color=[1, .78, .2, 1] if watched else c["faint"],
            size_hint_x=None, width=dp(30),
            pos_hint={"center_y": .5})
        self.star.bind(on_release=lambda x: on_star(asset, market_type))
        self.add_widget(self.star)

        self.bind(on_release=lambda x: on_press(asset))

    def update_price(self, price, change, source):
        c = colors(self.dark)
        if price <= 0:
            self.price_l.text = "—"
            self.price_l.text_color = c["faint"]
            self.chg_l.text = ""
            return
        old = self._last_price
        self._last_price = price
        self.price_l.text = fmt_price(price)
        if change > 0.01: col = c["up"]; txt = f"+{change:.2f}%"
        elif change < -0.01: col = c["down"]; txt = f"{change:.2f}%"
        else: col = c["neutral"]; txt = f"{change:.2f}%"
        self.price_l.text_color = col
        self.chg_l.text = txt
        self.chg_l.text_color = col
        # Flash animation on change
        if old > 0 and abs(price - old) / old > 0.001:
            flash_color = [col[0], col[1], col[2], 0.20]
            self._flash(flash_color)

    def _flash(self, color):
        orig = list(self.md_bg_color)
        self.md_bg_color = color
        Animation(md_bg_color=orig, duration=0.5, t="out_quad").start(self)

    def update_spark(self, values):
        if values and len(values) >= 2:
            self.spark.set_data(values, values[-1] >= values[0])

    def set_watched(self, w):
        c = colors(self.dark)
        self.star.icon = "star" if w else "star-outline"
        self.star.text_color = [1, .78, .2, 1] if w else c["faint"]


# ============================================================
# TICKER CARD (for Live screen)
# ============================================================

class TickerCard(MDCard):
    """Small card in Live screen ticker showing asset + sparkline"""

    def __init__(self, asset, market_type, dark=False, **kw):
        super().__init__(**kw)
        self.asset = asset
        self.market_type = market_type
        self.dark = dark
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (dp(120), dp(72))
        self.elevation = dp(1)
        self.padding = dp(6)
        self.spacing = dp(2)
        c = colors(dark)
        self.md_bg_color = c["card"]
        self.radius = [dp(10)] * 4

        top = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
        top.add_widget(MDLabel(text=asset[:10], font_style="Caption", bold=True,
                               theme_text_color="Custom", text_color=c["text"],
                               shorten=True, size_hint_x=0.7))
        self.chg_l = MDLabel(text="", font_style="Caption", halign="right",
                             theme_text_color="Custom", text_color=c["dim"],
                             size_hint_x=0.3)
        top.add_widget(self.chg_l)
        self.add_widget(top)

        self.price_l = MDLabel(text="—", font_style="Body2", bold=True,
                               theme_text_color="Custom", text_color=c["text"],
                               size_hint_y=None, height=dp(18), halign="left")
        self.add_widget(self.price_l)

        self.spark = Sparkline(width=dp(106), height=dp(26), show_fill=True)
        self.spark.size_hint = (None, None)
        self.add_widget(self.spark)

    def update_price(self, price, change):
        c = colors(self.dark)
        if price <= 0:
            self.price_l.text = "—"; self.chg_l.text = ""
            return
        self.price_l.text = fmt_price(price)
        if change > 0.01: col = c["up"]; txt = f"+{change:.1f}%"
        elif change < -0.01: col = c["down"]; txt = f"{change:.1f}%"
        else: col = c["neutral"]; txt = f"{change:.1f}%"
        self.price_l.text_color = col
        self.chg_l.text = txt; self.chg_l.text_color = col

    def update_spark(self, values):
        if values and len(values) >= 2:
            self.spark.set_data(values, values[-1] >= values[0])


# ============================================================
# NEWS ITEM
# ============================================================

class NewsItem(MDCard):
    def __init__(self, article, dark=False, **kw):
        super().__init__(**kw)
        self.article = article
        self.orientation = "vertical"
        self.padding = dp(10)
        self.size_hint_y = None
        self.height = dp(96)
        self.elevation = dp(1)
        c = colors(dark)
        self.md_bg_color = c["card"]
        self.radius = [dp(10)] * 4
        meta = MDLabel(
            text=f"{article['source']}  ·  {article.get('published', '')[:22]}",
            font_style="Caption", theme_text_color="Custom",
            text_color=c["accent"], size_hint_y=0.25)
        title = MDLabel(
            text=article["title"], font_style="Subtitle2", bold=True,
            theme_text_color="Custom", text_color=c["text"],
            size_hint_y=0.75, halign="left", valign="top")
        title.bind(size=title.setter("text_size"))
        self.add_widget(meta); self.add_widget(title)
        self.bind(on_release=lambda x: self._open())

    def _open(self):
        link = self.article.get("link", "")
        if link:
            try: webbrowser.open(link)
            except Exception as e: print(f"[Open] {e}")


# ============================================================
# CHAT BUBBLE
# ============================================================

class ChatBubble(MDBoxLayout):
    def __init__(self, msg, is_me, show_avatar=True, dark=False, **kw):
        super().__init__(**kw)
        self.msg = msg
        self.is_me = is_me
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.spacing = dp(6)
        self.padding = [dp(6), dp(1), dp(6), dp(1)]
        c = colors(dark)

        if not is_me:
            if show_avatar:
                self.add_widget(self._mk_avatar(c))
            else:
                self.add_widget(Widget(size_hint=(None, None), size=(dp(32), dp(1))))
        else:
            self.add_widget(Widget(size_hint_x=0.15))

        bubble = self._mk_bubble(c)
        self.add_widget(bubble)
        self.add_widget(Widget(size_hint_x=0.15 if not is_me else 0.05))
        Clock.schedule_once(lambda dt: self._sync(bubble), 0.05)

    def _mk_avatar(self, c):
        return AssetAvatar(self.msg.get("author", "?"), size=dp(32), font=dp(12))

    def _mk_bubble(self, c):
        bubble = MDBoxLayout(orientation="vertical")
        bubble.size_hint_x = 0.78
        bubble.size_hint_y = None
        bubble.padding = [dp(10), dp(6), dp(10), dp(6)]
        bubble.spacing = dp(2)
        with bubble.canvas.before:
            bg = c["bubble_me"] if self.is_me else c["bubble_other"]
            bubble._bgc = Color(*bg)
            bubble._bgr = RoundedRectangle(pos=bubble.pos, size=bubble.size,
                                            radius=[dp(14)])
        bubble.bind(pos=lambda *a: setattr(bubble._bgr, "pos", bubble.pos),
                    size=lambda *a: setattr(bubble._bgr, "size", bubble.size))
        if not self.is_me:
            bubble.add_widget(MDLabel(
                text=self.msg.get("author", "?"), font_style="Caption", bold=True,
                theme_text_color="Custom", text_color=c["accent"],
                size_hint_y=None, height=dp(16)))
        lbl = MDLabel(text=self.msg.get("text", ""), font_style="Body1",
                      theme_text_color="Custom", text_color=c["text"],
                      halign="left", valign="top", size_hint_y=None)
        lbl.bind(width=lambda *a: setattr(lbl, "text_size", (lbl.width, None)))
        lbl.bind(texture_size=lambda *a: setattr(lbl, "height", lbl.texture_size[1] + dp(2)))
        bubble.add_widget(lbl)
        bubble.add_widget(MDLabel(
            text=time_ago(self.msg.get("ts", 0)), font_style="Caption", halign="right",
            theme_text_color="Custom", text_color=c["dim"],
            size_hint_y=None, height=dp(14)))
        bubble.bind(minimum_height=bubble.setter("height"))
        return bubble

    def _sync(self, bubble):
        try:
            self.height = bubble.height + dp(4)
            bubble.bind(height=lambda *a: setattr(self, "height", bubble.height + dp(4)))
        except Exception:
            self.height = dp(60)


# ============================================================
# SCREENS
# ============================================================

class MainScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "main"
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")

        # Header with clock
        header = MDCard(orientation="vertical", size_hint_y=None, height=dp(105),
                        md_bg_color=c["header"], radius=[0, 0, dp(20), dp(20)],
                        elevation=0, padding=dp(12))
        tr = MDBoxLayout(orientation="horizontal", size_hint_y=0.5)
        tr.add_widget(MDLabel(text="MR TRADE", font_style="H4", bold=True,
                              theme_text_color="Custom", text_color=[1, 1, 1, 1]))
        tb = MDIconButton(
            icon="weather-night" if not app.dark else "white-balance-sunny",
            theme_text_color="Custom", text_color=[1, 1, 1, 1],
            pos_hint={"center_y": .5})
        tb.bind(on_release=lambda x: app.toggle_theme())
        tr.add_widget(tb)
        header.add_widget(tr)
        self.clock = MDLabel(font_style="Body2", halign="center", size_hint_y=0.5,
                             theme_text_color="Custom", text_color=[0.7, 0.8, 1, 1])
        header.add_widget(self.clock)

        # Fear & Greed card
        self.fng_card = MDCard(orientation="horizontal", size_hint_y=None,
                               height=dp(68), md_bg_color=c["card"],
                               radius=[dp(14)] * 4, elevation=dp(2),
                               padding=dp(12), spacing=dp(10))
        self.fng_card.add_widget(MDLabel(text="😱", font_style="H3",
                                         size_hint_x=None, width=dp(48),
                                         halign="center", valign="middle",
                                         theme_text_color="Custom",
                                         text_color=c["text"]))
        fng_info = MDBoxLayout(orientation="vertical", size_hint_x=1)
        fng_info.add_widget(MDLabel(text="Fear & Greed Index", font_style="Caption",
                                    theme_text_color="Custom", text_color=c["dim"],
                                    size_hint_y=0.4))
        self.fng_value = MDLabel(text="—", font_style="H6", bold=True,
                                 theme_text_color="Custom", text_color=c["text"],
                                 size_hint_y=0.6)
        fng_info.add_widget(self.fng_value)
        self.fng_card.add_widget(fng_info)
        self.fng_lbl = MDLabel(text="", font_style="Body2", bold=True,
                               halign="right", valign="middle",
                               theme_text_color="Custom", text_color=c["dim"],
                               size_hint_x=None, width=dp(80))
        self.fng_card.add_widget(self.fng_lbl)

        # Markets list
        markets = MDBoxLayout(orientation="vertical", spacing=dp(10),
                              padding=dp(14), size_hint_y=None)
        markets.bind(minimum_height=markets.setter("height"))
        icons = {"CRYPTO CURRENCY": "bitcoin", "FOREX MARKET": "currency-usd",
                 "STOCKS": "chart-line", "COMMODITIES": "gold",
                 "INDICES": "earth", "FUTURES": "chart-timeline-variant"}
        descs = {"CRYPTO CURRENCY": "32 assets · 24/7",
                 "FOREX MARKET": "28 pairs",
                 "STOCKS": "33 US stocks",
                 "COMMODITIES": "10 commodities",
                 "INDICES": "11 indices",
                 "FUTURES": "6 futures"}
        self._cards = []
        for name in MARKETS_CONFIG:
            card = self._mk_card(name, descs.get(name, ""), icons.get(name, "•"), c)
            self._cards.append(card)
            markets.add_widget(card)
        scroll = MDScrollView()
        scroll.add_widget(markets)
        root.add_widget(header)
        root.add_widget(self.fng_card)
        root.add_widget(scroll)
        self.add_widget(root)
        self._upd_clock()
        Clock.schedule_interval(self._upd_clock, 1)
        Clock.schedule_once(lambda dt: self._load_fng(), 0.3)

    def _load_fng(self):
        app = MDApp.get_running_app(); dm = app.data_manager
        def fetch():
            fng = dm.get_fear_greed()
            Clock.schedule_once(lambda dt: self._set_fng(fng))
        threading.Thread(target=fetch, daemon=True).start()

    def _set_fng(self, fng):
        c = colors(MDApp.get_running_app().dark)
        val = fng["value"]; lbl = fng["label"]
        self.fng_value.text = f"{val} / 100"
        self.fng_lbl.text = lbl
        # Color by value
        if val <= 25: col = [0.9, 0.25, 0.25, 1]; icon = "😱"
        elif val <= 45: col = [0.9, 0.5, 0.2, 1]; icon = "😟"
        elif val <= 55: col = [0.6, 0.6, 0.6, 1]; icon = "😐"
        elif val <= 75: col = [0.3, 0.75, 0.35, 1]; icon = "🙂"
        else: col = [0.15, 0.85, 0.3, 1]; icon = "😍"
        self.fng_value.text_color = col
        self.fng_lbl.text_color = col
        try:
            self.fng_card.children[-1].text = icon
        except Exception: pass

    def _mk_card(self, name, desc, icon, c):
        card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(72),
                      md_bg_color=c["card"], radius=[dp(14)] * 4,
                      elevation=dp(2), padding=dp(12), spacing=dp(10))
        ib = MDCard(size_hint=(None, None), size=(dp(44), dp(44)),
                    md_bg_color=c["chip"], radius=[dp(12)] * 4,
                    elevation=0, pos_hint={"center_y": .5})
        ib.add_widget(MDIconButton(icon=icon, theme_text_color="Custom",
                                   text_color=c["accent"],
                                   pos_hint={"center_x": .5, "center_y": .5}))
        tb = MDBoxLayout(orientation="vertical", size_hint_x=1)
        tb.add_widget(MDLabel(text=name, font_style="H6", bold=True,
                              theme_text_color="Custom", text_color=c["text"],
                              size_hint_y=0.55))
        tb.add_widget(MDLabel(text=desc, font_style="Caption",
                              theme_text_color="Custom", text_color=c["dim"],
                              size_hint_y=0.45))
        card.add_widget(ib); card.add_widget(tb)
        card.add_widget(MDIconButton(icon="chevron-right",
                                     theme_text_color="Custom",
                                     text_color=c["faint"],
                                     pos_hint={"center_y": .5}))
        card.bind(on_release=lambda x: MDApp.get_running_app().open_market(name))
        return card

    def _upd_clock(self, dt=None):
        if self.manager is None: return False
        try:
            self.clock.text = datetime.now().strftime("%A, %d %B %Y · %H:%M:%S")
        except Exception: return False
        return True


class MarketScreen(MDScreen):
    def __init__(self, market_name, market_type, assets, **kw):
        super().__init__(**kw)
        self.name = make_screen_key("market", market_name)
        self.market_name = market_name
        self.market_type = market_type
        self.assets = assets
        self.cards = {}
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        dm = app.data_manager
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")

        header = MDCard(orientation="horizontal", size_hint_y=None, height=dp(68),
                        md_bg_color=c["header"], radius=[0, 0, 0, 0],
                        elevation=0, padding=dp(6))
        back = MDIconButton(icon="arrow-left", theme_text_color="Custom",
                            text_color=[1, 1, 1, 1], pos_hint={"center_y": .5})
        back.bind(on_release=lambda x: app.go_back())
        tb = MDBoxLayout(orientation="vertical", size_hint_x=1)
        tb.add_widget(MDLabel(text=self.market_name, font_style="H6", bold=True,
                              theme_text_color="Custom", text_color=[1, 1, 1, 1],
                              halign="center", size_hint_y=0.55))
        self.banner = MDLabel(font_style="Caption", halign="center",
                              size_hint_y=0.45, theme_text_color="Custom")
        tb.add_widget(self.banner)
        rb = MDIconButton(icon="refresh", theme_text_color="Custom",
                          text_color=[1, 1, 1, 1], pos_hint={"center_y": .5})
        rb.bind(on_release=lambda x: self.refresh(force=True))
        header.add_widget(back); header.add_widget(tb); header.add_widget(rb)

        self._upd_banner()
        scroll = MDScrollView()
        self.list_layout = MDBoxLayout(orientation="vertical", spacing=dp(6),
                                       padding=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))

        for a in self.assets:
            card = PriceCard(a, self.market_type, dm.is_watched(a),
                             self._open, self._star, dark=app.dark)
            self.cards[a] = card
            self.list_layout.add_widget(card)
        scroll.add_widget(self.list_layout)
        root.add_widget(header); root.add_widget(scroll)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self.refresh(), 0.15)

    def _upd_banner(self):
        if is_market_open(self.market_type):
            self.banner.text = f"● OPEN · {len(self.assets)} assets"
            self.banner.text_color = [0.4, 0.95, 0.55, 1]
        else:
            self.banner.text = f"● CLOSED · {len(self.assets)} assets"
            self.banner.text_color = [1, 0.78, 0.4, 1]

    def refresh(self, force=False):
        self._upd_banner()
        app = MDApp.get_running_app(); dm = app.data_manager
        def fetch():
            # First: prices (fast)
            with ThreadPoolExecutor(max_workers=6) as ex:
                futs = {ex.submit(dm.get_price, a, self.market_type): a
                        for a in self.assets}
                for f in as_completed(futs):
                    a = futs[f]
                    try:
                        p, ch, s = f.result()
                        card = self.cards.get(a)
                        if card:
                            Clock.schedule_once(
                                lambda dt, cd=card, p=p, ch=ch, s=s:
                                cd.update_price(p, ch, s))
                    except Exception as e:
                        print(f"[Mkt] {a}: {e}")
            # Second: sparklines (slower, 30 days)
            with ThreadPoolExecutor(max_workers=3) as ex:
                futs = {ex.submit(dm.get_sparkline, a, self.market_type): a
                        for a in self.assets[:15]}  # Limit to first 15 for perf
                for f in as_completed(futs):
                    a = futs[f]
                    try:
                        vals = f.result()
                        card = self.cards.get(a)
                        if card and vals:
                            Clock.schedule_once(
                                lambda dt, cd=card, v=vals: cd.update_spark(v))
                    except Exception as e:
                        print(f"[Spark] {a}: {e}")
        threading.Thread(target=fetch, daemon=True).start()

    def _star(self, a, mt):
        try:
            app = MDApp.get_running_app(); dm = app.data_manager
            if dm.is_watched(a):
                dm.remove_watch(a)
                if a in self.cards: self.cards[a].set_watched(False)
                Snackbar(text=f"Removed {a}").open()
            else:
                dm.add_watch(a, mt)
                if a in self.cards: self.cards[a].set_watched(True)
                Snackbar(text=f"Added {a}").open()
        except Exception as e: print(f"[Star] {e}")

    def _open(self, a):
        MDApp.get_running_app().open_asset(a, self.market_type)


class AssetScreen(MDScreen):
    def __init__(self, asset, market_type, watched, **kw):
        super().__init__(**kw)
        self.name = make_screen_key("asset", asset)
        self.asset = asset
        self.market_type = market_type
        self._watched = watched
        self._poll_ev = None
        self._poll_n = 0
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")

        bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(50),
                     md_bg_color=c["header"], radius=[0, 0, 0, 0],
                     elevation=0, padding=[dp(4), 0, dp(8), 0])
        back = MDIconButton(icon="arrow-left", theme_text_color="Custom",
                            text_color=[1, 1, 1, 1], pos_hint={"center_y": .5})
        back.bind(on_release=lambda x: app.go_back())
        bar.add_widget(back)
        bar.add_widget(MDLabel(text=self.asset, font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=[1, 1, 1, 1], halign="center"))
        self.star = MDIconButton(
            icon="star" if self._watched else "star-outline",
            theme_text_color="Custom",
            text_color=[1, .78, .2, 1] if self._watched else [1, 1, 1, 1],
            pos_hint={"center_y": .5})
        self.star.bind(on_release=lambda x: self._star())
        bar.add_widget(self.star)

        # Big banner
        banner = MDCard(orientation="vertical", size_hint_y=None, height=dp(180),
                        md_bg_color=c["header"], radius=[0, 0, dp(18), dp(18)],
                        elevation=0, padding=dp(12), spacing=dp(4))
        top = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(58))
        av = AssetAvatar(self.asset, size=dp(50), font=dp(18))
        av.pos_hint = {"center_y": .5}
        top.add_widget(av)
        info = MDBoxLayout(orientation="vertical", size_hint_x=1, padding=[dp(10), 0])
        self.big_p = MDLabel(text="—", font_style="H5", bold=True,
                             theme_text_color="Custom", text_color=[1, 1, 1, 1],
                             size_hint_y=0.6)
        self.big_c = MDLabel(text="", font_style="Body2",
                             theme_text_color="Custom",
                             text_color=[0.8, 0.8, 0.8, 1], size_hint_y=0.4)
        info.add_widget(self.big_p); info.add_widget(self.big_c)
        top.add_widget(info)
        banner.add_widget(top)
        # Big sparkline (30 days)
        self.big_spark = Sparkline(width=Window.width - dp(50), height=dp(70))
        self.big_spark.size_hint = (None, None)
        banner.add_widget(self.big_spark)
        self.big_s = MDLabel(text="Loading...", font_style="Caption",
                             halign="center", size_hint_y=None, height=dp(18),
                             theme_text_color="Custom",
                             text_color=[0.65, 0.72, 0.9, 1])
        banner.add_widget(self.big_s)

        nh = MDBoxLayout(size_hint_y=None, height=dp(36),
                         padding=[dp(14), dp(4), dp(14), 0])
        nh.add_widget(MDLabel(text="Latest News", font_style="Subtitle1",
                              bold=True, theme_text_color="Custom",
                              text_color=c["text"]))
        self.news_scroll = MDScrollView()
        self.news_layout = MDBoxLayout(orientation="vertical", spacing=dp(8),
                                       padding=dp(10), size_hint_y=None)
        self.news_layout.bind(minimum_height=self.news_layout.setter("height"))
        self.news_scroll.add_widget(self.news_layout)
        root.add_widget(bar); root.add_widget(banner)
        root.add_widget(nh); root.add_widget(self.news_scroll)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self._price(), 0.1)
        Clock.schedule_once(lambda dt: self._spark(), 0.15)
        Clock.schedule_once(lambda dt: self._news(), 0.2)

    def _star(self):
        try:
            app = MDApp.get_running_app(); dm = app.data_manager
            if dm.is_watched(self.asset):
                dm.remove_watch(self.asset)
                self.star.icon = "star-outline"; self.star.text_color = [1, 1, 1, 1]
                Snackbar(text="Removed").open()
            else:
                dm.add_watch(self.asset, self.market_type)
                self.star.icon = "star"; self.star.text_color = [1, .78, .2, 1]
                Snackbar(text="Added").open()
        except Exception as e: print(f"[Star] {e}")

    def _price(self):
        dm = MDApp.get_running_app().data_manager
        def fetch():
            p, ch, s = dm.get_price(self.asset, self.market_type)
            Clock.schedule_once(lambda dt: self._upd(p, ch, s))
        threading.Thread(target=fetch, daemon=True).start()

    def _upd(self, p, ch, s):
        app = MDApp.get_running_app(); c = colors(app.dark)
        if p <= 0:
            self.big_p.text = "—"; self.big_s.text = s or "Unavailable"
            return
        self.big_p.text = fmt_price(p)
        if ch > 0.01: col = c["up"]; t = f"▲ +{ch:.2f}%"
        elif ch < -0.01: col = c["down"]; t = f"▼ {ch:.2f}%"
        else: col = c["neutral"]; t = f"{ch:.2f}%"
        self.big_c.text = t; self.big_c.text_color = col
        ot = "Live" if is_market_open(self.market_type) else "Closed"
        self.big_s.text = f"{ot} · {s} · {datetime.now().strftime('%H:%M:%S')}"

    def _spark(self):
        dm = MDApp.get_running_app().data_manager
        def fetch():
            vals = dm.get_sparkline(self.asset, self.market_type)
            if vals and len(vals) >= 2:
                Clock.schedule_once(
                    lambda dt: self.big_spark.set_data(vals, vals[-1] >= vals[0]))
        threading.Thread(target=fetch, daemon=True).start()

    def _news(self):
        dm = MDApp.get_running_app().data_manager
        dm.ensure_news()
        app = MDApp.get_running_app()
        self.news_layout.clear_widgets()
        self.news_layout.add_widget(loading_box("Loading news...", dark=app.dark))
        self._poll_n = 0
        if self._poll_ev: self._poll_ev.cancel()
        self._poll_ev = Clock.schedule_interval(self._poll, 1)

    def _poll(self, dt):
        if self.manager is None: return False
        dm = MDApp.get_running_app().data_manager
        arts = dm.get_asset_news(self.asset, limit=15)
        if arts:
            self._stop(); self._render(arts); return False
        self._poll_n += 1
        if self._poll_n > 20:
            self._stop(); self._render([]); return False
        return True

    def _stop(self):
        if self._poll_ev: self._poll_ev.cancel(); self._poll_ev = None

    def _render(self, arts):
        app = MDApp.get_running_app()
        self.news_layout.clear_widgets()
        if not arts:
            self.news_layout.add_widget(
                empty_state(f"No recent news about {self.asset}.", dark=app.dark))
            return
        for i, a in enumerate(arts):
            item = NewsItem(a, dark=app.dark)
            self.news_layout.add_widget(item)
            if i < 10: animate_in(item, delay=i * 0.03)


class NewsScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "news"
        self.current_cat = "world"
        self.tab_btns = {}
        self._poll_ev = None
        self._poll_n = 0
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")
        header = MDCard(orientation="vertical", size_hint_y=None, height=dp(128),
                        md_bg_color=c["header"], radius=[0, 0, dp(20), dp(20)],
                        elevation=0, padding=dp(10))
        tr = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34))
        tr.add_widget(MDLabel(text="World News", font_style="H5", bold=True,
                              theme_text_color="Custom", text_color=[1, 1, 1, 1]))
        rb = MDIconButton(icon="refresh", theme_text_color="Custom",
                          text_color=[1, 1, 1, 1], pos_hint={"center_y": .5})
        rb.bind(on_release=lambda x: self._load(force=True))
        tr.add_widget(rb)
        header.add_widget(tr)
        self.search = MDTextField(hint_text="Search news...", mode="round",
                                  size_hint_y=None, height=dp(38),
                                  text_color_focus=[1, 1, 1, 1],
                                  hint_text_color_normal=[0.75, 0.8, 0.9, 1],
                                  line_color_normal=[0.4, 0.5, 0.7, 1],
                                  line_color_focus=[1, 1, 1, 1],
                                  fill_color_normal=[0.15, 0.18, 0.25, 1],
                                  fill_color_focus=[0.15, 0.18, 0.25, 1])
        self.search.bind(on_text_validate=lambda x: self._search())
        header.add_widget(self.search)
        tabs = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(40), spacing=dp(6), padding=[0, dp(6), 0, 0])
        for cat, lbl in [("world", "World"), ("crypto", "Crypto"), ("finance", "Finance")]:
            b = MDFlatButton(text=f"  {lbl}  ", theme_text_color="Custom",
                             text_color=[1, 1, 1, 1],
                             md_bg_color=c["accent"] if cat == "world"
                             else [0.18, 0.20, 0.28, 1])
            b.bind(on_release=lambda x, cc=cat: self._switch(cc))
            self.tab_btns[cat] = b; tabs.add_widget(b)
        header.add_widget(tabs)
        self.news_scroll = MDScrollView()
        self.news_layout = MDBoxLayout(orientation="vertical", spacing=dp(8),
                                       padding=dp(10), size_hint_y=None)
        self.news_layout.bind(minimum_height=self.news_layout.setter("height"))
        self.news_scroll.add_widget(self.news_layout)
        root.add_widget(header); root.add_widget(self.news_scroll)
        self.add_widget(root)
        Clock.schedule_once(lambda dt: self._load(), 0.1)

    def on_enter(self):
        if not self.news_layout.children: self._load()

    def _switch(self, cat):
        self.current_cat = cat; self.search.text = ""
        c = colors(MDApp.get_running_app().dark)
        for k, b in self.tab_btns.items():
            b.md_bg_color = c["accent"] if k == cat else [0.18, 0.20, 0.28, 1]
        self._load()

    def _search(self):
        q = self.search.text.strip()
        if not q: self._load(); return
        app = MDApp.get_running_app()
        self._render(app.data_manager.search_news(q, limit=50))

    def _load(self, force=False):
        app = MDApp.get_running_app(); dm = app.data_manager
        dm.ensure_news(force=force)
        self.news_layout.clear_widgets()
        self.news_layout.add_widget(loading_box("Loading news...", dark=app.dark))
        self._poll_n = 0
        if self._poll_ev: self._poll_ev.cancel()
        self._poll_ev = Clock.schedule_interval(self._poll, 1)

    def _poll(self, dt):
        if self.manager is None: return False
        dm = MDApp.get_running_app().data_manager
        arts = dm.get_cat_news(self.current_cat, limit=40)
        if arts:
            self._stop(); self._render(arts); return False
        self._poll_n += 1
        if self._poll_n > 20:
            self._stop(); self._render([]); return False
        return True

    def _stop(self):
        if self._poll_ev: self._poll_ev.cancel(); self._poll_ev = None

    def _render(self, arts):
        app = MDApp.get_running_app()
        self.news_layout.clear_widgets()
        if not arts:
            self.news_layout.add_widget(
                empty_state("No news found.\nTry another search.", dark=app.dark))
            return
        for i, a in enumerate(arts):
            item = NewsItem(a, dark=app.dark)
            self.news_layout.add_widget(item)
            if i < 12: animate_in(item, delay=i * 0.02)


class LiveScreen(MDScreen):
    """Live screen: ticker at top + chat below"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "live"
        self._shown_ids = set()
        self.ticker_cards = {}
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["chat_bg"]
        root = MDBoxLayout(orientation="vertical")

        # Header
        header = MDCard(orientation="horizontal", size_hint_y=None, height=dp(52),
                        md_bg_color=c["header"], radius=[0, 0, dp(14), dp(14)],
                        elevation=0, padding=dp(8), spacing=dp(8))
        header.add_widget(MDLabel(text="Live", font_style="H5", bold=True,
                                  theme_text_color="Custom",
                                  text_color=[1, 1, 1, 1], size_hint_x=0.25))
        self.name_field = TextInput(
            hint_text="Your name",
            text=app.data_manager.get_uname(), multiline=False,
            size_hint_x=0.75, size_hint_y=None, height=dp(34),
            background_color=(1, 1, 1, 0.15),
            foreground_color=[1, 1, 1, 1], cursor_color=[1, 1, 1, 1],
            hint_text_color=[0.75, 0.8, 0.9, 1],
            padding=[dp(10), dp(7), dp(10), dp(7)], font_size=dp(14))
        self.name_field.bind(on_text_validate=lambda x: self._save_name())
        header.add_widget(self.name_field)

        # Ticker bar (horizontal scroll)
        ticker_label = MDBoxLayout(size_hint_y=None, height=dp(24),
                                   padding=[dp(10), dp(4), dp(10), 0])
        ticker_label.add_widget(MDLabel(
            text="📈 Live Market Pulse", font_style="Caption", bold=True,
            theme_text_color="Custom", text_color=c["accent"]))
        self.ticker_scroll = MDScrollView(size_hint_y=None, height=dp(78),
                                           do_scroll_x=True, do_scroll_y=False)
        self.ticker_layout = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                          padding=dp(8), size_hint_x=None,
                                          size_hint_y=1)
        self.ticker_layout.bind(minimum_width=self.ticker_layout.setter("width"))
        self.ticker_scroll.add_widget(self.ticker_layout)

        # Chat scroll
        self.scroll = MDScrollView()
        self.chat_layout = MDBoxLayout(orientation="vertical", spacing=dp(2),
                                       padding=[dp(4), dp(8), dp(4), dp(8)],
                                       size_hint_y=None)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))
        self.scroll.add_widget(self.chat_layout)

        # Input bar
        input_bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(52),
                           md_bg_color=c["card"], radius=[dp(26)] * 4,
                           elevation=dp(2), padding=[dp(8), dp(4), dp(4), dp(4)],
                           spacing=dp(4))
        self.msg_field = TextInput(
            hint_text="Type a message...", multiline=False,
            size_hint_x=1, size_hint_y=None, height=dp(42),
            background_color=(0, 0, 0, 0),
            foreground_color=c["text"], cursor_color=c["accent"],
            hint_text_color=c["dim"],
            padding=[dp(12), dp(12), dp(12), dp(10)], font_size=dp(15))
        self.msg_field.bind(on_text_validate=lambda x: self._send())
        input_bar.add_widget(self.msg_field)
        send_btn = MDIconButton(
            icon="send", theme_text_color="Custom",
            text_color=[1, 1, 1, 1], md_bg_color=c["accent"],
            pos_hint={"center_y": .5},
            size_hint=(None, None), size=(dp(42), dp(42)))
        send_btn.bind(on_release=lambda x: self._send())
        input_bar.add_widget(send_btn)

        root.add_widget(header)
        root.add_widget(ticker_label)
        root.add_widget(self.ticker_scroll)
        root.add_widget(self.scroll)
        root.add_widget(input_bar)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self._load_ticker(), 0.1)
        Clock.schedule_once(lambda dt: self.refresh(), 0.05)

    def _load_ticker(self):
        """Load ticker cards if not yet loaded"""
        if self.ticker_cards: 
            self._refresh_ticker()
            return
        app = MDApp.get_running_app()
        for asset, mt in TICKER_ASSETS:
            card = TickerCard(asset, mt, dark=app.dark)
            self.ticker_cards[asset] = card
            self.ticker_layout.add_widget(card)
        self._refresh_ticker()

    def _refresh_ticker(self):
        app = MDApp.get_running_app(); dm = app.data_manager
        def fetch():
            with ThreadPoolExecutor(max_workers=6) as ex:
                futs = {}
                for asset, mt in TICKER_ASSETS:
                    futs[ex.submit(dm.get_price, asset, mt)] = (asset, mt)
                for f in as_completed(futs):
                    asset, mt = futs[f]
                    try:
                        p, ch, s = f.result()
                        card = self.ticker_cards.get(asset)
                        if card:
                            Clock.schedule_once(
                                lambda dt, cd=card, p=p, ch=ch:
                                cd.update_price(p, ch))
                    except Exception as e:
                        print(f"[Ticker] {asset}: {e}")
            # Sparklines in parallel with limited workers
            with ThreadPoolExecutor(max_workers=3) as ex:
                futs = {}
                for asset, mt in TICKER_ASSETS:
                    futs[ex.submit(dm.get_sparkline, asset, mt)] = asset
                for f in as_completed(futs):
                    asset = futs[f]
                    try:
                        vals = f.result()
                        card = self.ticker_cards.get(asset)
                        if card and vals:
                            Clock.schedule_once(
                                lambda dt, cd=card, v=vals: cd.update_spark(v))
                    except Exception as e:
                        pass
        threading.Thread(target=fetch, daemon=True).start()

    def _save_name(self):
        MDApp.get_running_app().data_manager.set_uname(self.name_field.text.strip())

    def refresh(self):
        try:
            app = MDApp.get_running_app(); dm = app.data_manager
            msgs = dm.get_messages(limit=500)
            my_uid = dm.get_uid()
            if not msgs and not self.chat_layout.children:
                self.chat_layout.add_widget(empty_state(
                    "No messages yet.\nSay hello!", dark=app.dark))
                return
            if msgs:
                for child in list(self.chat_layout.children):
                    if isinstance(child, MDBoxLayout) and len(child.children) == 1 \
                       and isinstance(child.children[0], MDLabel) \
                       and "No messages" in getattr(child.children[0], 'text', ''):
                        self.chat_layout.remove_widget(child)
                        break
            prev_author = None; prev_ts = 0
            if self.chat_layout.children:
                last = self.chat_layout.children[0]
                if isinstance(last, ChatBubble):
                    prev_author = last.msg.get("author")
                    prev_ts = last.msg.get("ts", 0)
            appended = False
            for m in msgs:
                if m["id"] in self._shown_ids: continue
                same = (m.get("author") == prev_author and
                        m.get("ts", 0) - prev_ts < 300)
                bubble = ChatBubble(m, is_me=(m.get("uid") == my_uid),
                                    show_avatar=not same, dark=app.dark)
                self.chat_layout.add_widget(bubble)
                self._shown_ids.add(m["id"])
                prev_author = m.get("author"); prev_ts = m.get("ts", 0)
                appended = True
            if appended:
                Clock.schedule_once(
                    lambda dt: setattr(self.scroll, "scroll_y", 0), 0.1)
        except Exception as e:
            print(f"[Chat] {e}")

    def _send(self):
        try:
            txt = self.msg_field.text.strip()
            if not txt: return
            app = MDApp.get_running_app()
            name = self.name_field.text.strip() or "Anonymous"
            app.data_manager.set_uname(name)
            app.data_manager.add_message(name, txt)
            self.msg_field.text = ""
            self.refresh()
        except Exception as e: print(f"[Send] {e}")


class SearchScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "search"
        self._debounce = None
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")
        header = MDCard(orientation="vertical", size_hint_y=None, height=dp(100),
                        md_bg_color=c["header"], radius=[0, 0, dp(18), dp(18)],
                        elevation=0, padding=dp(10))
        header.add_widget(MDLabel(text="Search", font_style="H5", bold=True,
                                  theme_text_color="Custom",
                                  text_color=[1, 1, 1, 1],
                                  size_hint_y=None, height=dp(32)))
        self.field = MDTextField(
            hint_text="Bitcoin, Tesla, Gold...", mode="round",
            size_hint_y=None, height=dp(42),
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_normal=[0.75, 0.8, 0.9, 1],
            line_color_normal=[0.4, 0.5, 0.7, 1],
            line_color_focus=[1, 1, 1, 1],
            fill_color_normal=[0.15, 0.18, 0.25, 1],
            fill_color_focus=[0.15, 0.18, 0.25, 1])
        self.field.bind(text=self._on_text)
        header.add_widget(self.field)
        self.results = MDBoxLayout(orientation="vertical", spacing=dp(6),
                                   padding=dp(8), size_hint_y=None)
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll = MDScrollView(); scroll.add_widget(self.results)
        root.add_widget(header); root.add_widget(scroll)
        self.add_widget(root)

    def _on_text(self, *a):
        if self._debounce: self._debounce.cancel()
        self._debounce = Clock.schedule_once(lambda dt: self._search(), 0.35)

    def _search(self):
        app = MDApp.get_running_app(); dm = app.data_manager
        q = self.field.text.strip()
        self.results.clear_widgets()
        if not q:
            self.results.add_widget(empty_state("Start typing to search.", dark=app.dark))
            return
        res = dm.search_assets(q)
        if not res:
            self.results.add_widget(empty_state(f"No results for '{q}'", dark=app.dark))
            return
        for a, mt, mn in res[:40]:
            card = PriceCard(a, mt, dm.is_watched(a),
                             lambda x, t=mt: app.open_asset(x, t),
                             self._star, dark=app.dark)
            self.results.add_widget(card)
            threading.Thread(target=self._fetch, args=(card, a, mt),
                             daemon=True).start()

    def _star(self, a, mt):
        app = MDApp.get_running_app(); dm = app.data_manager
        if dm.is_watched(a): dm.remove_watch(a)
        else: dm.add_watch(a, mt)
        self._search()

    def _fetch(self, card, a, mt):
        app = MDApp.get_running_app()
        p, ch, s = app.data_manager.get_price(a, mt)
        Clock.schedule_once(lambda dt: card.update_price(p, ch, s))
        vals = app.data_manager.get_sparkline(a, mt)
        if vals:
            Clock.schedule_once(lambda dt: card.update_spark(vals))


class WatchlistScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "watchlist"
        self._last_keys = None
        self._cards = {}
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical")
        header = MDCard(orientation="horizontal", size_hint_y=None, height=dp(56),
                        md_bg_color=c["header"], radius=[0, 0, dp(18), dp(18)],
                        elevation=0, padding=dp(10))
        header.add_widget(MDLabel(text="Watchlist", font_style="H5", bold=True,
                                  theme_text_color="Custom",
                                  text_color=[1, 1, 1, 1]))
        rb = MDIconButton(icon="refresh", theme_text_color="Custom",
                          text_color=[1, 1, 1, 1], pos_hint={"center_y": .5})
        rb.bind(on_release=lambda x: self.refresh(force=True))
        header.add_widget(rb)
        self.scroll = MDScrollView()
        self.list_layout = MDBoxLayout(orientation="vertical", spacing=dp(6),
                                       padding=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        root.add_widget(header); root.add_widget(self.scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh(), 0.05)

    def refresh(self, force=False):
        try:
            app = MDApp.get_running_app(); dm = app.data_manager
            wl = dm.get_watchlist()
            wl_keys = tuple((e["asset"], e["type"]) for e in wl)
            if not force and wl_keys == self._last_keys and self._cards:
                for a, card in self._cards.items():
                    threading.Thread(target=self._fetch, args=(card, a),
                                     daemon=True).start()
                return
            self._last_keys = wl_keys
            self.list_layout.clear_widgets()
            self._cards = {}
            if not wl:
                self.list_layout.add_widget(empty_state(
                    "Your watchlist is empty.\nTap ⭐ on any asset.", dark=app.dark))
                return
            for e in wl:
                card = PriceCard(e["asset"], e["type"], True,
                                 lambda a, t=e["type"]: app.open_asset(a, t),
                                 self._star, dark=app.dark)
                self.list_layout.add_widget(card)
                self._cards[e["asset"]] = card
                threading.Thread(
                    target=self._fetch, args=(card, e["asset"], e["type"]),
                    daemon=True).start()
        except Exception as e:
            print(f"[WL] {e}")

    def _star(self, a, mt):
        MDApp.get_running_app().data_manager.remove_watch(a)
        Snackbar(text=f"Removed {a}").open()
        self.refresh(force=True)

    def _fetch(self, card, a, mt=None):
        try:
            app = MDApp.get_running_app()
            if mt is None:
                for e in app.data_manager.get_watchlist():
                    if e["asset"] == a: mt = e["type"]; break
            if mt is None: return
            p, ch, s = app.data_manager.get_price(a, mt)
            Clock.schedule_once(lambda dt: card.update_price(p, ch, s))
            vals = app.data_manager.get_sparkline(a, mt)
            if vals:
                Clock.schedule_once(lambda dt: card.update_spark(vals))
        except Exception as e:
            print(f"[WL fetch] {e}")


class SettingsScreen(MDScreen):
    """MINIMAL: only Dark Mode"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = "settings"
        self._build()

    def _build(self):
        app = MDApp.get_running_app()
        c = colors(app.dark)
        self.md_bg_color = c["bg"]
        root = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(14))
        header = MDCard(orientation="horizontal", size_hint_y=None, height=dp(56),
                        md_bg_color=c["header"], radius=[0, 0, dp(18), dp(18)],
                        elevation=0, padding=dp(10))
        header.add_widget(MDLabel(text="Settings", font_style="H5", bold=True,
                                  theme_text_color="Custom",
                                  text_color=[1, 1, 1, 1]))
        root.add_widget(header)
        # ONLY: Dark Mode
        row = MDCard(orientation="horizontal", size_hint_y=None, height=dp(60),
                     md_bg_color=c["card"], radius=[dp(12)] * 4,
                     elevation=dp(1), padding=dp(14))
        row.add_widget(MDLabel(text="🌙  Dark Mode", font_style="Subtitle1",
                               theme_text_color="Custom",
                               text_color=c["text"], size_hint_x=0.7))
        sw = MDSwitch(pos_hint={"center_y": .5})
        sw.active = app.dark
        sw.bind(active=lambda x, v: app.set_dark(v))
        row.add_widget(sw)
        root.add_widget(row)
        root.add_widget(Widget())
        self.add_widget(root)


# ============================================================
# APP
# ============================================================

class MRTradeApp(MDApp):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.screen_history = []
        self.back_time = 0
        self.back_count = 0
        self._market_screens = {}
        self._asset_screens = {}
        self._current_market_key = None
        self.bottom_bar = None
        self._booted = False

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        base = self.user_data_dir
        self.store = JsonStore(os.path.join(base, "mrtrade.json"))
        self.chat_store = JsonStore(os.path.join(base, "chat.json"))
        self.data_manager = DataManager(self.store, self.chat_store)
        self.dark = self.data_manager.get_dark()
        self.theme_cls.theme_style = "Dark" if self.dark else "Light"

        self.main_screen = MainScreen()
        self.watchlist_screen = WatchlistScreen()
        self.live_screen = LiveScreen()
        self.news_screen = NewsScreen()
        self.search_screen = SearchScreen()
        self.settings_screen = SettingsScreen()

        self.sm = MDScreenManager()
        self.sm.transition.duration = 0
        for s in (self.main_screen, self.watchlist_screen, self.live_screen,
                  self.news_screen, self.search_screen, self.settings_screen):
            self.sm.add_widget(s)
        self.sm.current = "main"

        tabs = [
            ("main", "home", "Home"),
            ("watchlist", "star", "Watch"),
            ("live", "forum", "Live"),
            ("news", "newspaper", "News"),
            ("search", "magnify", "Search"),
            ("settings", "cog", "Settings"),
        ]
        self.bottom_bar = BottomBar(tabs, self._on_tab, dark=self.dark)
        self.bottom_bar.set_active("main")

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(self.sm)
        root.add_widget(self.bottom_bar)

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self._on_back)
        Clock.schedule_interval(self._refresh_current_market, 15)

        if not self._booted:
            self._booted = True
            Clock.schedule_once(lambda dt: self.data_manager.ensure_news(), 0.5)
        return root

    def _on_tab(self, key):
        if key in ("main", "watchlist", "live", "news", "search", "settings"):
            self.sm.transition.duration = 0
            self.sm.current = key
            self.bottom_bar.set_active(key)
            self._current_market_key = None

    def _push(self):
        self.screen_history.append(self.sm.current)

    def go_back(self):
        if self.screen_history:
            p = self.screen_history.pop()
            self.sm.transition.duration = 0
            self.sm.current = p
            self._current_market_key = p if p.startswith("market_") else None
            if p.startswith("market_"):
                Clock.schedule_once(lambda dt: self._refresh_current_market(), 0.05)
            if p in ("main", "watchlist", "live", "news", "search", "settings"):
                self.bottom_bar.set_active(p)
            else:
                self.bottom_bar.set_active("")
        else:
            self.sm.current = "main"
            self.bottom_bar.set_active("main")
            self._current_market_key = None

    def open_market(self, name):
        cfg = MARKETS_CONFIG.get(name)
        if not cfg:
            Snackbar(text=f"Unknown: {name}").open()
            return
        key = make_screen_key("market", name)
        if key not in self._market_screens:
            try:
                sc = MarketScreen(name, cfg["type"], cfg["assets"])
                self._market_screens[key] = sc
                self.sm.add_widget(sc)
            except Exception as e:
                print(f"[open_market] {e}")
                Snackbar(text=f"Error: {e}").open()
                return
        self._push()
        self.sm.transition.duration = 0
        self.sm.current = key
        self.bottom_bar.set_active("")
        self._current_market_key = key
        Clock.schedule_once(lambda dt: self._refresh_current_market(), 0.05)

    def open_asset(self, asset, mt):
        key = make_screen_key("asset", asset)
        if key not in self._asset_screens:
            try:
                watched = self.data_manager.is_watched(asset)
                sc = AssetScreen(asset, mt, watched)
                self._asset_screens[key] = sc
                self.sm.add_widget(sc)
            except Exception as e:
                print(f"[open_asset] {e}")
                Snackbar(text=f"Error: {e}").open()
                return
        self._push()
        self.sm.transition.duration = 0
        self.sm.current = key
        self.bottom_bar.set_active("")
        self._current_market_key = None

    def _refresh_current_market(self, dt=None):
        try:
            if self._current_market_key and \
               self._current_market_key in self._market_screens:
                self._market_screens[self._current_market_key].refresh()
        except Exception as e:
            print(f"[Auto] {e}")

    def toggle_theme(self):
        self.set_dark(not self.dark)

    def set_dark(self, v):
        self.dark = v
        self.data_manager.set_dark(v)
        Clock.schedule_once(lambda dt: self._rebuild_theme(), 0.05)

    def _rebuild_theme(self):
        try:
            cur = self.sm.current
            self._market_screens = {}
            self._asset_screens = {}
            self._current_market_key = None
            self.screen_history = []
            for sid in list(self.sm.screen_names):
                try: self.sm.remove_widget(self.sm.get_screen(sid))
                except Exception: pass
            self.main_screen = MainScreen()
            self.watchlist_screen = WatchlistScreen()
            self.live_screen = LiveScreen()
            self.news_screen = NewsScreen()
            self.search_screen = SearchScreen()
            self.settings_screen = SettingsScreen()
            for s in (self.main_screen, self.watchlist_screen, self.live_screen,
                      self.news_screen, self.search_screen, self.settings_screen):
                self.sm.add_widget(s)
            self.sm.current = cur if cur in self.sm.screen_names else "main"
            self.bottom_bar.update_theme(self.dark)
            self.bottom_bar.set_active(
                cur if cur in ("main", "watchlist", "live", "news",
                               "search", "settings") else "")
            self.theme_cls.theme_style = "Dark" if self.dark else "Light"
        except Exception as e:
            print(f"[Rebuild] {e}")

    def _on_back(self, window, key, *a):
        if key != 27: return False
        now = time.time()
        if self.sm.current == "main":
            if now - self.back_time < 2: self.back_count += 1
            else: self.back_count = 1
            self.back_time = now
            if self.back_count >= 2: self.stop()
            else: Snackbar(text="Press back again to exit").open()
            return True
        self.go_back()
        return True


if __name__ == "__main__":
    print("=" * 50)
    print("MR TRADE v6.0 - Legendary Edition")
    print("=" * 50)
    print(f"Total assets: {sum(len(c['assets']) for c in MARKETS_CONFIG.values())}")
    print("=" * 50)
    try:
        MRTradeApp().run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFATAL: {e}")