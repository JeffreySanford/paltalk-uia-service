"""Identify the current speaker displayed in the room UI.
"""
from typing import Optional
from app.probe import probe_window


def get_speaker_now(title_substr: str) -> Optional[str]:
    res = probe_window(title_substr, activate=True)
    # Heuristic: search for controls in the 'Talking Now' area: small vertical range near the top-center
    candidates = []
    for c in res.get("controls", []):
        name = (c.get("name") or "").strip()
        rect = c.get("rect") or {}
        top = rect.get("top", 0)
        left = rect.get("left", 0)
        # Based on observed layout, talking now area is around top ~120-140 and left in left chat column
        if name and 100 < top < 160 and left < -1500 and len(name) > 1:
            candidates.append((top, name))
    if not candidates:
        # fallback: use speaker_candidates from probe
        sc = res.get("speaker_candidates", [])
        if sc:
            return sc[0].get("name")
        return None
    # pick the topmost candidate
    candidates.sort()
    return candidates[0][1]


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("title")
    args = p.parse_args()
    speaker = get_speaker_now(args.title)
    print(speaker or "(unknown)")


if __name__ == "__main__":
    main()
