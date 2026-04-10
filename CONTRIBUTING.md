# Contributing

Thanks for your interest in `play-store-screenshots`. This guide covers how the repo is organized, how to run the tests, and the conventions contributions are expected to follow.

## Repository layout

```
play-store-screenshots/
├── SKILL.md                          # Main instruction file Claude reads
├── mockup.png                        # Pre-measured Pixel 8 Pro frame (1022×2148)
├── README.md                         # GitHub landing page
├── LICENSE                           # MIT
├── CONTRIBUTING.md                   # This file
├── .gitignore
├── .github/workflows/test.yml        # CI — runs pytest on push/PR
└── scripts/
    ├── generate_mockup.py            # Python/PIL script that produces mockup.png
    └── test_generate_mockup.py       # pytest tests verifying mockup.png
```

## Making changes

### Editing `SKILL.md`

`SKILL.md` is the file Claude reads on every skill invocation. It must stay internally consistent and should be edited with the same care you'd give production code:

- Keep the 10 top-level sections in their current order (`Overview`, `Core Principle`, `Step 1`–`Step 7`, `Common Mistakes`).
- Embedded TypeScript/TSX code examples must compile when copy-pasted into a Next.js project.
- The Phone Mockup Component constants (`MK_W`, `MK_H`, `SC_L`, `SC_T`, `SC_W`, `SC_H`, `SC_RX`, `SC_RY`) are a **source of truth mirror** of the Python generator. If you change any of these, you must also update `scripts/generate_mockup.py` and re-run the mockup generator and tests.
- The `alpha: false` option on `getContext("2d")` inside `flattenToRgb` is load-bearing — without it, Play Store rejects every exported PNG with `IMAGE_ALPHA_NOT_ALLOWED`. Don't remove it.
- The Phone component uses `img("/mockup.png")` (the pre-loaded data-URI helper) rather than a raw path. Don't regress this — it's the only way `html-to-image` serializes the mockup frame deterministically.

### Editing the mockup generator

`scripts/generate_mockup.py` is the source of truth for `mockup.png`. The workflow for changing the frame:

1. Edit `scripts/generate_mockup.py`. Keep the locked dimensions at the top of the file clearly commented.
2. Regenerate `mockup.png`:
   ```bash
   python scripts/generate_mockup.py
   ```
3. Run the test suite:
   ```bash
   pytest scripts/test_generate_mockup.py -v
   ```
4. If you changed `MK_W`, `MK_H`, the screen rectangle, or the corner radius, also update the matching constants in `SKILL.md` under "Phone Mockup Component". SKILL.md and the Python script must stay in lockstep.
5. Commit the Python change AND the regenerated `mockup.png` in the same commit.

### Running tests

```bash
pip install pillow pytest
pytest scripts/test_generate_mockup.py -v
```

All 6 tests must pass before you open a PR. CI runs the same suite on every push to `main` and every pull request.

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new user-visible feature or capability
- `fix:` — bug fix
- `docs:` — documentation only (README, CONTRIBUTING, comments, etc.)
- `chore:` — infrastructure, config, build tooling, dependency bumps
- `test:` — adding or adjusting tests without changing behavior
- `refactor:` — internal change that doesn't alter behavior
- `ci:` — changes to CI configuration or workflows

Keep commits **atomic**: one logical change per commit. Don't bundle a bug fix with a new feature.

## Pull requests

- Open against `main`.
- Keep PRs focused. A PR that touches `SKILL.md`, the Python generator, and the CI workflow at once is usually three PRs.
- Make sure CI is green before requesting review.
- Describe *why* the change is needed, not just *what* it does.

## License

`play-store-screenshots` is MIT-licensed. By contributing, you agree that your contributions will be licensed under the same MIT license. See `LICENSE` for the full text.
