"""Probe utilities for Paltalk UI Automation PoC
Provides probe_window and send_message functions.
"""
from typing import Dict, List, Optional
import platform

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    try:
        from pywinauto import Desktop, keyboard
        from pywinauto.keyboard import send_keys
    except Exception as e:
        Desktop = None
        send_keys = None
        _IMPORT_ERROR = e
else:
    Desktop = None
    send_keys = None


def rect_to_dict(rect) -> Dict[str, int]:
    return {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}


def element_info(elem) -> Dict:
    try:
        info = {
            "control_type": elem.element_info.control_type,
            "automation_id": elem.element_info.automation_id,
            "name": elem.element_info.name,
            "framework_id": elem.element_info.framework_id,
            "class_name": elem.element_info.class_name,
            "rect": rect_to_dict(elem.rectangle()),
        }
    except Exception as e:
        info = {"error": str(e)}
    return info


def _find_window_by_title(substr: str):
    d = Desktop(backend="uia")
    children = d.windows()
    for w in children:
        title = (w.window_text() or "").strip()
        if substr.lower() in title.lower():
            return w
    return None


def probe_window(title_substr: str, max_elems: int = 300, activate: bool = False) -> Dict:
    """Probe a Paltalk window and return controls plus candidate speaker names.

    Returns a dict containing found(bool), title, rect, controls[], speaker_candidates[], mic_controls[], activated(bool)
    """
    if not IS_WINDOWS:
        return {"found": False, "error": "Not running on Windows"}

    if Desktop is None:
        return {"found": False, "error": f"pywinauto import failed: {_IMPORT_ERROR}"}

    w = _find_window_by_title(title_substr)
    if not w:
        return {"found": False, "title_substr": title_substr}

    out = {"found": True, "title": w.window_text(), "controls": []}
    try:
        out["rect"] = rect_to_dict(w.rectangle())
    except Exception:
        out["rect"] = None

    out["activated"] = False
    if activate:
        try:
            try:
                w.restore()
            except Exception:
                pass
            try:
                w.set_focus()
            except Exception:
                try:
                    w.element_info.element.SetFocus()
                except Exception:
                    pass
            import time
            time.sleep(0.5)
            out["activated"] = True if w.is_active() else False
        except Exception as e:
            out["activated_error"] = str(e)

    try:
        desc = w.descendants()
    except Exception:
        desc = []

    def keyfn(e):
        try:
            r = e.rectangle()
            return (r.top if r else 0, r.left if r else 0)
        except Exception:
            return (0, 0)

    desc_sorted = sorted(desc, key=keyfn)[:max_elems]
    for e in desc_sorted:
        out["controls"].append(element_info(e))

    candidates = []
    for c in out["controls"]:
        name = c.get("name") or ""
        if name and len(name.strip()) > 1 and not name.strip().isdigit():
            candidates.append({"name": name, "rect": c.get("rect"), "control_type": c.get("control_type")})
    out["speaker_candidates"] = candidates[:20]

    mic_matches = [c for c in out["controls"] if (c.get("name") or "").lower().find("mic") != -1 or (c.get("automation_id") or "").lower().find("mic") != -1]
    out["mic_controls"] = mic_matches

    return out


def send_message(title_substr: str, message: str, activate: bool = True) -> Dict:
    """Attempt to post a message into the room window.

    Strategy:
    - Find window, optionally activate
    - Try to find Edit or Document controls to set text; otherwise set focus and send keystrokes
    """
    if not IS_WINDOWS:
        return {"ok": False, "error": "Not running on Windows"}
    if Desktop is None:
        return {"ok": False, "error": f"pywinauto import failed: {_IMPORT_ERROR}"}

    w = _find_window_by_title(title_substr)
    if not w:
        return {"ok": False, "error": "window_not_found"}

    try:
        if activate:
            try:
                w.restore()
            except Exception:
                pass
            try:
                w.set_focus()
            except Exception:
                try:
                    w.element_info.element.SetFocus()
                except Exception:
                    pass
    except Exception as e:
        return {"ok": False, "error": f"activate_failed: {e}"}

    # Try to find an edit control
    try:
        edits = [c for c in w.descendants() if getattr(c.element_info, 'control_type', '').lower() in ('edit', 'document')]
    except Exception:
        edits = []

    if edits:
        target = edits[-1]
        try:
            ctrl = target.wrapper_object()
            try:
                ctrl.set_edit_text(message)
            except Exception:
                try:
                    ctrl.type_keys(message, with_spaces=True)
                except Exception:
                    pass
            # Send Enter
            try:
                ctrl.type_keys('{ENTER}')
            except Exception:
                send_keys('{ENTER}')
            return {"ok": True, "method": "control"}
        except Exception as e:
            return {"ok": False, "error": f"control_send_failed: {e}"}

    # Fallback: set focus and send keys to window
    try:
        w.set_focus()
        send_keys(message + "{ENTER}")
        return {"ok": True, "method": "keys_fallback"}
    except Exception as e:
        return {"ok": False, "error": f"send_keys_failed: {e}"}
