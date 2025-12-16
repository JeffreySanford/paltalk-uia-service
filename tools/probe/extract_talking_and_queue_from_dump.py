"""Extract current speaker and mic queue from dump more carefully by inspecting TalkerWidget and MemberItemWidgets."""
import json
from pathlib import Path


def load_dump(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def find_talker_and_queue(data):
    # Find TalkerWidget rect
    talker_rect = None
    for c in data:
        if c.get('class_name', '').endswith('TalkerWidget'):
            talker_rect = c.get('rect')
            break

    speaker = None
    if talker_rect:
        ttop = talker_rect.get('top', 0)
        tleft = talker_rect.get('left', 0)
        tright = talker_rect.get('right', 0)
        # search for text controls inside or just below this rect
        candidates = []
        for c in data:
            name = (c.get('name') or '').strip()
            if not name:
                continue
            r = c.get('rect') or {}
            if r.get('left', 1e9) >= tleft - 20 and r.get('right', -1e9) <= tright + 20 and r.get('top', 0) >= ttop - 10:
                candidates.append((r.get('top', 0), name))
        if candidates:
            candidates.sort()
            speaker = candidates[0][1]

    # Now find mic queue members by locating MemberItemWidgets inside RoomMemberListWidget
    queue = []
    for c in data:
        if c.get('class_name', '') == 'ui::rooms::member_list::MemberItemWidget':
            # Within this widget look for PlainText or UsernameWidget children with names
            r = c.get('rect') or {}
            left, top, right = r.get('left', 0), r.get('top', 0), r.get('right', 0)
            # find name text near this rect
            for c2 in data:
                name = (c2.get('name') or '').strip()
                if not name:
                    continue
                r2 = c2.get('rect') or {}
                if abs(r2.get('top', 0) - top) <= 4 and abs(r2.get('left', 0) - left) <= 40:
                    lname = name.lower()
                    if any(k in lname for k in ('join queue', 'button', 'member since', 'mic')):
                        continue
                    queue.append((top, name))
                    break
    queue = [n for _, n in sorted(queue)]
    # allow only unique names, preserve order
    seen = set()
    outq = []
    for n in queue:
        if n not in seen:
            seen.add(n)
            outq.append(n)
    return speaker, outq


def main():
    dump = Path('all_controls_dump.json')
    if not dump.exists():
        print('Dump not found')
        return
    data = load_dump(dump)
    speaker, queue = find_talker_and_queue(data)
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
