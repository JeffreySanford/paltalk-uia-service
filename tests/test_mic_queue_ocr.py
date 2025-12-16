from tools.probe.mic_queue_ocr import parse_mic_queue_lines


def test_parse_lines_simple():
    lines = [
        "1. Gossip God",
        "2 elimenno",
        "Join Queue",
        "3 sharticus",
        "Remove Ads",
    ]
    res = parse_mic_queue_lines(lines)
    assert res == ["Gossip God", "elimenno", "sharticus"]


def test_parse_lines_numbers_and_noise():
    lines = ["1 Alice", "Bob", "Member since 2019", "Clear"]
    res = parse_mic_queue_lines(lines)
    assert res == ["Alice", "Bob"]
