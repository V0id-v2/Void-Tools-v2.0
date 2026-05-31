"""Shared HTTP helpers for password-reset requests."""
import re
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

OK_CODES = {200, 201, 202, 204, 302, 303, 307, 409, 429}


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    retry = Retry(total=1, backoff_factor=0.15, status_forcelist=(502, 503, 504))
    adapter = HTTPAdapter(max_retries=retry, pool_connections=30, pool_maxsize=30)
    s.mount("https://", adapter)
    return s


def _ok(r):
    if r.status_code in OK_CODES:
        return True
    if r.status_code in (404, 405, 500, 502, 503):
        return False
    if r.status_code == 403:
        return "captcha" not in r.text.lower()[:800]
    ct = (r.headers.get("content-type") or "").lower()
    if "json" in ct:
        try:
            j = r.json()
            if isinstance(j, dict):
                if j.get("success") is True or j.get("ok") is True or j.get("result") == "success":
                    return True
                err = str(j.get("error", j.get("message", ""))).lower()
                if "captcha" in err or "rate" in err:
                    return r.status_code == 429
        except Exception:
            pass
        return r.status_code < 500
    text = r.text.lower()[:1200]
    if any(x in text for x in ("captcha", "recaptcha", "hcaptcha", "robot")):
        return False
    if r.status_code in (400, 401, 422) and any(
        x in text for x in ("sent", "email", "inbox", "lien", "link", "check", "message")
    ):
        return True
    return r.status_code < 500 and r.status_code not in (404, 405)


def hit(session, name, stats, method, url, **kwargs):
    try:
        fn = getattr(session, method)
        r = fn(url, timeout=16, allow_redirects=True, **kwargs)
        detail = str(r.status_code)
        if not _ok(r) and len(r.text) < 120:
            detail += f" · {r.text[:60]}"
        stats.hit(name, _ok(r), detail)
        return r
    except Exception as e:
        stats.hit(name, False, str(e)[:40])
        return None


def post_json(session, name, stats, url, payload, headers=None, referer=None):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if referer:
        h["Referer"] = referer
        p = urlparse(referer)
        if p.scheme and p.netloc:
            h["Origin"] = f"{p.scheme}://{p.netloc}"
    if headers:
        h.update(headers)
    return hit(session, name, stats, "post", url, json=payload, headers=h)


def post_form(session, name, stats, url, data, referer=None, headers=None):
    h = {}
    if referer:
        h["Referer"] = referer
    if headers:
        h.update(headers)
    return hit(session, name, stats, "post", url, data=data, headers=h or None)


def hidden_fields(html, hidden_only=True):
    fields = {}
    for tag in re.findall(r"<input[^>]+>", html, re.I):
        if hidden_only and not re.search(r'type=["\']hidden["\']', tag, re.I):
            continue
        n = re.search(r'name=["\']([^"\']+)["\']', tag, re.I)
        v = re.search(r'value=["\']([^"\']*)["\']', tag, re.I)
        if n:
            fields[n.group(1)] = v.group(1) if v else ""
    return fields


def scrape_form_post(session, name, stats, page_url, email, email_fields=None, referer=None):
    email_fields = email_fields or ("email",)
    try:
        r = session.get(page_url, timeout=16)
        if r.status_code >= 400:
            stats.hit(name, False, str(r.status_code))
            return None
        html = r.text
        action_m = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', html, re.I)
        action = urljoin(page_url, action_m.group(1)) if action_m else page_url
        data = hidden_fields(html)
        for field in email_fields:
            data[field] = email
        return post_form(session, name, stats, action, data, referer=referer or page_url)
    except Exception as e:
        stats.hit(name, False, str(e)[:40])
        return None


def csrf_form(session, name, stats, page_url, post_url, email, field="email", extra=None):
    try:
        r = session.get(page_url, timeout=16)
        tok = re.search(r'name="authenticity_token"\s+value="([^"]+)"', r.text)
        tok = tok or re.search(r'name="_token"\s+value="([^"]+)"', r.text)
        data = hidden_fields(r.text)
        data[field] = email
        if tok:
            data["authenticity_token"] = tok.group(1)
        if extra:
            data.update(extra)
        return post_form(session, name, stats, post_url, data, referer=page_url)
    except Exception as e:
        stats.hit(name, False, str(e)[:40])
        return None
