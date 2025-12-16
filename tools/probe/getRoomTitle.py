"""Return the actual room window title for a given substring.
"""
from app.probe import probe_window


def get_room_title(title_substr: str):
    res = probe_window(title_substr, activate=False)
    return res.get("title") if res.get("found") else None


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("title")
    args = p.parse_args()
    title = get_room_title(args.title)
    print(title or "(not found)")


if __name__ == "__main__":
    main()
