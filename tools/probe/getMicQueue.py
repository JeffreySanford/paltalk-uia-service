"""Extract the mic queue (users waiting to speak) from the room UI."""
from typing import List
from app.probe import probe_window


def get_mic_queue(title_substr: str) -> List[str]:
    from pywinauto import Desktop

    def is_noise(name: str) -> bool:
        if not name:
            return True
        ln = name.lower()
        noise = ("join queue", "join_queue", "basebutton", "clear", "remove ads", "member since", "mic", "join")
        if any(n in ln for n in noise):
            return True
        if len(name) > 40:
            return True
        if sum(ch.isdigit() for ch in name) >= 3:
            return True
        return False

    try:
        d = Desktop(backend="uia")
        w = None
        for win in d.windows():
            if title_substr.lower() in (win.window_text() or '').lower():
                w = win
                break
        if not w:
            return []

        # Find MicQueue header control
        header = None
        for c in w.descendants():
            try:
                aid = getattr(c.element_info, 'automation_id', '') or ''
            except Exception:
                aid = ''
            cname = c.class_name() or ''
            name = (c.window_text() or c.element_info.name or '').strip()
            if 'MicQueueTitleItemWidget' in aid or 'MicQueueTitleItemWidget' in cname or name.lower().startswith('mic queue'):
                header = c
                break

        candidates = []
        if header:
            hrect = header.rectangle()
            col_left, col_right, start_top = hrect.left, hrect.right, hrect.bottom
            for c in w.descendants():
                try:
                    rect = c.rectangle()
                    if rect.left < col_left - 20 or rect.right > col_right + 20:
                        continue
                    if rect.top <= start_top:
                        continue
                    # Try to extract visible text from control or its children
                    text = (c.window_text() or '')
                    if not text:
                        # check children
                        for ch in c.descendants():
                            text = (ch.window_text() or '')
                            if text:
                                break
                    text = text.strip()
                    if not text:
                        continue
                    if is_noise(text):
                        continue
                    candidates.append((rect.top, text))
                except Exception:
                    continue

        # sort and dedupe
        candidates = sorted(candidates)
        seen = set()
        out = []
        for _, name in candidates:
            if name not in seen:
                seen.add(name)
                out.append(name)
            # If we found nothing, try OCR fallback
            if not out:
                try:
                    from .mic_queue_ocr import ocr_region, parse_mic_queue_lines
                    # If we have a header control, capture a small region below it; otherwise fallback to the whole window
                    if header:
                        bbox = (hrect.left, hrect.bottom + 4, hrect.right, hrect.bottom + 200)
                    else:
                        wr = w.rectangle()
                        bbox = (wr.left, wr.top + int((wr.bottom - wr.top) * 0.3), wr.right, wr.bottom)
                    lines, err = ocr_region(bbox)
                    if err:
                        return []
                    ocr_names = parse_mic_queue_lines(lines)
                    return ocr_names
                except Exception:
                    return out
            return out
    except Exception:
        return []
    # dedupe preserving order
    seen = set()
    out = []
    for n in items:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("title")
    p.add_argument("--out", default="mic_queue.txt")
    args = p.parse_args()
    q = get_mic_queue(args.title)
    with open(args.out, "w", encoding="utf-8") as f:
        for name in q:
            f.write(name + "\n")
    print(f"Wrote {len(q)} entries to {args.out}")


if __name__ == "__main__":
    main()
