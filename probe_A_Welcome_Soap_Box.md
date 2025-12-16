# Probe Results: "A Welcome Soap Box"

**Window Title:** A Welcome Soap Box  
**Activated:** false  
**Window Rect:** { "left": -2461, "top": -38, "right": -1405, "bottom": 645 }

## Controls
- **Button:** Minimize (`rect`: {left: -1544, top: -68, right: -1497, bottom: -38})
- **Button:** Maximize (`rect`: {left: -1497, top: -68, right: -1451, bottom: -38})
- **Button:** Close (`rect`: {left: -1451, top: -68, right: -1404, bottom: -38})
- **TitleBar:** (rect: {left: -2445, top: -66, right: -1405, bottom: -38})
- **MenuBar:** System (rect: {left: -2461, top: -61, right: -2439, bottom: -39})
- **MenuItem:** System (rect: {left: -2461, top: -61, right: -2439, bottom: -39})
- **Group:** RoomWidget (rect: {left: -2461, top: -38, right: -1405, bottom: 645})
- **Button:** Room_Top_ShareButton (rect: {left: -1661, top: -27, right: -1625, bottom: 9})
- **Button:** Send gift (rect: {left: -1617, top: -27, right: -1581, bottom: 9})
- **Button:** Toggle Speaker (rect: {left: -1573, top: -27, right: -1537, bottom: 9})
- **Button:** Show Speaker Menu (rect: {left: -1537, top: -27, right: -1520, bottom: 9})
- **Button:** Toggle Webcam (rect: {left: -1512, top: -27, right: -1476, bottom: 9})
- **Button:** Show Webcam Menu (rect: {left: -1476, top: -27, right: -1459, bottom: 9})
- **Button:** Menu button (rect: {left: -1451, top: -27, right: -1415, bottom: 9})
- **CheckBox:** Unfollow (rect: {left: -2226, top: -26, right: -2151, bottom: -10})
- ...

## Mic Controls
- **Text:** 76 second mic max for boring people. (rect: {left: -2206, top: -6, right: -1667, bottom: 11})
- **Button:** Join Queue to Talk (rect: {left: -1583, top: 238, right: -1419, bottom: 261})
- ...

## Speaker Candidates
- **Button:** Minimize
- **Button:** Maximize
- **Button:** Close
- **Button:** Room_Top_ShareButton
- **Button:** Send gift
- **Button:** Toggle Speaker
- ...

---



## UI Regions Identified

### 1. Current Speaker
- **Region:** Directly under the "Talking Now" label, with a mic icon on the right.
- **Username:** `Gossip God`

### 2. Mic Queue
- **Region:** Below the current speaker, a vertical list of usernames waiting for the mic.
- **Usernames (sample):**
	- (no users currently in the mic queue)

### Mic Queue Extraction
- I added `tools/probe/getMicQueue.py` which writes `mic_queue.txt` containing the current queue (one username per line).
- Current result: `mic_queue.txt` is empty (no users waiting to speak at the time of probe).
 - Current result (manual update): `mic_queue.txt` now shows the **current speaker** and **waiting list**.
 - Mic queue is now **probe-generated**; manual edits were removed. Run `tools/probe/getMicQueue.py` to refresh `mic_queue.txt`.
 - OCR fallback: if the UIA probe finds no readable queue entries (common when the mic queue is rendered inside a web view), `getMicQueue` will attempt an OCR-based fallback using `tools/probe/mic_queue_ocr.py`.
	 - This fallback is automatic when no UIA results are found.
	 - Requirements: `pytesseract` Python package and the Tesseract binary installed and on PATH. Install via `pip install pytesseract pillow` and platform Tesseract installer.
	 - The OCR helper captures a small region below the mic header and attempts to extract visible usernames heuristically.

### 3. Chat Room Members
- **Region:** Typically a sidebar or panel listing all users currently in the room.
- **Count:** 27 users (as observed)
- **Usernames (sample):**
	- (usernames would be listed here as found in the probe)

- **Region:** Above the input box, this area displays all chat messages in the room.
- **Description:** Each message is typically a widget (e.g., `TextMessageWidget`) or a text control.
- **Current State:** No message has been sent in the room yet by automation.
+### 4. Chat Area (Text Messages)
- **Region:** Above the input box, this area displays all chat messages in the room.
- **Component Names:**
	- `ui::chatlog::TextMessageWidget` (main message container)
	- `ui::chatlog::UsernameWidget` (username, if available)
	- `QLabel` or `QTextBrowser` (message text)
- **Extraction Structure:**
	- Each message is extracted as a JSON object with fields:
		- `username`: (currently null, placeholder for future extraction)
		- `timestamp`: (currently null, placeholder for future extraction)
		- `message`: the message text
- **Current State:** No message has been sent in the room yet by automation. See `chat_messages.txt` for extracted samples.
- **Region:** Above the input box, this area displays all chat messages in the room.
- **Description:** Each message is typically a widget (e.g., `TextMessageWidget`) or a text control.
- **Current State:** No message has been sent in the room yet by automation.

### 5. Input Box
- **Region:** Bottom of the chat window.
- **Description:** Input box with two icons next to it and a placeholder text: "Write a message"
- **Purpose:** For sending chat messages to the room.

---

---

**Note:** This is a partial list. The actual probe output contains many more controls and details. For a full export, refer to the raw JSON output from the probe.

## Tooling / Scripts (cleaned up)
I created a small `tools` package with focused utilities and a separate `tools/send` module for message sending.

- `tools/probe/getRoomTitle.py` — returns the window title for a given substring
- `tools/probe/getSpeakerNow.py` — identifies the current speaker (heuristic)
- `tools/probe/getChatterList.py` — extracts the list of chat room participants
- `tools/probe/getChatMessages.py` — extracts left-side chat messages and writes `chat_messages.txt`
- `tools/send/send_message.py` — CLI wrapper around the `send_message` automation

Run scripts with: `python -m tools.probe.getChatMessages "A Welcome Soap Box"` etc.

Note: older ad-hoc scripts used while exploring the UI are deprecated; the focused tools above should be used going forward.
