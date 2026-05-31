"""Test remote sync — Discord / shop / GitHub links & update alerts."""
import json
import os
import sys
import tempfile

VOID = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if VOID not in sys.path:
    sys.path.insert(0, VOID)

from lib import constants as C
from lib.config import get_settings
from lib import remote as R


def reset_remote_state():
    """Reload remote module state from disk."""
    R._manifest = {}
    R._loaded = False
    if os.path.isfile(R.CACHE_PATH):
        os.remove(R.CACHE_PATH)


def test_fetch_github():
    print("1. Fetch GitHub manifest...")
    data = R._fetch_url(R.REMOTE_URL, timeout=10)
    assert "config_rev" in data, "missing config_rev"
    assert "links" in data, "missing links"
    assert data["links"].get("discord"), "missing discord link"
    print(f"   OK rev={data['config_rev']} discord={data['links']['discord']}")
    return True


def test_sync_remote():
    print("2. sync() from GitHub...")
    reset_remote_state()
    ok, source = R.sync(force=True)
    assert ok and source == "remote", f"expected remote, got {source}"
    m = R.get_manifest()
    assert m.get("_source") == "remote"
    assert C.DISCORD == m["links"]["discord"]
    assert C.SHOP == m["links"]["shop"]
    assert C.GITHUB == m["links"]["github"]
    print(f"   OK source={source} DISCORD={C.DISCORD}")
    return True


def test_link_override():
    print("3. Link override via test manifest...")
    reset_remote_state()
    test_manifest = {
        "config_rev": "99",
        "latest_version": C.VERSION,
        "links": {
            "discord": "https://discord.gg/test-void-sync",
            "github": "https://github.com/V0id-v2/Void-Tools-v2.0",
            "shop": "https://void-tools.mysellauth.com/",
        },
        "announcement": {"title_en": "TEST", "body_en": "sync ok"},
        "changelog": "TEST CHANGELOG",
    }
    backup = None
    if os.path.isfile(R.LOCAL_MANIFEST):
        fd, backup = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(R.LOCAL_MANIFEST, encoding="utf-8") as src, open(backup, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    try:
        with open(R.LOCAL_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(test_manifest, f, indent=2, ensure_ascii=False)
        reset_remote_state()
        ok, source = R.sync(force=True)
        assert ok, "sync failed"
        assert source == "bundled", f"expected bundled override, got {source}"
        assert C.DISCORD == "https://discord.gg/test-void-sync"
        assert C.CHANGELOG == "TEST CHANGELOG"
        s = get_settings()
        s.set("last_seen_config_rev", "0")
        s.save()
        assert R.has_pending_update(), "should detect new config_rev"
        R.mark_seen()
        assert not R.has_pending_update(), "should be seen after mark_seen"
        print("   OK overrides + pending update flow")
    finally:
        if backup:
            with open(backup, encoding="utf-8") as src, open(R.LOCAL_MANIFEST, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            os.remove(backup)
        reset_remote_state()
        R.sync(force=True)
    return True


def test_version_badge():
    print("4. Version update badge...")
    reset_remote_state()
    R._manifest = {
        "config_rev": "1",
        "latest_version": "9.9.9",
        "links": {},
    }
    R._loaded = True
    assert R.version_update_available(), "9.9.9 should be newer than 2.0.0"
    assert R.status_badge() == "MAJ"
    R._manifest["latest_version"] = C.VERSION
    assert not R.version_update_available()
    print("   OK MAJ badge when latest > local")
    reset_remote_state()
    R.sync(force=True)
    return True


def test_cache_fallback():
    print("5. Cache fallback...")
    reset_remote_state()
    real_url = R.REMOTE_URL
    R.sync(force=True)
    assert os.path.isfile(R.CACHE_PATH), "cache not written"
    R.REMOTE_URL = "https://invalid.example.com/manifest.json"
    R._loaded = False
    ok, source = R.sync(force=True)
    assert source == "cache", f"expected cache fallback, got {source}"
    R.REMOTE_URL = real_url
    print(f"   OK fallback source={source}")
    return True


def main():
    # restore real URL after cache test
    global_remote = os.environ.get(
        "VOID_REMOTE_URL",
        "https://raw.githubusercontent.com/V0id-v2/Void-Tools-v2.0/main/Void/config/remote-manifest.json",
    )
    R.REMOTE_URL = global_remote
    tests = [
        test_fetch_github,
        test_sync_remote,
        test_link_override,
        test_version_badge,
        test_cache_fallback,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            failed.append((t.__name__, str(e)))
            print(f"   FAIL: {e}")

    R.REMOTE_URL = global_remote
    reset_remote_state()
    R.sync(force=True)

    print()
    if failed:
        print(f"FAILED {len(failed)}/{len(tests)}")
        for name, msg in failed:
            print(f"  - {name}: {msg}")
        return 1
    print(f"ALL {len(tests)} TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
