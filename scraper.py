"""Site generator for athoyemahmud.github.io

This version keeps the original scraping logic (scrape_linktree_data and
 download_profile_picture) but replaces the HTML and CSS generators with a
 responsive, card-based layout that looks good on both mobile and desktop.

You can drop this in as scraper.py and run:

    python scraper.py

The GitHub Actions workflow that already calls `python scraper.py` and
 publishes the `public/` directory will then deploy the new layout.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


# --- Content knobs (easy to tweak later) ------------------------------------

SITE_TITLE = "Athoye Mahmud | Digital Home"
TAGLINE = (
    "Building thoughtful data products, documenting the journey, and staying curious."
)
LOCATION = "Dhaka, Bangladesh"
ROLE = "Data Science undergrad · ML/AI aspirant"
SECTION_HEADING = "Explore"
SECTION_INTRO = (
    "Favorite corners of the internet where I read, watch, train, and ship ideas."
)
FOOTER_LINE = "Let’s connect or collaborate — message me on Signal or email."

# Optional: nicer subtitles for some well-known links
SUBTITLE_OVERRIDES = {
    "last.fm": "Listening history & scrobbles.",
    "goodreads": "Books I’m reading and want to read.",
    "flickr": "Photos and visual notes.",
    "steam": "Games I play when I’m not reading papers.",
    "roadmap.sh": "Developer roadmaps I track and recommend.",
    "streamlit": "Apps and experiments built with data.",
    "kaggle": "Datasets, notebooks and ML experiments.",
}


# --- Scraping logic (same idea as your original) ----------------------------


def scrape_linktree_data(html_file: str) -> Dict[str, Any]:
    """Parse the saved Linktree HTML and extract profile + links.

    Expects `html_file` to contain the Linktree page source with a
    `<script id="__NEXT_DATA__">` tag, as saved by your GitHub Actions
    workflow.
    """

    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag is None:
        raise ValueError("Could not find the __NEXT_DATA__ script tag.")

    json_data = json.loads(script_tag.string)

    # Match your original structure: props.pageProps.account / links / socialLinks
    page_props = json_data["props"]["pageProps"]
    account_data = page_props["account"]

    profile_picture_url = account_data["profilePictureUrl"]
    username = account_data["username"]
    social_links = page_props.get("socialLinks", [])
    links = page_props.get("links", [])

    return {
        "profile_picture_url": profile_picture_url,
        "username": username,
        "social_links": social_links,
        "links": links,
    }


def download_profile_picture(url: str, output_dir: str = "public") -> None:
    """Download the profile picture into `output_dir/profile_picture.jpg`."""

    filename = os.path.join(output_dir, "profile_picture.jpg")
    response = requests.get(url, stream=True, timeout=20)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download profile picture. Status code: {response.status_code}")


# --- HTML + CSS generators (new layout) ------------------------------------


def _subtitle_for(title: str) -> str:
    key = title.strip().lower()
    return SUBTITLE_OVERRIDES.get(key, f"Visit {title}")


def generate_html(data: Dict[str, Any], output_dir: str = "public") -> None:
    """Generate a responsive, card-based index.html using scraped data."""

    os.makedirs(output_dir, exist_ok=True)

    username: str = data.get("username", "athoye")
    links: List[Dict[str, str]] = data.get("links", [])

    # Build the links grid markup
    link_items: List[str] = []
    for link in links:
        title = link.get("title") or "Link"
        url = link.get("url") or "#"
        subtitle = _subtitle_for(title)
        item_html = f"""          <a class=\"link-tile\" href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\">
            <span class=\"link-title\">{title}</span>
            <span class=\"link-subtitle\">{subtitle}</span>
          </a>"""
        link_items.append(item_html)

    links_block = "\n".join(link_items)
    year = datetime.now().year

    html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{SITE_TITLE}</title>
    <meta name=\"description\" content=\"The digital home of {username}.\" />
    <link rel=\"stylesheet\" href=\"style.css\" />
  </head>
  <body>
    <div class=\"background-gradient\" aria-hidden=\"true\"></div>
    <main class=\"page\">
      <section class=\"profile-card\">
        <img
          src=\"profile_picture.jpg\"
          alt=\"Portrait of {username}\"
          class=\"profile-photo\"
        />
        <h1 class=\"name\">{username}</h1>
        <p class=\"tagline\">{TAGLINE}</p>
        <div class=\"meta\">
          <span>{LOCATION}</span>
          <span>{ROLE}</span>
        </div>
      </section>

      <section class=\"links-grid\" aria-labelledby=\"explore-heading\">
        <header class=\"section-header\">
          <h2 id=\"explore-heading\">{SECTION_HEADING}</h2>
          <p class=\"section-intro\">{SECTION_INTRO}</p>
        </header>
        <div class=\"links\">
{links_block}
        </div>
      </section>

      <footer class=\"footer\">
        <p>{FOOTER_LINE}</p>
        <p class=\"small-print\">© {year} {username}. Crafted with care.</p>
      </footer>
    </main>
  </body>
</html>
"""

    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_css(output_dir: str = "public") -> None:
    """Generate the stylesheet for the new layout.

    This is intentionally self-contained so GitHub Pages can serve `public/`
    directly without extra assets.
    """

    os.makedirs(output_dir, exist_ok=True)

    css_content = """
:root {
  --bg: #050816;
  --bg-alt: rgba(16, 24, 40, 0.88);
  --accent: #4f46e5;
  --accent-soft: rgba(79, 70, 229, 0.15);
  --border-subtle: rgba(148, 163, 184, 0.4);
  --text-primary: #e5e7eb;
  --text-muted: #9ca3af;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text-primary);
  background: radial-gradient(circle at top left, #111827, #020617 52%, #020617 100%);
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: clamp(1.5rem, 5vw, 3rem);
}

.background-gradient {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 0% 0%, rgba(79, 70, 229, 0.35), transparent 55%),
    radial-gradient(circle at 100% 100%, rgba(14, 165, 233, 0.28), transparent 55%);
  opacity: 0.9;
  z-index: -1;
}

.page {
  width: min(960px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.6fr);
  gap: clamp(1.5rem, 3vw, 2.25rem);
}

.profile-card,
.links-grid {
  position: relative;
  padding: clamp(1.75rem, 3vw, 2.25rem);
  border-radius: 1.75rem;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.86));
  border: 1px solid rgba(148, 163, 184, 0.4);
  box-shadow:
    0 18px 45px rgba(15, 23, 42, 0.72),
    0 0 0 1px rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(22px);
}

.profile-card::before {
  content: "";
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  background: conic-gradient(
    from 140deg,
    rgba(79, 70, 229, 0.45),
    transparent 40%,
    transparent 60%,
    rgba(14, 165, 233, 0.55)
  );
  opacity: 0.9;
  z-index: -1;
}

.profile-photo {
  width: 112px;
  height: 112px;
  border-radius: 999px;
  object-fit: cover;
  border: 3px solid rgba(148, 163, 184, 0.7);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.9);
  display: block;
  margin-bottom: 1.25rem;
}

.name {
  font-size: clamp(1.9rem, 3vw, 2.1rem);
  font-weight: 700;
  letter-spacing: 0.02em;
  margin: 0 0 0.5rem 0;
}

.tagline {
  margin: 0 0 1.25rem 0;
  font-size: 0.98rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.meta span {
  font-size: 0.8rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.5);
  background: radial-gradient(circle at 0% 0%, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.7));
}

.section-header {
  margin-bottom: 1rem;
}

.links-grid h2 {
  margin: 0 0 0.35rem 0;
  font-size: 1.1rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(148, 163, 184, 0.95);
}

.section-intro {
  margin: 0;
  font-size: 0.96rem;
  color: var(--text-muted);
}

.links {
  margin-top: 1.4rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.9rem;
}

.link-tile {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: radial-gradient(circle at 0% 0%, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.86));
  text-decoration: none;
  color: inherit;
  transition:
    transform 160ms ease-out,
    border-color 160ms ease-out,
    box-shadow 160ms ease-out,
    background 160ms ease-out;
}

.link-title {
  font-size: 0.98rem;
  font-weight: 500;
}

.link-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.link-tile::after {
  content: "↗";
  font-size: 0.85rem;
  opacity: 0.7;
  position: absolute;
  right: 0.9rem;
  top: 0.9rem;
}

.link-tile:hover {
  transform: translateY(-4px);
  border-color: rgba(129, 140, 248, 0.9);
  background: radial-gradient(circle at 0% 0%, rgba(79, 70, 229, 0.28), rgba(15, 23, 42, 0.94));
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.85);
}

.footer {
  grid-column: 1 / -1;
  margin-top: 1.4rem;
  text-align: center;
  font-size: 0.86rem;
  color: var(--text-muted);
}

.small-print {
  margin-top: 0.35rem;
  opacity: 0.85;
}

/* Responsive tweaks */
@media (max-width: 880px) {
  body {
    padding: 1.25rem;
  }

  .page {
    grid-template-columns: minmax(0, 1fr);
  }

  .footer {
    margin-top: 1rem;
  }
}

@media (max-width: 520px) {
  body {
    padding: 1rem;
  }

  .profile-card,
  .links-grid {
    padding: 1.25rem 1.15rem;
    border-radius: 1.25rem;
  }

  .links {
    grid-template-columns: minmax(0, 1fr);
  }
}
"""

    css_path = os.path.join(output_dir, "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)


# --- Orchestration ---------------------------------------------------------


def build_site(html_file: str = "linktree.html", output_dir: str = "public") -> None:
    os.makedirs(output_dir, exist_ok=True)
    scraped_data = scrape_linktree_data(html_file)
    download_profile_picture(scraped_data["profile_picture_url"], output_dir=output_dir)
    generate_html(scraped_data, output_dir=output_dir)
    generate_css(output_dir=output_dir)
    print(f"Successfully generated files in '{output_dir}' directory.")


if __name__ == "__main__":
    build_site()
