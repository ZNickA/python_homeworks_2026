import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from final_project.console import run


if __name__ == '__main__':
    raise SystemExit(run())
