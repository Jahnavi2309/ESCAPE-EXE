# ESCAPE.EXE — THE LAST 10 MINUTES

A complete offline desktop escape-room mystery built with Python and Tkinter. Wake up inside a containment facility, investigate an abandoned office, decipher a laboratory terminal, and break the final seal before ten minutes expire.

## Requirements and installation

- Python **3.10 or newer**, with Tkinter enabled.
- macOS, Windows, or Linux with a graphical desktop.
- No pip packages, external images, audio files, network connection, or accounts required.

Download or copy this directory. Open a terminal in the directory and run:

```sh
python main.py
```

On systems that name Python 3 `python3`, use `python3 main.py`. Verify your version with `python --version`. The bundled runtime on the development machine was Python 3.12; the system `python3` was an older 3.9 installation.

## Features

- Four connected puzzles with a final code derived from your recovered answers.
- Clean Frame-based screens with consistent spacing, readable widgets, subtle hover effects and Canvas room illustrations. Click the note, office evidence, terminal and unlocked doors to explore.
- Resizable 1100 × 720 window; minimum 1000 × 680.
- Monotonic ten-minute countdown shared by all rooms and investigation panels.
- Evidence inventory, scrollable journal, reusable custom investigation panels, contextual hints, four final-clue review buttons and a simple alphabet reference chart.
- Three valid incorrect guesses per room, deterministic scores, ranks, victory and two defeat paths.

## Controls and rules

Click **START GAME**, read the introduction, then **BEGIN**. The countdown starts only at BEGIN. Click highlighted scene objects to investigate them. Type an answer and press **ENTER** or **CHECK ANSWER**. In the office, click the safe to enter its combination; discover all four clues first. Collect the brass key and click the exit to use it.

Click **JOURNAL / INVENTORY** to review recovered evidence. It never reveals undiscovered clues. **HINT** shows the current room's hint. **ESC** or CLOSE dismisses a panel. Panels do not pause the countdown. Complete the first and third rooms, then select NEXT ROOM; their success messages remain visible until you continue. After solving the final lock, click **OPEN DOOR** to display the victory screen. The timer and escape score freeze when that lock is solved.

Empty entries, non-ASCII characters, malformed numeric codes, and wrong numeric lengths do not consume attempts. A nonempty alphabetic laboratory guess is a valid attempt. Three wrong valid guesses in any room cause security lockdown. Reaching zero causes timeout. Restart and main menu provide fresh runs with no retained clues or penalties.

## Scoring

| Event | Points |
| --- | ---: |
| Completed room | +250 |
| Wrong valid answer | −25 |
| First hint use in each room | −50 |
| Successful escape | +1 per full remaining second |

Scores are clamped to zero after summing rewards and penalties. Repeated hints in the same room do not add penalties. Opening the office safe alone does not complete the room: using the key at the exit does. Time and score freeze on victory or defeat; defeat does not earn a time bonus.

| Final score | Rank |
| --- | --- |
| 1300+ | MASTER ESCAPIST |
| 1000–1299 | EXPERT |
| 750–999 | DETECTIVE |
| 0–749 | SURVIVOR |

## Project structure

```text
main.py               Application entry point
config.py             Palette, room names, clues, hints
state.py              Puzzle rules, inventory, scoring, monotonic clock
game.py               Frame layout, room drawings, panels, timer callback
tests/test_game.py     Automated rule and complete-playthrough tests
tests/gui_smoke.py     Optional real-display GUI integration smoke test
README.md             Setup and game guide
VIVA_GUIDE.md          Implementation walkthrough and 28 viva questions
```

The compact structure deliberately keeps the view in one class and the independently testable game rules in another. There are no asset paths to configure.

## Python concepts demonstrated

Classes and methods; dictionaries, lists and sets; string validation and Caesar-shift arithmetic; injected clock functions; monotonic elapsed-time calculation; event-driven GUI programming; small nested functions for object callbacks; Canvas drawing and tags; Frame layout, Tkinter widgets and bindings; nonblocking `after()` countdown; and standard-library `unittest` tests.

One scheduled callback updates the countdown. It reads elapsed monotonic time rather than counting callbacks. The active screen guards clock checks, and shutdown cancels the scheduled job. No GUI thread sleeps or nested mainloops are used.

## Testing

Run all automated logic tests from this directory:

```sh
python -m unittest discover -s tests -v
```

Tests cover code validation, clue requirements, key collection and use, Caesar decoding, derived master code, invalid input, all-room attempt limits, hint deductions, rank boundaries, inventory deduplication, reset, timer accuracy and a complete successful escape.

With a working graphical desktop, also run:

```sh
python tests/gui_smoke.py
```

This opens actual Tkinter windows and drives every screen, clickable room exploration, Enter submission, panels, the explicit final exit, lockdown, timeout and restart. It also checks widget bounds and control heights at 1100 × 720, 1000 × 680 and 1400 × 900, including investigation panels. It is a scripted integration smoke test; also play a full run manually to assess pacing, readability and hover interactions.

Development verification: 14 rule tests passed under Python 3.12.14. The real macOS display smoke test passed using Tk 9.0. No Windows/Linux desktop visual checks were performed.

## Troubleshooting

- **macOS:** Prefer a current Python installer from python.org that includes a compatible Tcl/Tk. Apple's command-line-tools Python can be old or linked to old Tk. Check `python -m tkinter`; it should open a demonstration window. Launch from a logged-in desktop session.
- **Windows:** Run the Python installer again and ensure **tcl/tk and IDLE** is enabled. `py -3 main.py` can select Python 3 when `python` points to another installation. Start in a terminal to see error messages.
- **Linux:** Install your distribution's Tkinter package (commonly `python3-tk`) and use a desktop display, then run `python3 main.py`.
- **No window / display error:** Tkinter requires a graphical session. Headless environments can run the rule tests but cannot launch the game. A macOS sandbox without display access can also produce a Tk scaling or service-connection error.
- **Fonts:** TkDefaultFont and TkFixedFont use the platform’s standard fonts. No font download is required.

## Viva preparation

See [VIVA_GUIDE.md](VIVA_GUIDE.md) for a walkthrough of the actual code, short examples, the final-code calculation, a demonstration order and 28 common viva questions.

### Blank window with Apple's Python on macOS

The system `python3` on this development Mac is Python 3.9 linked to legacy Tk 8.5. It can open a blank window on current macOS. `main.py` now checks the runtime before building the interface. If that old installation is selected and the existing modern Codex Python is available, it relaunches with that runtime. No download or installation occurs. On other computers, use Python 3.10+ with Tk 8.6+; an unsupported installation shows a clear terminal message.

This workspace includes a local VS Code interpreter setting and a **Run ESCAPE.EXE** task pointing at the tested Python installation. Use **Terminal → Run Build Task** (Cmd+Shift+B on this Mac). These `.vscode` paths are specific to this machine; change them when copying the project to another computer. Typing `python3 main.py` also uses the startup check.
