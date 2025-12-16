"""Send messages into a Paltalk room using the app.probe.send_message helper."""
from app.probe import send_message


def send_message_cli(title_substr: str, message: str):
    return send_message(title_substr, message, activate=True)


def main():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("title")
    p.add_argument("message")
    args = p.parse_args()
    res = send_message_cli(args.title, args.message)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
