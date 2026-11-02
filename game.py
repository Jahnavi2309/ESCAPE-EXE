"""Tkinter layout and room interactions; puzzle rules live in state.py."""
import math
import tkinter as tk
from tkinter import ttk
from config import BG, PANEL, BUTTON, RED, MUTED, TEXT, GREEN, TITLES, HINTS, CLUES
from state import GameState, rank

STORY = ('You wake up in an unfamiliar room.\nThe door is locked.\n\n'
         'A distorted voice speaks through an old speaker.\n“You have ten minutes.”\n\n'
         'Four rooms. Four puzzles.\nEvery answer brings you closer to freedom.\n'
         'Every mistake costs you time.\n\nFind the clues. Break the locks.\n\nESCAPE.')
RIDDLE = ('I am a three-digit number.\n\nMy digits add up to 12.\n'
          'My first digit is 4.\nMy last digit is 2.\n\nWhat number am I?')
FINAL_CLUES = ['First digit of the first door’s code', 'Complete detective safe combination',
               'Number of letters in the decoded word', 'Last two digits of the first door’s code']


class EscapeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('ESCAPE.EXE — The Last 10 Minutes')
        self.geometry('1100x720')
        self.minsize(1000, 680)
        self.configure(bg=BG)
        self.state = GameState()
        self.screen = 'menu'
        self.modal = None
        self.entry = None
        self.safe_entry = None
        self.canvas = None
        self.selected = ''
        self.job = None
        self.feedback = tk.StringVar()
        self.item_count = tk.StringVar()
        self.attempt_text = tk.StringVar()
        self.object_name = tk.StringVar(value='Click an object to investigate.')
        self.setup_styles()
        self.page = tk.Frame(self, bg=BG, padx=24, pady=20)
        self.page.pack(fill='both', expand=True)
        self.bind('<Return>', self.on_enter)
        self.bind('<Escape>', self.close_modal)
        self.protocol('WM_DELETE_WINDOW', self.shutdown)
        self.show_menu()
        self.update_timer()

    def setup_styles(self):
        # Clam lets the same button colors work on macOS, Windows and Linux.
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('TkDefaultFont', 11), padding=(12, 7),
                        background=BUTTON, foreground=TEXT, borderwidth=0)
        style.map('Game.TButton', background=[('active', '#333A48'), ('disabled', PANEL)],
                  foreground=[('disabled', MUTED)])
        style.configure('Accent.TButton', background=RED)
        style.map('Accent.TButton', background=[('active', '#B92D3A')])
        style.configure('Game.TEntry', fieldbackground=BG, foreground=TEXT,
                        insertcolor=TEXT, padding=8)

    def label(self, parent, text='', size=12, color=TEXT, **options):
        return tk.Label(parent, text=text, font=('TkDefaultFont', size), bg=parent['bg'],
                        fg=color, **options)

    def button(self, parent, text, command, accent=False, width=24):
        return ttk.Button(parent, text=text, command=command, width=width,
                          style='Accent.TButton' if accent else 'Game.TButton')

    def clear_page(self, screen):
        self.close_modal()
        for widget in self.page.winfo_children():
            widget.destroy()
        self.screen = screen
        self.entry = None
        self.canvas = None
        self.feedback.set('')

    def centered_card(self, title, subtitle):
        card = tk.Frame(self.page, bg=PANEL, padx=36, pady=28)
        card.pack(expand=True)
        self.label(card, title, 30, RED).pack(pady=(0, 8))
        self.label(card, subtitle, 12, MUTED).pack(pady=(0, 24))
        return card

    def show_menu(self):
        self.clear_page('menu')
        card = self.centered_card('ESCAPE.EXE', 'THE LAST 10 MINUTES')
        self.label(card, 'Every clue has a meaning. Every second has a price.',
                   13, MUTED).pack(pady=(0, 28))
        self.button(card, 'START GAME', self.start_game, True).pack(pady=6)
        self.button(card, 'HOW TO PLAY', self.show_instructions).pack(pady=6)
        self.button(card, 'EXIT', self.shutdown).pack(pady=6)
        self.label(card, 'Version 1.1 • Offline mystery game', 10, MUTED).pack(pady=(24, 0))

    def show_instructions(self):
        self.clear_page('help')
        card = self.centered_card('HOW TO PLAY', 'Explore. Connect the evidence. Escape.')
        instructions = (
            'Click labeled objects to investigate; green marks mean already inspected.\n'
            'Read the note in Room 1 and inspect every office clue in Room 2.\n'
            'Type an answer and press Enter or CHECK ANSWER.\n'
            'Open the safe, collect its key, and click the office exit to use it.\n'
            'Use INVENTORY to review recovered items and journal entries.\n'
            'HINT costs 50 points once per room; repeat views are free.\n'
            'Three wrong valid answers in one room cause lockdown.\n'
            'The ten-minute clock continues while reading investigation panels.\n'
            'A completed room earns 250 points; a wrong answer costs 25.\n'
            'A successful escape earns one point per full second remaining.\n'
            'Click OPEN DOOR after solving the final lock.\n'
            'Press Esc or CLOSE to dismiss an investigation panel.')
        self.label(card, instructions, 12, justify='left', wraplength=750,
                   anchor='w').pack(pady=(0, 22))
        self.button(card, 'MAIN MENU', self.show_menu).pack()

    def start_game(self):
        self.state.reset()
        self.selected = ''
        self.clear_page('intro')
        card = self.centered_card('AN UNKNOWN ROOM', 'The countdown begins when you click BEGIN.')
        self.label(card, STORY, 13, justify='center', wraplength=700).pack(pady=(0, 24))
        self.button(card, 'BEGIN', self.begin, True).pack()

    def begin(self):
        self.state.start()
        self.show_room()

    def show_room(self):
        self.clear_page('room')
        self.selected = ''
        header = tk.Frame(self.page, bg=BG)
        self.page.columnconfigure(0, weight=1)
        self.page.rowconfigure(1, weight=1)
        header.grid(row=0, column=0, sticky='ew', pady=(0, 14))
        header.columnconfigure(0, weight=1)
        self.label(header, TITLES[self.state.room-1], 22, anchor='w').grid(row=0, column=0, sticky='w')
        self.label(header, f'ROOM {self.state.room} OF 4', 10, MUTED).grid(row=1, column=0, sticky='w', pady=(5, 0))
        timer_box = tk.Frame(header, bg=BG)
        timer_box.grid(row=0, column=1, rowspan=2, sticky='e')
        self.label(timer_box, 'TIME REMAINING', 9, MUTED).pack(anchor='e')
        self.timer_label = self.label(timer_box, '', 25)
        self.timer_label.pack(anchor='e')

        body = tk.Frame(self.page, bg=BG)
        body.grid(row=1, column=0, sticky='nsew')
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, minsize=350)
        scene_panel = tk.Frame(body, bg=PANEL, padx=12, pady=12)
        scene_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 18))
        self.label(scene_panel, 'EXPLORE THE ROOM', 10, MUTED).pack(pady=(0, 8))
        self.canvas = tk.Canvas(scene_panel, bg=PANEL, highlightthickness=0, width=500, height=300)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', self.draw_scene)
        self.label(scene_panel, textvariable=self.object_name, size=10, color=MUTED,
                   wraplength=470).pack(pady=(8, 0))
        self.controls = tk.Frame(body, bg=PANEL, padx=20, pady=14)
        self.controls.grid(row=0, column=1, sticky='nsew')
        self.controls.columnconfigure(0, weight=1)
        self.controls.rowconfigure(1, weight=1)
        self.label(self.controls, textvariable=self.attempt_text, size=10,
                   color=MUTED).grid(row=0, column=0, pady=(0, 12))
        self.puzzle = tk.Frame(self.controls, bg=PANEL)
        self.puzzle.grid(row=1, column=0, sticky='nsew')
        self.action_area = tk.Frame(self.controls, bg=PANEL)
        self.action_area.grid(row=2, column=0, sticky='ew', pady=(12, 0))
        self.show_puzzle()
        self.show_actions()

        footer = tk.Frame(self.page, bg=BG)
        footer.grid(row=2, column=0, sticky='ew', pady=(12, 0))
        self.button(footer, 'INVENTORY', self.open_inventory, width=18).pack(side='left')
        self.button(footer, 'HINT', self.show_hint, width=12).pack(side='left', padx=(12, 0))
        self.label(footer, textvariable=self.item_count, size=11, color=MUTED).pack(side='right')
        self.status_label = self.label(self.page, textvariable=self.feedback, size=11,
                                       color=MUTED, wraplength=900, height=1)
        self.status_label.grid(row=3, column=0, sticky='ew', pady=(6, 0))
        self.refresh_indicators()
        self.display_time()

    def show_puzzle(self):
        room = self.state.room
        if room == 1:
            self.label(self.puzzle, 'THE DOOR LOCK', 16).pack(pady=(6, 16))
            if 'Wall Note' in self.state.journal:
                text = RIDDLE
            else:
                text = 'A folded note is pinned to the wall.\n\nClick the note to reveal the riddle.'
            self.label(self.puzzle, text, 13, wraplength=300, justify='center').pack(expand=True)
        elif room == 2:
            self.label(self.puzzle, 'FOLLOW THE EVIDENCE', 16).pack(pady=(6, 16))
            self.label(self.puzzle, 'Inspect the book, painting, desk and cabinet.\n\n'
                       'Their clues reveal the safe combination.\n\n'
                       'Collect the key inside, then click the exit.', 13,
                       wraplength=300).pack(expand=True)
            self.clue_count = self.label(self.puzzle, '', 12, GREEN)
            self.clue_count.pack(pady=16)
        elif room == 3:
            self.label(self.puzzle, 'DECODE THE TERMINAL', 16).pack(pady=(6, 16))
            self.label(self.puzzle, 'HVFDSH', 26, GREEN).pack(pady=10)
            self.label(self.puzzle, 'Letters were shifted three places forward.\n\n'
                       'Shift backward to decode.\nClick the terminal to inspect it.',
                       12, wraplength=300).pack(expand=True)
            self.button(self.puzzle, 'ALPHABET REFERENCE', self.cipher_panel).pack(pady=(12, 0))
        else:
            self.label(self.puzzle, 'THE FINAL LOCK', 16).pack(pady=(0, 8))
            self.label(self.puzzle, 'Review the clues. Join all four parts.',
                       12, MUTED).pack(pady=(0, 12))
            categories = ['1 / FIRST DOOR: FIRST DIGIT', '2 / SAFE COMBINATION',
                          '3 / DECODED WORD LENGTH', '4 / FIRST DOOR: LAST TWO']
            for index, category in enumerate(categories):
                def review(number=index):
                    self.review_clue(number)
                self.button(self.puzzle, category, review).pack(fill='x', pady=3)

    def show_actions(self):
        # Replace only the answer controls; the room and evidence remain visible.
        for widget in self.action_area.winfo_children():
            widget.destroy()
        self.entry = None
        room = self.state.room
        if room in self.state.completed:
            self.label(self.action_area, 'ACCESS GRANTED', 14, GREEN).pack(pady=(0, 10))
            if room == 4:
                self.button(self.action_area, 'OPEN DOOR', self.finish_game, True).pack(fill='x')
            else:
                self.button(self.action_area, 'NEXT ROOM', self.next_room, True).pack(fill='x')
        elif room == 2:
            if self.state.safe_open and 'Brass Key' not in self.state.inventory:
                self.button(self.action_area, 'COLLECT KEY', self.collect_key, True).pack(fill='x')
            elif 'Brass Key' in self.state.inventory:
                self.label(self.action_area, 'Key collected. Click the exit.', 12, GREEN).pack(pady=12)
            else:
                self.button(self.action_area, 'INSPECT SAFE', self.inspect_safe).pack(fill='x')
        else:
            title = 'DECODED WORD' if room == 3 else ('SIX-DIGIT CODE' if room == 4 else 'THREE-DIGIT CODE')
            self.label(self.action_area, title, 10, MUTED).pack(pady=(0, 8))
            self.entry = ttk.Entry(self.action_area, font=('TkFixedFont', 20), justify='center',
                                   style='Game.TEntry', width=12)
            self.entry.pack(fill='x', pady=(0, 10))
            self.button(self.action_area, 'CHECK ANSWER', self.check_answer, True).pack(fill='x')
            self.entry.focus_set()

    def refresh_indicators(self):
        self.item_count.set(f'ITEMS COLLECTED: {len(self.state.inventory)}')
        self.attempt_text.set(f'ATTEMPTS REMAINING: {3-self.state.attempts[self.state.room]} / 3')
        if self.screen == 'room' and self.state.room == 2:
            count = sum(title in self.state.journal for title, detail in CLUES.values())
            self.clue_count.configure(text=f'CLUES INVESTIGATED: {count} / 4')

    def notify(self, message, success=False):
        self.feedback.set(message)
        self.status_label.configure(fg=GREEN if success else MUTED)

    def on_enter(self, event):
        if self.screen == 'room' and (self.modal is None or self.safe_entry is not None):
            self.check_answer()
        return 'break'

    def active_game(self):
        if self.screen != 'room':
            return False
        if not self.state.check_time():
            self.end_game()
            return False
        return True

    def check_answer(self):
        if not self.active_game():
            return
        source = self.safe_entry if self.state.room == 2 else self.entry
        if source is None:
            return
        result = self.state.submit(source.get())
        if self.state.failure:
            self.end_game()
            return
        self.refresh_indicators()
        if result == 'correct':
            self.close_modal()
            self.show_actions()
            self.draw_scene()
            message = 'Correct! Door unlocked.'
            if self.state.room == 2:
                message = 'Safe unlocked. Collect the key inside.'
                self.inspect_safe()
            elif self.state.room == 3:
                message = 'ACCESS GRANTED. Decoded message saved for the final lock.'
            elif self.state.room == 4:
                message = 'ACCESS GRANTED. Click OPEN DOOR to escape.'
            self.notify(message, True)
        else:
            if result == 'invalid':
                lengths = {1: 3, 2: 2, 4: 6}
                if self.state.room == 3:
                    message = 'Enter a word using letters A–Z.'
                else:
                    message = f'Enter exactly {lengths[self.state.room]} digits.'
            elif result == 'clues':
                message = 'Investigate all four office clues first.'
            elif result == 'wrong':
                left = 3-self.state.attempts[self.state.room]
                message = f'ACCESS DENIED. Incorrect answer. {left} attempts remaining.'
            else:
                return
            self.notify(message)
            if self.safe_entry is not None:
                self.modal_feedback.configure(text=message)

    def next_room(self):
        if self.active_game() and self.state.advance():
            self.show_room()

    def finish_game(self):
        if self.screen == 'room' and 4 in self.state.completed:
            self.end_game(victory=True)

    def end_game(self, victory=False):
        self.clear_page('victory' if victory else 'defeat')
        card = self.centered_card('ESCAPE SUCCESSFUL' if victory else 'GAME OVER',
                                  'You made it outside.' if victory else self.state.failure)
        seconds = math.ceil(self.state.remaining())
        stats = [('Rooms completed', f'{len(self.state.completed)} / 4'),
                 ('Last reached room', f'{self.state.room} / {TITLES[self.state.room-1]}'),
                 ('Time remaining', f'{seconds//60:02}:{seconds%60:02}'),
                 ('Wrong attempts', str(self.state.wrong)), ('Hints used', str(len(self.state.hints))),
                 ('Final score', str(self.state.score))]
        if victory:
            stats.append(('Rank', rank(self.state.score)))
        table = tk.Frame(card, bg=PANEL)
        table.pack(fill='x', pady=(0, 20))
        for row, (name, value) in enumerate(stats):
            self.label(table, name, 12, MUTED).grid(row=row, column=0, sticky='w', padx=(0, 32), pady=7)
            self.label(table, value, 12).grid(row=row, column=1, sticky='e', pady=7)
        table.columnconfigure(1, weight=1)
        self.button(card, 'PLAY AGAIN' if victory else 'TRY AGAIN', self.start_game, True).pack(pady=6)
        self.button(card, 'MAIN MENU', self.show_menu).pack(pady=6)

    def display_time(self):
        seconds = math.ceil(self.state.remaining())
        self.timer_label.configure(text=f'{seconds//60:02}:{seconds%60:02}',
                                   fg=RED if seconds < 60 else TEXT)

    def update_timer(self):
        # One callback owns the clock. It measures real elapsed time, not callback counts.
        if self.screen == 'room':
            if self.state.check_time():
                self.display_time()
            else:
                self.end_game()
        self.job = self.after(100, self.update_timer)

    def shutdown(self):
        if self.job is not None:
            self.after_cancel(self.job)
        self.close_modal()
        self.destroy()

    def popup(self, title, body, actions=None, input_field=False):
        self.close_modal()
        panel = tk.Toplevel(self, bg=PANEL, padx=24, pady=20)
        self.modal = panel
        panel.title(title)
        panel.transient(self)
        panel.resizable(False, False)
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width()-620)//2
        y = self.winfo_rooty() + (self.winfo_height()-470)//2
        panel.geometry(f'620x470+{max(0, x)}+{max(0, y)}')
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.label(panel, title, 19, RED).grid(row=0, column=0, pady=(0, 18))
        content = tk.Frame(panel, bg=PANEL)
        content.grid(row=1, column=0, sticky='nsew')
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        # Scrollable text gives long journal entries a fixed, bounded area.
        text = tk.Text(content, font=('TkFixedFont', 12), wrap='word', bg=PANEL,
                       fg=TEXT, relief='flat', highlightthickness=0, width=50, height=6)
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(content, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        text.configure(yscrollcommand=scrollbar.set)
        text.insert('1.0', body)
        text.configure(state='disabled')
        self.modal_feedback = self.label(panel, '', 11, RED, wraplength=560)
        self.modal_feedback.grid(row=2, column=0, sticky='ew', pady=6)
        controls = tk.Frame(panel, bg=PANEL)
        controls.grid(row=3, column=0, sticky='ew')
        if input_field:
            self.safe_entry = ttk.Entry(controls, font=('TkFixedFont', 20),
                                        justify='center', style='Game.TEntry')
            self.safe_entry.pack(fill='x', pady=(0, 10))
        for title, command in actions or []:
            self.button(controls, title, command, True).pack(fill='x', pady=4)
        self.button(controls, 'CLOSE [ESC]', self.close_modal).pack(fill='x', pady=(6, 0))
        panel.protocol('WM_DELETE_WINDOW', self.close_modal)
        panel.bind('<Escape>', self.close_modal)
        panel.bind('<Return>', self.on_enter)
        # A grab prevents clicks behind the panel; after() still updates the clock.
        panel.grab_set()
        if self.safe_entry is not None:
            self.safe_entry.focus_set()
        else:
            panel.focus_set()

    def close_modal(self, event=None):
        if self.modal is not None:
            self.modal.grab_release()
            self.modal.destroy()
            self.modal = None
        self.safe_entry = None
        if self.entry is not None and self.entry.winfo_exists():
            self.entry.focus_set()

    def open_inventory(self):
        if not self.active_game():
            return
        sections = ['ITEMS']
        for name, value in self.state.inventory.items():
            sections.append(f'{name}: {value}')
        if not self.state.inventory:
            sections.append('No items collected yet.')
        sections.append('JOURNAL')
        for name, detail in self.state.journal.items():
            sections.append(f'{name}\n{detail}')
        if not self.state.journal:
            sections.append('Click objects to record clues.')
        self.popup('INVENTORY / JOURNAL', '\n\n'.join(sections))

    def show_hint(self):
        if not self.active_game():
            return
        self.state.hint()
        self.popup('ROOM HINT', HINTS[self.state.room-1] + '\n\n'
                   'Cost: 50 points on first use in this room. Repeat views are free.')

    def cipher_panel(self):
        if not self.active_game():
            return
        self.popup('ALPHABET REFERENCE',
                   'Move each encrypted letter three places backward.\n\n'
                   'ENCRYPTED  D E F G H I J K L M N O P\n'
                   'DECODED    A B C D E F G H I J K L M\n\n'
                   'ENCRYPTED  Q R S T U V W X Y Z A B C\n'
                   'DECODED    N O P Q R S T U V W X Y Z\n\n'
                   'Example: H becomes E. The alphabet wraps at A.')

    def review_clue(self, number):
        if not self.active_game() or self.state.room != 4:
            return
        first = self.state.results[1]
        safe = self.state.results[2]
        word = self.state.results[3]
        details = [f'First door code: {first}\nUse its first digit.',
                   f'Detective safe combination: {safe}\nUse the complete combination.',
                   f'Decoded message: {word}\nCount its letters.',
                   f'First door code: {first}\nUse its final two digits.']
        self.popup(f'CLUE {number+1}', FINAL_CLUES[number] + '\n\n' + details[number])

    def investigate(self, name):
        if not self.active_game():
            return
        self.selected = name
        if name in CLUES:
            title, detail = CLUES[name]
            is_new = title not in self.state.journal
            self.state.discover(name)
            self.refresh_indicators()
            self.draw_scene()
            self.notify('New clue discovered!' if is_new else 'Clue already recorded in your journal.', is_new)
            self.popup(name.upper(), detail)
        elif name == 'Note':
            self.state.journal['Wall Note'] = RIDDLE
            for widget in self.puzzle.winfo_children():
                widget.destroy()
            self.show_puzzle()
            self.draw_scene()
            self.notify('Riddle added to your journal.', True)
            self.popup('THE WALL NOTE', RIDDLE)
        elif name == 'Safe':
            self.draw_scene()
            self.inspect_safe()
        elif name == 'Exit':
            if self.state.use_key():
                self.refresh_indicators()
                self.show_actions()
                self.draw_scene()
                self.notify('Exit unlocked. The brass key fits.', True)
                self.popup('EXIT UNLOCKED', 'A laboratory lies beyond the door.', [('NEXT ROOM', self.next_room)])
            else:
                self.notify('You need to collect the key first.')
                self.popup('EXIT LOCKED', 'Find the brass key inside the safe and collect it first.')
        elif name == 'Terminal':
            detail = 'HVFDSH\n\nEvery letter was shifted three positions forward. Reverse the shift to decode the word.'
            self.state.journal['Laboratory Terminal'] = detail
            self.draw_scene()
            self.popup('COMPUTER TERMINAL', detail, [('ALPHABET REFERENCE', self.cipher_panel)])
        elif name == 'Door':
            if self.state.room in self.state.completed:
                if self.state.room == 4:
                    self.finish_game()
                else:
                    self.next_room()
            else:
                self.notify('The door is locked. Solve the code first.')

    def inspect_safe(self):
        if not self.active_game() or self.state.room != 2:
            return
        if self.state.safe_open:
            if 'Brass Key' in self.state.inventory:
                self.popup('SAFE OPEN', 'The key has been collected. Use it on the exit.')
            else:
                self.popup('SAFE OPEN', 'A brass key rests inside.', [('COLLECT KEY', self.collect_key)])
        else:
            self.popup('SAFE COMBINATION', 'Find the connection between all four office clues.\nEnter a two-digit combination.',
                       [('UNLOCK SAFE', self.check_answer)], input_field=True)

    def collect_key(self):
        if not self.active_game():
            return
        self.state.collect_key()
        self.close_modal()
        self.refresh_indicators()
        self.show_actions()
        self.draw_scene()
        self.notify('Key added to inventory. Click the exit to use it.', True)

    def object_color(self, name):
        if name == self.selected:
            return RED
        if name in CLUES and CLUES[name][0] in self.state.journal:
            return GREEN
        if name == 'Note' and 'Wall Note' in self.state.journal:
            return GREEN
        if name == 'Terminal' and 'Laboratory Terminal' in self.state.journal:
            return GREEN
        return '#657080'

    def bind_object(self, name):
        # All shapes in an object share one tag and the same three event handlers.
        tag = 'object_' + name
        def enter(event):
            self.canvas.configure(cursor='hand2')
            self.canvas.itemconfigure('border_' + name, outline=RED, width=3)
            self.object_name.set('Inspect ' + name)
        def leave(event):
            self.canvas.configure(cursor='')
            self.canvas.itemconfigure('border_' + name, outline=self.object_color(name), width=2)
            self.object_name.set('Green = investigated. Red = selected. Click to explore.')
        def click(event):
            self.investigate(name)
        self.canvas.tag_bind(tag, '<Enter>', enter)
        self.canvas.tag_bind(tag, '<Leave>', leave)
        self.canvas.tag_bind(tag, '<Button-1>', click)

    def box(self, name, x, y, width, height, color=BUTTON):
        tags = ('object_' + name, 'border_' + name)
        self.canvas.create_rectangle(x, y, x+width, y+height, fill=color,
                                     outline=self.object_color(name), width=2, tags=tags)

    def scene_text(self, name, x, y, text, color=TEXT, size=11):
        self.canvas.create_text(x, y, text=text, fill=color, font=('TkDefaultFont', size),
                                tags='object_' + name)

    def draw_scene(self, event=None):
        if self.canvas is None or not self.canvas.winfo_exists():
            return
        c = self.canvas
        c.delete('all')
        c.configure(cursor='')
        self.object_name.set('Green = investigated. Red = selected. Click to explore.')
        # Scenery alone uses a 600 × 400 logical drawing area, scaled to fit.
        c.create_line(15, 330, 585, 330, fill='#343B48')
        room = self.state.room
        if room in (1, 4):
            unlocked = room in self.state.completed
            indicator = GREEN if unlocked else RED
            self.box('Door', 205, 45, 200, 280, '#242A34')
            c.create_line(305, 48, 305, 322, fill='#495361', tags='object_Door')
            for y in range(80, 285, 42):
                c.create_line(220, y, 390, y, fill='#343D4B', tags='object_Door')
            c.create_rectangle(250, 20, 360, 28, fill=indicator, outline='', tags='object_Door')
            self.scene_text('Door', 305, 170, 'UNLOCKED' if unlocked else 'LOCKED', indicator, 16)
            self.scene_text('Door', 305, 205, 'Click to continue' if unlocked else 'Security door', MUTED)
            self.box('Door', 435, 130, 70, 110)
            self.scene_text('Door', 470, 150, 'LOCK', indicator)
            for i in range(9):
                x, y = 447+(i%3)*16, 174+(i//3)*18
                c.create_rectangle(x, y, x+8, y+8, fill=indicator, outline='', tags='object_Door')
            if room == 1:
                self.box('Note', 40, 120, 100, 135, '#B5AA8D')
                for y in range(148, 212, 15):
                    c.create_line(55, y, 124, y, fill='#645E50', tags='object_Note')
                self.scene_text('Note', 90, 235, 'NOTE', '#252A35')
                self.bind_object('Note')
            self.bind_object('Door')
        elif room == 2:
            self.box('Book', 25, 35, 140, 150, '#43372D')
            for i in range(7):
                x = 38+i*16
                c.create_rectangle(x, 51+(i%2)*8, x+11, 116,
                                   fill=['#7C4250', '#596775', '#8B7F5C'][i%3], outline='', tags='object_Book')
            c.create_line(28, 124, 162, 124, fill='#85705C', tags='object_Book')
            self.scene_text('Book', 95, 155, 'BOOK')
            self.box('Painting', 215, 35, 130, 112, '#65503D')
            c.create_polygon(226, 122, 265, 59, 333, 122, fill='#394651', tags='object_Painting')
            self.scene_text('Painting', 280, 164, 'PAINTING')
            self.box('Desk', 25, 245, 180, 40, '#71503A')
            for x in (38, 177):
                c.create_rectangle(x, 285, x+14, 330, fill='#4B382C', outline='', tags='object_Desk')
            c.create_rectangle(95, 218, 140, 243, fill='#C4B89D', tags='object_Desk')
            self.scene_text('Desk', 115, 266, 'DESK')
            self.box('Cabinet', 440, 195, 120, 135, '#3D4651')
            for y in (210, 249, 288):
                c.create_rectangle(451, y, 549, y+29, outline='#697482', tags='object_Cabinet')
                c.create_line(486, y+12, 514, y+12, fill=MUTED, width=3, tags='object_Cabinet')
            self.scene_text('Cabinet', 500, 351, 'CABINET')
            self.box('Safe', 245, 220, 125, 110, '#2C333E')
            if self.state.safe_open:
                self.scene_text('Safe', 307, 241, 'SAFE OPEN', GREEN)
                if 'Brass Key' not in self.state.inventory:
                    c.create_oval(270, 268, 290, 288, outline='#D9BB75', width=4, tags='object_Safe')
                    c.create_line(290, 278, 340, 278, fill='#D9BB75', width=4, tags='object_Safe')
                    c.create_line(327, 278, 327, 290, fill='#D9BB75', width=4, tags='object_Safe')
                else:
                    self.scene_text('Safe', 307, 285, 'EMPTY', MUTED)
            else:
                c.create_oval(285, 236, 331, 282, outline=MUTED, width=3, tags='object_Safe')
                self.scene_text('Safe', 307, 309, 'SAFE')
            self.box('Exit', 450, 25, 100, 130)
            self.scene_text('Exit', 500, 84, 'EXIT', GREEN if self.state.key_used else MUTED)
            for name in ('Book', 'Painting', 'Desk', 'Cabinet', 'Safe', 'Exit'):
                self.bind_object(name)
                if name in CLUES and CLUES[name][0] in self.state.journal:
                    self.scene_text(name, {'Book':95, 'Painting':280, 'Desk':115, 'Cabinet':500}[name],
                                    {'Book':202, 'Painting':187, 'Desk':350, 'Cabinet':375}[name], 'INSPECTED', GREEN, 9)
        else:
            c.create_rectangle(55, 285, 545, 300, fill='#414A58', outline='')
            c.create_rectangle(80, 300, 95, 350, fill='#303744', outline='')
            c.create_rectangle(505, 300, 520, 350, fill='#303744', outline='')
            self.box('Terminal', 150, 65, 300, 180, '#101A20')
            self.scene_text('Terminal', 300, 100, 'LAB / TERMINAL 03', MUTED)
            solved = 3 in self.state.completed
            self.scene_text('Terminal', 300, 152, 'ESCAPE' if solved else 'HVFDSH', GREEN, 26)
            self.scene_text('Terminal', 300, 207, 'ACCESS GRANTED' if solved else 'Click to inspect', GREEN if solved else MUTED)
            c.create_rectangle(287, 245, 313, 284, fill='#414A58', tags='object_Terminal')
            for x in (70, 485):
                c.create_polygon(x, 229, x+10, 229, x+10, 250, x+25, 280, x-15, 280, x, 250,
                                 fill='#255349', outline=GREEN)
            self.bind_object('Terminal')
        width, height = max(1, c.winfo_width()), max(1, c.winfo_height())
        scale = min(width/600, height/400)
        c.scale('all', 0, 0, scale, scale)
        c.move('all', (width-600*scale)/2, (height-400*scale)/2)
