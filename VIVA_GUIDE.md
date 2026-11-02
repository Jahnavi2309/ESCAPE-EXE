# ESCAPE.EXE — Simple Viva Guide

## 1. What the project does

ESCAPE.EXE is an offline desktop escape-room game with four connected puzzles. The player explores clickable objects, collects evidence, opens locks and tries to escape within ten minutes. Three wrong answers in any room cause lockdown. The application includes instructions, a story introduction, inventory and journal, hints, scores and restart screens.

## 2. Why Python and Tkinter?

Python has readable syntax and useful standard libraries. Tkinter comes with most desktop Python installations and provides windows, labels, buttons, text fields and Canvas drawing. The game needs no external packages or internet connection.

## 3. Main files

| File | Responsibility |
| --- | --- |
| `main.py` | Creates `EscapeGame` and starts `mainloop()` |
| `game.py` | Builds screens, draws rooms and responds to clicks |
| `state.py` | Stores game data and checks puzzle rules, time and scores |
| `config.py` | Holds colors, room names, office clues and hints |
| `tests/test_game.py` | Tests the game rules without opening a window |
| `tests/gui_smoke.py` | Opens real windows and checks interactions and layout |

There are two main classes: `EscapeGame`, which inherits from `tk.Tk`, and `GameState`, which is a regular Python class. Keeping rules separate from the display makes testing easier.

## 4. How the GUI works

`self.page` is the main Frame. `clear_page()` destroys its old children when changing screens. Menu, instructions, story and results use a centered card with `pack()`.

Gameplay uses `grid()` in `self.page`: header, room body, footer and feedback occupy separate rows. The header puts the room name on the left and the timer on the right. The body has a Canvas on the left and puzzle controls on the right. The footer always contains inventory and hint buttons.

Frames inside these regions use either `pack()` or `grid()`. Both can be used in one application, but they are never mixed for children of the same parent. Labels and Entry fields are real widgets, not Canvas text pretending to be controls.

The Canvas only draws room illustrations. `draw_scene()` draws at logical coordinates of 600 × 400, then scales and centers the shapes to fit the available space. A Configure event redraws only this scene when it resizes; it does not replace a typed answer.

Investigation panels are custom `Toplevel` windows. A modal grab prevents clicks behind the panel, while the countdown continues. Long evidence is displayed in a scrollable, read-only Text widget.

## 5. How button clicks work

A button stores a function in its `command` option. The function is passed without parentheses so Tkinter can call it later.

Actual example from `game.py`:

```python
self.button(card, 'START GAME', self.start_game, True).pack(pady=6)
```

`button()` creates a styled `ttk.Button`. `start_game()` runs when it is clicked.

Canvas objects use tags, such as `object_Book`. `bind_object()` attaches hover, leave and click handlers to every shape with that tag. Its small nested functions remember the object's name. The click handler calls `investigate(name)`.

For the final clue buttons, a default function argument remembers each loop index:

```python
def review(number=index):
    self.review_clue(number)
```

Without saving the index this way, every button could use the loop's last index.

## 6. How the countdown works

`GameState.start()` records `time.monotonic()` only when BEGIN is pressed. This clock measures elapsed time and is unaffected by ordinary system clock changes.

The remaining time is 600 seconds minus elapsed time. It is clamped to zero. On victory or defeat, `stop()` records a stop time, so results no longer change.

`EscapeGame.update_timer()` runs through one scheduled callback:

```python
self.job = self.after(100, self.update_timer)
```

`after()` schedules work and returns immediately. It does not sleep or block the interface. The callback checks real elapsed time rather than subtracting one for every callback. `display_time()` formats minutes and seconds and turns the timer red below one minute. `shutdown()` cancels the scheduled callback.

The clock starts in Room 1 and never restarts during room transitions. Investigation windows do not pause it. Solving the final lock freezes the escape result; OPEN DOOR then shows the victory screen.

## 7. How puzzles are validated

`check_answer()` reads the Entry and calls `self.state.submit(source.get())`. The state method returns a simple string such as `invalid`, `clues`, `wrong` or `correct`.

Numeric inputs are stripped of surrounding spaces and must contain the required number of ASCII digits. Invalid input does not use an attempt. Laboratory answers must be alphabetic; they are converted to uppercase. Each valid wrong answer increases that room's attempt count. The third one sets the lockdown reason and stops the clock.

Answers remain: Room 1 **462**, Room 2 **66**, Room 3 **ESCAPE**, Room 4 **466662**. The office safe also checks that all four clues were discovered. Opening the safe does not complete Room 2: the key must be collected and used at the exit.

## 8. How inventory is stored

`GameState.inventory` is a dictionary from item name to information. `journal` is a separate dictionary from clue title to clue text. Clicking the book calls `discover('Book')`, which adds its information to both dictionaries.

Dictionary keys are unique, so inspecting the same book twice does not duplicate it. The item indicator uses `len(self.state.inventory)`. The journal only displays discovered evidence. The Room 1 note and laboratory terminal are recorded when inspected.

`selected` stores the last selected object. Selected objects have a red border. Investigated office objects show green INSPECTED labels; other discovered objects have green borders when not selected.

## 9. How rooms change

