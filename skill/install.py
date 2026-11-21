#!/usr/bin/env python3
"""Install the public Momentum skill using Python 3 stdlib only."""
import argparse
import pathlib
import tempfile
from urllib.parse import urljoin
from urllib.request import urlopen

FILES = ('SKILL.md', 'references/routing.md', 'references/recipes.md')
DEFAULT_SOURCE = 'https://raw.githubusercontent.com/neoskx/Momentum/main/skill/'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('agent', choices=['claude', 'codex'])
    parser.add_argument('--base-url', default=DEFAULT_SOURCE)
    parser.add_argument('--dest', type=pathlib.Path)
    args = parser.parse_args()
    dest = args.dest or pathlib.Path.home() / ('.claude' if args.agent == 'claude' else '.codex') / 'skills/momentum'
    if any(p.is_symlink() for p in (dest, *dest.parents)):
        raise ValueError('installation destination must not contain symlinks')
    # Fetch everything before replacing any installed file.
    with tempfile.TemporaryDirectory(prefix='momentum-install-') as tmp:
        stage = pathlib.Path(tmp)
        for name in FILES:
            with urlopen(urljoin(args.base_url.rstrip('/') + '/', name), timeout=60) as response:
                data = response.read()
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for name in FILES:
            target = dest / name
            if target.is_symlink() or any(p.is_symlink() for p in target.parents):
                raise ValueError('installation destination must not contain symlinks')
        for name in FILES:
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((stage / name).read_bytes())
    print(f'Installed momentum to {dest}')


if __name__ == '__main__':
    main()
