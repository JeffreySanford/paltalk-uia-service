"""Extract the list of chat room participants (chatter list).
"""
from typing import List
from app.probe import probe_window


def get_chatter_list(title_substr: str) -> List[str]:
    res = probe_window(title_substr, activate=True)
    names = []
    for c in res.get("controls", []):
        cls = c.get("class_name", "")
        name = (c.get("name") or "").strip()
        aid = (c.get("automation_id") or "").lower()
        # Heuristics: member list widgets often contain 'member_list' or 'UsernameWidget'
        if name and ("usernamewidget" in cls.lower() or "member_list" in aid or cls.lower().endswith("qlabel") or cls.lower().endswith("plaintext")):
            # Exclude common UI labels or button texts (e.g., BaseButton184, Join Queue to Talk)
            lname = name.lower()
            excluded_substrings = ("button", "join queue", "join_queue", "basebutton")
            if any(sub in lname for sub in excluded_substrings):
                continue
            # Exclude banner-like lines (contain digits or banner keywords)
            banner_substrings = ("second", "mic", "max", "advert", "advertisement")
            if any(sub in lname for sub in banner_substrings):
                continue
            if any(ch.isdigit() for ch in name):
                # numeric banners (e.g., '76 second ...') or numeric labels
                continue
            # Exclude overly long text that is unlikely to be a username
            if len(name) > 40:
                continue
            names.append(name)
    # dedupe preserving order
    seen = set()
    out = []
    for n in names:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def main():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("title")
    p.add_argument("--out", default="chatter_list.txt")
    args = p.parse_args()
    names = get_chatter_list(args.title)
    with open(args.out, "w", encoding="utf-8") as f:
        for n in names:
            f.write(n + "\n")
    print(f"Wrote {len(names)} chatters to {args.out}")


if __name__ == "__main__":
    main()