`next_room()` calls `GameState.advance()`. It increases the room number only when the current room is in the `completed` set and time has not expired. Then `show_room()` builds the next room using the same state object.

The first unlocked door can be clicked to continue. The office requires the key at the exit. The laboratory has NEXT ROOM after success. The final room has an explicit OPEN DOOR button and a clickable unlocked door.

## 10. How the Caesar cipher works

Each uppercase letter is converted to a position from 0 to 25 using `ord()`. Subtracting three reverses the shift. `% 26` wraps negative positions around the alphabet. `chr()` converts the position back to a letter.

Actual code from `state.py`:

```python
position = ord(letter) - ord('A')
decoded += chr((position - shift) % 26 + ord('A'))
```

For example, H has position 7. Moving back three gives position 4, which is E. Therefore HVFDSH becomes ESCAPE. Nonletters are preserved by the decoding helper. The terminal panel and alphabet chart help the player understand the shift.

## 11. How the final code is calculated

Actual `master_code()` implementation:

```python
first = self.results[1]
return first[0] + self.results[2] + str(len(self.results[3])) + first[-2:]
```

`first[0]` gives **4**. The safe result gives **66**. `len('ESCAPE')` gives **6**, converted to text with `str()`. `first[-2:]` gives **62**. String concatenation produces **466662**. The final answer is derived from the stored results, rather than separately hardcoded.

## 12. How restart resets the game

`start_game()` calls `GameState.reset()` and displays the introduction. `reset()` clears inventory, journal, results, completed rooms, hints, attempt counts, key flags, start time, stop time and failure reason. It sets the room back to 1. The timer waits until BEGIN is clicked again.

## 13. Likely viva questions

1. **What is the aim?** Build an interactive desktop escape-room game with puzzles and a time limit.
2. **Which library builds the GUI?** Tkinter, with ttk for styled buttons and Entry fields.
3. **What does `mainloop()` do?** It processes user events and scheduled callbacks until the window closes.
4. **Why use classes?** To keep related game data and GUI methods together.
5. **Why separate `state.py` from `game.py`?** Game rules can be tested without creating a window.
6. **What is a callback?** A function Tkinter runs later, for example after a button click.
7. **Why pass a function without parentheses to `command`?** Parentheses would run it immediately instead of on click.
8. **What is a Canvas tag?** A name that groups drawn shapes so they can share event handlers.
9. **Why use Frames?** They group controls and give each screen a clear layout.
10. **How do you avoid overlapping widgets?** Use padded pack/grid regions and separate header, content, footer and feedback rows.
11. **Can pack and grid be used together?** In different parent Frames, yes; for children of the same parent, no.
12. **Why use `after()`?** It schedules the timer without blocking the GUI.
13. **Why avoid `time.sleep()`?** Sleeping in the GUI thread stops clicks, drawing and timer updates.
14. **Why use `time.monotonic()`?** It reliably measures elapsed time even if the wall clock changes.
15. **Does reading inventory pause the timer?** No. The same countdown continues while the panel is open.
16. **How are repeated clues handled?** Their dictionary key is reused, so duplicates are avoided.
17. **How do hints avoid repeated penalties?** Used room numbers are stored in a set; duplicates do not increase its size.
18. **Why use a set for completed rooms?** Each room should count as completed only once.
19. **How are invalid inputs handled?** They return `invalid` and do not increase attempts.
20. **How is Room 2 different?** The player must inspect all clues, open a safe, collect a key and use it at the exit.
21. **What does `% 26` do?** It wraps shifted letter positions inside the 26-letter alphabet.
22. **What is string slicing?** Selecting part of a string; `first[-2:]` selects its final two characters.
23. **What is the score formula?** 250 per completed room, minus 25 per wrong answer and 50 per hinted room, plus whole seconds left on victory; minimum zero.
24. **How do you stop duplicate countdowns?** Only `update_timer()` schedules its next call; starting a game does not start another loop.
25. **How is restart implemented?** Reset the existing game state and show the introduction again.
26. **Does this project need a database?** No. Dictionaries and sets store the current run in memory.
27. **How was it tested?** Standard unittest checks the rules; the GUI smoke script checks a full escape, failures, panels, input and window sizes.
28. **Why does a panel use a grab?** It keeps clicks inside that panel while normal timer callbacks continue.

## Demonstration order

Run `python main.py`. Show instructions, start a game, click the Room 1 note and solve its lock. In the office inspect all four clues, open the safe, collect the key and click the exit. Inspect the terminal and chart, decode the message, then review the four final clue buttons and solve the last lock. Click OPEN DOOR, show score and rank, then use PLAY AGAIN to demonstrate reset.

Run tests with `python -m unittest discover -s tests -v`. On a desktop, use `python tests/gui_smoke.py` for integration and layout checks.

## Startup compatibility check

Before importing the GUI, `main.py` checks the Python and Tk versions. Python 3.10+ and Tk 8.6+ are required. On this Mac, if the system's old Python/Tk is selected, the launcher uses `os.execv()` to replace that process with the already-installed modern Codex Python. This is a compatibility fallback, not another timer or GUI instance. On machines without that fallback, an unsupported runtime exits with setup instructions. The normal game still starts with `EscapeGame().mainloop()`.
