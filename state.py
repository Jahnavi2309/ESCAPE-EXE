"""Pure game rules, independent of Tkinter. Inject a clock for deterministic tests."""
import math
import time
from config import CLUES


def decode_caesar(text, shift=3):
    decoded = ''
    for letter in text.upper():
        if letter.isascii() and letter.isalpha():
            position = ord(letter) - ord('A')
            decoded += chr((position - shift) % 26 + ord('A'))
        else:
            decoded += letter
    return decoded


def rank(score):
    if score >= 1300:
        return 'MASTER ESCAPIST'
    elif score >= 1000:
        return 'EXPERT'
    elif score >= 750:
        return 'DETECTIVE'
    return 'SURVIVOR'


class GameState:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.reset()

    def reset(self):
        self.room = 1
        self.started = None
        self.stopped = None
        self.completed = set()
        self.attempts = {n: 0 for n in range(1, 5)}
        self.hints = set()
        self.inventory = {}
        self.journal = {}
        self.results = {}
        self.failure = None
        self.safe_open = False
        self.key_used = False

    def start(self):
        if self.started is None:
            self.started = self.clock()

    def remaining(self):
        if self.started is None:
            return 600.0
        return max(0.0, 600 - ((self.stopped if self.stopped is not None else self.clock()) - self.started))

    def stop(self):
        if self.stopped is None:
            self.stopped = self.clock()

    def check_time(self):
        if self.started is not None and self.remaining() <= 0 and not self.failure:
            self.failure = 'TIME HAS RUN OUT.'
            self.stop()
        return self.failure is None

    def discover(self, obj):
        title, detail = CLUES[obj]
        self.inventory[title] = {'Book': '47', 'Painting': '19'}.get(obj, detail)
        self.journal[title] = detail

    def hint(self):
        self.hints.add(self.room)

    def master_code(self):
        first = self.results[1]
        return first[0] + self.results[2] + str(len(self.results[3])) + first[-2:]

    def submit(self, value):
        if not self.check_time() or self.stopped is not None:
            return 'inactive'
        if self.room in self.completed or (self.room == 2 and self.safe_open):
            return 'solved'
        value = value.strip()
        length = {1: 3, 2: 2, 4: 6}.get(self.room)
        if self.room == 3:
            if not value or not value.isascii() or not value.isalpha():
                return 'invalid'
            value = value.upper()
        elif not value.isascii() or not value.isdigit() or len(value) != length:
            return 'invalid'
        if self.room == 2 and not all(title in self.inventory for title, _ in CLUES.values()):
            return 'clues'
        answer = {1: '462', 2: str(47 + 19), 3: decode_caesar('HVFDSH')}.get(self.room)
        if self.room == 4:
            answer = self.master_code()
        if value != answer:
            self.attempts[self.room] += 1
            if self.attempts[self.room] >= 3:
                self.failure = 'SECURITY LOCKDOWN INITIATED.'
                self.stop()
            return 'wrong'
        self.results[self.room] = value
        if self.room == 2:
            self.safe_open = True
        else:
            self.completed.add(self.room)
        if self.room == 1:
            self.inventory['First Door Code'] = value
        if self.room == 3:
            self.inventory['Decoded Message'] = value
        if self.room == 4:
            self.stop()
        return 'correct'

    def collect_key(self):
        if self.safe_open:
            self.inventory['Brass Key'] = 'A heavy brass key. Fits the office exit.'

    def use_key(self):
        if self.room == 2 and 'Brass Key' in self.inventory:
            self.key_used = True
            self.completed.add(2)
            return True
        return False

    def advance(self):
        if self.room in self.completed and self.room < 4 and self.check_time():
            self.room += 1
            return True
        return False

    @property
    def wrong(self):
        return sum(self.attempts.values())

    @property
    def score(self):
        bonus = math.floor(self.remaining()) if len(self.completed) == 4 else 0
        return max(0, 250 * len(self.completed) - 25 * self.wrong - 50 * len(self.hints) + bonus)
