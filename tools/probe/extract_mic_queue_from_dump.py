"""Extract mic queue and current speaker from the existing UI dump (all_controls_dump.json).

This is a fallback method that parses the saved dump when live UIA probing doesn't expose the mic queue.
"""
import json
from pathlib import Path


def extract_from_dump(dump_path: Path):
    data = json.loads(dump_path.read_text(encoding='utf-8'))

    # Find MicQueueTitleItemWidget
    header = None
    for c in data:
        aid = c.get('automation_id') or ''
        cname = c.get('class_name') or ''
        if 'MicQueueTitleItemWidget' in aid or 'MicQueueTitleItemWidget' in cname:
            header = c
            break

    # Find TalkingNowWidget and speaker
    speaker = None
    for c in data:
        aid = c.get('automation_id') or ''
        cname = c.get('class_name') or ''
        if 'TalkingNowWidget' in aid or 'TalkingNowWidget' in cname:
            # look for following text or child with name
            rect = c.get('rect') or {}
            top = rect.get('top', 0)
            # search for nearest text control below the widget
            candidate = None
            best_dist = None
            for c2 in data:
                name = (c2.get('name') or '').strip()
                if not name:
                    continue
                r2 = c2.get('rect') or {}
                if r2.get('top', 0) > top:
                    dist = r2.get('top', 0) - top
                    if best_dist is None or dist < best_dist:
                        best_dist = dist
                        candidate = name
            if candidate:
                speaker = candidate
            break

    queue = []
    if header:
        hrect = header.get('rect') or {}
        hleft, hright, hbottom = hrect.get('left', 0), hrect.get('right', 0), hrect.get('bottom', 0)
        # find PlainText or UsernameWidget PlainText items below header within same column
        for c in data:
            name = (c.get('name') or '').strip()
            rect = c.get('rect') or {}
            if not name:
                continue
            left, right, top = rect.get('left', 0), rect.get('right', 0), rect.get('top', 0)
            if top <= hbottom:
                continue
            if left >= hleft - 10 and right <= hright + 10:
                lname = name.lower()
                if any(k in lname for k in ('join queue', 'join_queue', 'button', 'basebutton', 'clear')):
                    continue
                # Heuristic: usernames are shortish
                if len(name) > 40:
                    continue
                queue.append((top, name))
        # sort by vertical position
        queue = [n for _, n in sorted(queue)]

    return speaker, queue


def main():
    dump = Path('all_controls_dump.json')
    if not dump.exists():
        print('Dump file not found.')
        return
    speaker, queue = extract_from_dump(dump)
    out = Path('mic_queue.txt')
    with out.open('w', encoding='utf-8') as f:
        if speaker:
            f.write(f'Current Speaker: {speaker}\n')
        else:
            f.write('Current Speaker: (unknown)\n')
        f.write('Waiting to speak:\n')
        if queue:
            for name in queue:
                f.write('- ' + name + '\n')
        else:
            f.write('(none)\n')
    print('Wrote mic_queue.txt with', len(queue), 'waiting entries; speaker:', speaker)


if __name__ == '__main__':
    main()
