#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_JSON = os.path.join(BASE_DIR, "videos.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = BASE_DIR
VIDEOS_OUTPUT_DIR = os.path.join(BASE_DIR, "videos")
DEFAULT_COVER = "assets/img/no-cover.svg"
SITE_URL = "https://farming21.github.io/indonesia"
VALID_CATEGORIES = ("indonesia", "papua")
REQUIRED_FIELDS = ("slug", "judul", "driveId", "tanggal", "deskripsi", "kategori")


def load_videos():
    if not os.path.exists(VIDEOS_JSON):
        print(f"ERROR: {VIDEOS_JSON} tidak ditemukan.")
        sys.exit(1)

    with open(VIDEOS_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: videos.json tidak valid: {e}")
            sys.exit(1)

    if not isinstance(data, list):
        print("ERROR: videos.json harus berisi array.")
        sys.exit(1)

    for i, v in enumerate(data):
        if not isinstance(v, dict):
            print(f"ERROR: Video index {i} harus berupa object.")
            sys.exit(1)

        missing = [k for k in REQUIRED_FIELDS if not v.get(k)]
        if missing:
            print(f"ERROR: Video index {i} kekurangan field: {missing}")
            sys.exit(1)

        if v["kategori"] not in VALID_CATEGORIES:
            print(f"ERROR: Video '{v['slug']}' kategori tidak valid: {v['kategori']}")
            sys.exit(1)

    return data


def load_template(name):
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        print(f"ERROR: Template tidak ditemukan: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def escape_html(text):
    return (str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;"))


def cover_for_video(video):
    cover = str(video.get("cover") or "").strip()
    return cover if cover else DEFAULT_COVER


def absolute_cover_url(cover_path):
    """Return an absolute URL suitable for Open Graph/Twitter previews."""
    if cover_path.startswith(("http://", "https://")):
        return cover_path
    return f"{SITE_URL}/{cover_path.lstrip('/')}"


def build_video_card(video):
    cover = cover_for_video(video)
    return f'''<a href="videos/{escape_html(video["slug"])}.html" class="video-card" data-category="{escape_html(video["kategori"])}">
    <img src="{escape_html(cover)}" alt="{escape_html(video["judul"])}" loading="lazy">
    <div class="card-body">
        <h3>{escape_html(video["judul"])}</h3>
        <p style="color:#64748b;font-size:0.85rem;margin-bottom:0.5rem;">{escape_html(video["tanggal"])}</p>
        <span class="badge">{escape_html(video["kategori"])}</span>
    </div>
</a>'''


def generate_index(videos):
    template = load_template("index.html")
    sorted_videos = sorted(videos, key=lambda x: x["tanggal"], reverse=True)
    cards_html = "\n        ".join(build_video_card(v) for v in sorted_videos)
    if not cards_html:
        cards_html = '<p style="text-align:center;grid-column:1/-1;padding:2rem;color:#64748b;">Belum ada video.</p>'
    output = template.replace("{{ VIDEO_CARDS }}", cards_html)
    out_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"OK: index.html ({len(videos)} video)")


def generate_video_pages(videos):
    if os.path.exists(VIDEOS_OUTPUT_DIR):
        for fn in os.listdir(VIDEOS_OUTPUT_DIR):
            if fn.endswith(".html"):
                os.remove(os.path.join(VIDEOS_OUTPUT_DIR, fn))
    else:
        os.makedirs(VIDEOS_OUTPUT_DIR, exist_ok=True)

    template = load_template("video.html")

    for v in videos:
        output = template
        output = output.replace("{{ JUDUL }}", escape_html(v["judul"]))
        output = output.replace("{{ DESKRIPSI }}", escape_html(v["deskripsi"]))
        output = output.replace("{{ DRIVE_ID }}", escape_html(v["driveId"]))
        output = output.replace("{{ KATEGORI }}", escape_html(v["kategori"]))
        output = output.replace("{{ TANGGAL }}", escape_html(v["tanggal"]))

        cover = cover_for_video(v)
        cover_path = cover if cover.startswith(("http://", "https://")) else "../" + cover
        output = output.replace("{{ COVER }}", escape_html(cover_path))

        # Social sharing (Facebook, WhatsApp, Telegram, X, etc.) requires
        # an absolute image URL; the player itself continues using the
        # relative cover path above.
        og_cover = absolute_cover_url(cover)
        page_url = f"{SITE_URL}/videos/{v['slug']}.html"
        output = output.replace("{{ OG_COVER }}", escape_html(og_cover))
        output = output.replace("{{ PAGE_URL }}", escape_html(page_url))

        out_path = os.path.join(VIDEOS_OUTPUT_DIR, f"{v['slug']}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output)

    print(f"OK: videos/ ({len(videos)} halaman detail)")


def main():
    print("=" * 60)
    print(f"GENERATOR DIMULAI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    videos = load_videos()
    print(f"Total video valid: {len(videos)}")
    generate_index(videos)
    generate_video_pages(videos)
    print("=" * 60)
    print("GENERASI SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
