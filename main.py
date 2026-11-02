"""Start the game with Python 3.10+ and a supported Tk installation."""
import os
from pathlib import Path
import sys


def check_runtime():
    """Avoid Apple's legacy Tk, which can produce a blank window on recent macOS."""
    try:
        import tkinter
        tk_version = tkinter.TkVersion
    except ImportError:
        tk_version = 0
    if sys.version_info >= (3, 10) and tk_version >= 8.6:
        return

    # This Mac already has a modern Python supplied by the Codex desktop app.
    # Other computers can run normally with their own modern Python installation.
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    if sys.platform == 'darwin' and bundled.is_file() and bundled.resolve() != Path(sys.executable).resolve():
        print('The selected Python/Tk is outdated. Launching with the installed modern Python.',
              file=sys.stderr, flush=True)
        os.execv(str(bundled), [str(bundled), str(Path(__file__).resolve())] + sys.argv[1:])

    raise SystemExit('ESCAPE.EXE needs Python 3.10+ with Tk 8.6 or newer. '
                     'Select a current Python installation in VS Code. '
                     'The older Apple Python/Tk can show a blank window.')


if __name__ == '__main__':
    check_runtime()
    from game import EscapeGame
    EscapeGame().mainloop()
