# VoicePerio v2.1.2 Release Notes

**Release Date:** February 19, 2026
**Version:** 2.1.2
**Platform:** Windows 10/11 (64-bit)
**Distribution:** Portable Bundle (No Installation Required)

---

## VoicePerio v2.1.2 — Dentrix Command Accuracy Update

This release focuses entirely on correctness and usability of the Dentrix integration. Every change was derived directly from [Dentrix Enterprise's official keyboard shortcut documentation](https://blog.dentrixenterprise.com/perio-chart-shortcut-keys/) to ensure all voice commands map to exactly the right key events. Several long-standing bugs in navigation and number entry have been fixed, a new voice command has been added, audio feedback has been overhauled, and a non-functional UI element has been removed.

No new dependencies are introduced. All changes are fully compatible with the portable no-exe distribution — just replace the `app/` folder contents and relaunch.

---

## What's New

### Double-Digit Pocket Depth Entry (10–19 mm)

Voice entry of probing depths from 10–19 mm is now supported. Per Dentrix's documented shortcut, values in this range require a **numpad minus key followed by the units digit** (e.g., 12 = `subtract` + `num2`). This sequence is now generated automatically.

Previously, any spoken number above 9 was silently disabled because the old implementation attempted to type `"10"`, `"12"`, etc. as plain text, which Dentrix does not accept.

**What to say:**
- `"ten"` → 10 mm (numpad `−` + `0`)
- `"eleven"` → 11 mm (numpad `−` + `1`)
- `"twelve"` through `"nineteen"` follow the same pattern

Double-digit words are always treated as their own field entry regardless of how quickly they are spoken — they cannot be grouped with adjacent digits.

Phonetic variations handled by fuzzy matching: `forteen` → fourteen, `fiveteen` → fifteen, `sixten` → sixteen, `eightteen` → eighteen, `ninteen` → nineteen, and others.

---

### Fixed: "Next" Command Now Uses Page Down

The `"next"` voice command was sending `Enter` instead of `Page Down`. In Dentrix, `Enter` follows the active navigation script path while `Page Down` is the explicit **Next** button equivalent. This caused inconsistent cursor movement when saying "next" — the command appeared to do nothing or jump unexpectedly.

`"next"` now sends `Page Down`, making it symmetric with `"previous"` which correctly sends `Page Up`. The `"skip"` command continues to use `Enter` internally, which is the correct key for script-path advancement.

---

### New Voice Command: "Clear"

Saying `"clear"` now sends the `Delete` key to Dentrix, clearing all entries in the current selection — the same action as the Clear button in Dentrix's data entry controls.

This command was defined in the configuration file but was completely absent from the primary voice processing path. It was never recognised by the speech engine and never executed. It is now fully wired through all layers: vocabulary, parser, and executor.

---

### Audio Feedback Overhaul

The previous chime played whatever Windows had configured for the system "Asterisk" sound event — an unpredictable, often long audio clip outside the application's control.

All sounds are now **generated programmatically** using `winsound.Beep` and play in a background thread, so charting is never blocked. Three selectable options replace the single old chime:

| Option | Sound | Duration |
|---|---|---|
| **Click** | Single 1200 Hz tone | 40 ms |
| **Beep** | 880 Hz then 1100 Hz (two-note) | 140 ms |
| **Chime** | C5 → E5 → G5 (melodic) | ~260 ms |
| **Readback** | Spoken confirmation (existing) | varies |
| **Off** | Silence | — |

The sound style is selected from the **Behavior** tab in Settings. The default for new installations has been changed from `off` to `click` so audio feedback works out of the box.

---

### Removed: Save Button

The Save button that appeared in the VoicePerio overlay has been removed. It was non-functional — clicking it only appended `"Save command"` to the internal feedback history and sent nothing to Dentrix.

Since VoicePerio is designed for hands-free use alongside an open Dentrix window, UI buttons that duplicate Dentrix actions add no value. The `"save"` voice command (`Ctrl+S`) remains fully intact and is unaffected by this change.

---

## Voice Command Reference (Updated)

### Pocket Depths

| Say | Result |
|---|---|
| `"three"` | Types `3` |
| `"three two three"` | Types `3`, `2`, `3` into successive fields |
| `"ten"` | Types `10` (numpad `−` + `0`) |
| `"fifteen"` | Types `15` (numpad `−` + `5`) |

### Navigation

| Say | Dentrix Key | Notes |
|---|---|---|
| `"next"` | `Page Down` | Explicit next field |
| `"previous"` / `"back"` | `Page Up` | Previous field |
| `"home"` | `Home` | First position in script |
| `"skip"` | Types `000` | Placeholder zeros, auto-advances |
| `"skip five"` | `Enter` × 5 | Advances 5 fields |

### Indicators

| Say | Dentrix Key |
|---|---|
| `"bleeding"` / `"bleed"` / `"bop"` | `B` |
| `"suppuration"` / `"pus"` | `S` |
| `"plaque"` | `A` (opens context menu) |
| `"calculus"` / `"tartar"` | `C` |
| `"furcation"` / `"furca"` | `G` (opens context menu) |
| `"mobility"` / `"mobile"` | `M` |
| `"recession"` | `R` |

### Actions

| Say | Dentrix Key |
|---|---|
| `"save"` | `Ctrl+S` |
| `"clear"` | `Delete` — clears current selection |
| `"undo"` / `"correction"` / `"scratch"` | `Ctrl+Z` |
| `"enter"` / `"okay"` | `Enter` |
| `"cancel"` / `"escape"` | `Escape` |

---

## Compatibility

| Component | Status |
|---|---|
| Portable no-exe distribution | Fully compatible — replace `app/` folder |
| No new pip dependencies | All new audio code uses Python stdlib only (`winsound`, `threading`) |
| Existing config files | Compatible — new `audio_feedback_mode` values (`click`, `beep`) are additive |
| Vosk speech model | Unchanged |
| Windows 10 / 11 | Supported |

---

## Changelog

### v2.1.2 (2026-02-19)

#### Added
- Voice entry of pocket depths 10–19 mm via Dentrix numpad minus-key protocol (`subtract` + numpad units digit)
- Spoken number words `"ten"` through `"nineteen"` added to speech grammar and parser
- Phonetic fuzzy-matching for double-digit mishearings (e.g., `"forteen"`, `"fiveteen"`, `"eightteen"`)
- `"clear"` voice command — sends `Delete` key to Dentrix, clearing the current selection
- `_play_click()` audio feedback — 1200 Hz, 40 ms programmatic tone
- `_play_beep()` audio feedback — 880 Hz + 1100 Hz double-beep, 140 ms total
- `_play_tones()` shared helper for background-threaded tone generation via `winsound.Beep`
- `NumberGroup.requires_minus_protocol` property for double-digit detection
- `ActionExecutor.type_perio_number()` method — routes single digits to numpad keys, 10–19 to minus protocol, multi-digit sequences to `type_text`
- `NUMPAD_DIGIT_KEYS` and `NUMPAD_MINUS_KEY` constants on `ActionExecutor`
- Audio feedback sound style selector in Settings → Behavior tab (Click / Beep / Chime / Readback / Off)

#### Fixed
- `"next"` voice command now sends `Page Down` instead of `Enter`, correctly matching the Dentrix Next button shortcut
- `"clear"` voice command was previously defined in config but never reached the execution path — now fully wired through vocabulary, parser, and executor
- Audio feedback chime was controlled by the Windows system sound configuration (MB_ICONASTERISK); sounds are now generated programmatically and have consistent duration regardless of system settings

#### Changed
- `go_next()` in `NumberSequencer` hardcoded to `Page Down` (was `self.advance_key` / `Enter`)
- `chime` audio feedback mode now plays a short programmatic C5-E5-G5 melody (~260 ms) instead of the Windows Asterisk system sound
- Default `audio_feedback_mode` changed from `"off"` to `"click"` for new installations
- Audio feedback modes expanded from `{off, chime, readback}` to `{off, click, beep, chime, readback}`
- `NumberSequencer.enter_number_groups()` and `enter_single_value()` now call `type_perio_number()` instead of `type_text()` to route all numeric entry through the correct Dentrix key protocol
- `type_number()` on `ActionExecutor` now accepts range 0–19 (was 0–15) and delegates to `type_perio_number()`
- Double-digit number words in `group_numbers()` are always forced into their own `NumberGroup` regardless of timing, preventing invalid digit concatenation
- `WORD_TO_DIGIT` map extended with 10 new entries (`"ten"` through `"nineteen"`)
- `_DOUBLE_DIGIT_VALUES` frozenset introduced for O(1) membership testing

#### Removed
- Save button from the VoicePerio overlay UI (`CompactActionBar.save_button`)
- `save_requested` signal from `CompactActionBar` and `ModernMedicalUI`
- `GUIManager._on_save_requested()` dead handler method
- Signal connection `modern_ui.save_requested → _on_save_requested` in `GUIManager._connect_signals()`

---

## Previous Releases

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for v2.1.0 and v2.0.0 release notes.
