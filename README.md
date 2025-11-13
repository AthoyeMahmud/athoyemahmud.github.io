# athoyemahmud.github.io

This repository powers [Athoye Mahmud's digital home](https://athoyemahmud.github.io). The site is generated from the latest data on [Linktree](https://linktr.ee/athoye) so that it always mirrors the same set of profiles and links.

## How the site is built

1. GitHub Actions (see [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)) saves the Linktree HTML into `linktree.html` and runs `python scraper.py`.
2. `scraper.py` parses the `__NEXT_DATA__` payload to collect the username, profile image, and Linktree links.
3. The script downloads the profile photo and writes a responsive `public/index.html` + `public/style.css` based on the data.
4. The resulting `public/` directory is published automatically to GitHub Pages.

## Regenerating locally

```bash
python scraper.py
```

The script refreshes `public/profile_picture.jpg`, `public/index.html`, and `public/style.css`. Commit the updated files if you are making manual adjustments or testing layout changes.

## Customising the copy

Edit the constants near the top of `scraper.py` (`TAGLINE`, `LOCATION`, `ROLE`, etc.) to tweak the profile card, section heading, or footer text. The workflow will pick up the new copy the next time it runs.
