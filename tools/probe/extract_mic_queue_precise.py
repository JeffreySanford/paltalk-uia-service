"""More precise extractor for mic queue using control coordinates and text filters."""
import json
from pathlib import Path


def load_dump(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def is_ui_noise(name: str) -> bool:
    n = name.lower()
    if not n:
        return True
    noise = ["join queue", "join_queue", "basebutton", "clear", "remove ads", "member since", "mic"]
    if any(k in n for k in noise):
        return True
    # exclude long banner lines
    if len(name) > 40:
        return True
    # exclude strings with many digits
    if sum(ch.isdigit() for ch in name) >= 3:
        return True
    return False


def extract(dump_path: Path):
    data = load_dump(dump_path)

    # find MicQueue header rect
    header_rect = None
    for c in data:
        aid = c.get('automation_id') or ''
        cname = c.get('class_name') or ''
        name = (c.get('name') or '').strip()
        if 'MicQueueTitleItemWidget' in aid or 'MicQueueTitleItemWidget' in cname or name.lower().startswith('mic queue'):
            header_rect = c.get('rect')
            break

    if header_rect:
        col_left = header_rect.get('left')
        col_right = header_rect.get('right')
        start_top = header_rect.get('bottom')
    else:
        # fallback to member-list column area heuristics
        col_left, col_right, start_top = -1600, -1400, 200

    candidates = []
    for c in data:
        name = (c.get('name') or '').strip()
        rect = c.get('rect') or {}
        if not name:
            continue
        left = rect.get('left', 0)
        right = rect.get('right', 0)
        top = rect.get('top', 0)
        # must be in column and below header
        if left < col_left - 20 or right > col_right + 20:
            continue
        if top <= start_top:
            continue
        # exclude noise
        if is_ui_noise(name):
            continue
        candidates.append((top, name))

    # dedupe and sort by top
    candidates = sorted(candidates)
    seen = set()
    queue = []
    for _, name in candidates:
        if name not in seen:
            seen.add(name)
            queue.append(name)

    # find current speaker (talker area)
    speaker = None
    for c in data:
        cname = c.get('class_name') or ''
        if 'TalkerWidget' in cname or 'TalkingNow' in (c.get('automation_id') or ''):
            # search for nearest visible name below
            r = c.get('rect') or {}
            ttop = r.get('top', 0)
            nearest = None
            best = None
            for c2 in data:
                name2 = (c2.get('name') or '').strip()
                if not name2 or is_ui_noise(name2):
                    continue
                r2 = c2.get('rect') or {}
                if r2.get('top', 0) >= ttop:
                    dist = r2.get('top', 0) - ttop
                    if best is None or dist < best:
                        best = dist
                        nearest = name2
            speaker = nearest
            break

    return speaker, queue


def main():
    dump = Path('all_controls_dump.json')
    if not dump.exists():
        print('Dump not found')
        return
    speaker, queue = extract(dump)
    out = Path('mic_queue.txt')
    with out.open('w', encoding='utf-8') as f:
        f.write(f'Current Speaker: {speaker or "(unknown)"}\n')
        f.write('Waiting to speak:\n')
        if queue:
            for n in queue:
                f.write('- ' + n + '\n')
        else:
            f.write('(none)\n')
    print('Wrote mic_queue.txt; speaker=', speaker, 'queue=', queue)


if __name__ == '__main__':
    main()
