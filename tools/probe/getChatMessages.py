"""Extract chat messages from the left chat area of a room window.
Provides a simple CLI to write messages to a file `chat_messages.txt`.
"""
from typing import List, Dict
from app.probe import probe_window
import json


def get_chat_messages(title_substr: str) -> List[Dict]:
    res = probe_window(title_substr, activate=True)
    controls = [c for c in res.get("controls", []) if (c.get("rect") or {}).get("left", 0) < -1000]
    # sort by top coordinate
    def top_coord(c):
        r = c.get("rect") or {}
        return (r.get("top", 0), r.get("left", 0))

    controls_sorted = sorted(controls, key=top_coord)

    msgs = []

    import re
    uname_ts_re = re.compile(r"^(?P<username>[^,\n]+),\s*\[(?P<hour>\d{1,2}):(?P<min>\d{2})\]$")

    i = 0
    while i < len(controls_sorted):
        c = controls_sorted[i]
        name = (c.get("name") or "").strip()
        cls = c.get("class_name", "")
        ctrl_type = c.get("control_type")
        top = (c.get("rect") or {}).get("top", 0)

        # Case A: username and timestamp in one control
        m = uname_ts_re.match(name)
        if m:
            username = m.group("username").strip()
            timestamp = f"{m.group('hour')}:{m.group('min')}"
            # find next text control below this line
            message = None
            j = i + 1
            while j < len(controls_sorted):
                c2 = controls_sorted[j]
                top2 = (c2.get("rect") or {}).get("top", 0)
                if top2 <= top:
                    j += 1
                    continue
                # prefer QTextBrowser or Text controls
                if c2.get("control_type") == "Text" or c2.get("class_name", "").endswith("QTextBrowser"):
                    candidate = (c2.get("name") or "").strip()
                    if candidate:
                        message = candidate
                        break
                j += 1
            msgs.append({"username": username, "timestamp": timestamp, "message": message or "", "rect": c.get("rect")})
            i = j
            continue

        # Case B: message widget with multiline that contains username line then message
        if (ctrl_type == "Text" or cls.endswith("QTextBrowser")) and name:
            # split lines and try to parse first line as 'username, [time]'
            lines = [ln.strip() for ln in name.splitlines() if ln.strip()]
            if lines:
                first = lines[0]
                m2 = uname_ts_re.match(first)
                if m2 and len(lines) >= 2:
                    username = m2.group("username").strip()
                    timestamp = f"{m2.group('hour')}:{m2.group('min')}"
                    message = "\n".join(lines[1:])
                    msgs.append({"username": username, "timestamp": timestamp, "message": message, "rect": c.get("rect")})
                    i += 1
                    continue

        # Case C: standalone message text without username (add with unknown username)
        if (ctrl_type == "Text" or cls.endswith("QTextBrowser")) and name:
            msgs.append({"username": None, "timestamp": None, "message": name, "rect": c.get("rect")})
            i += 1
            continue

        i += 1

    return msgs


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("title", help="Room window title substring")
    p.add_argument("--out", default="chat_messages.txt")
    args = p.parse_args()
    messages = get_chat_messages(args.title)
    with open(args.out, "w", encoding="utf-8") as f:
        for m in messages:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"Wrote {len(messages)} messages to {args.out}")


if __name__ == "__main__":
    main()
