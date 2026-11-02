"""Shared visual theme and puzzle configuration."""
BG = '#0D0F14'
PANEL = '#181B23'
RED = '#D93645'
MUTED = '#A0A6B0'
TEXT = '#F5F5F5'
GREEN = '#40C98B'
BUTTON = '#252A35'
TITLES = ['THE LOCKED ROOM', "DETECTIVE’S OFFICE", 'SECRET LABORATORY', 'FINAL CHAMBER']
HINTS = [
    'Find the middle digit by subtracting the known digits from 12.',
    'The book and painting reveal two numbers. The desk and cabinet suggest what to do with them.',
    'To reverse the encryption, move each letter three positions backward. H becomes E.',
    'The four parts contain 1 digit, 2 digits, 1 digit, and 2 digits. Join them in that order.'
]
CLUES = {
    'Book': ('Missing Book Page', 'Page 47 has been torn out. The remaining pages appear untouched.'),
    'Painting': ('Painting Number', 'Behind the painting, you discover a number scratched into the wall: 19.'),
    'Desk': ('Desk Note', 'A note reads: The missing page and the hidden number must become one.'),
    'Cabinet': ('Cabinet File', 'Old case files cover the shelves. One file says: Addition opens what force cannot.')
}
