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
    required = ["slug", "judul", "driveId", "tanggal", "deskripsi", "cover", "kategori"]
    for i, v in enumerate(data):
        missing = [k for k in required if k not in v]
        if missing:
            print(f"ERROR: Video index {i} kekurangan field: {missing}")
            sys.exit(1)
        if v["kategori"] not in ("indonesia", "papua"):
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

def build_video_card(video):
    return f'''<a href="videos/{video["slug"]}.html" class="video-card" data-category="{video["kategori"]}">
    <img src="{video["cover"]}" alt="{escape_html(video["judul"])}" loading="lazy">
    <div class="card-body">
        <h3>{escape_html(video["judul"])}</h3>
        <p style="color:#64748b;font-size:0.85rem;margin-bottom:0.5rem;">{video["tanggal"]}</p>
        <span class="badge">{video["kategori"]}</span>
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
        output = output.replace("{{ DRIVE_ID }}", v["driveId"])
        output = output.replace("{{ KATEGORI }}", v["kategori"])
        output = output.replace("{{ TANGGAL }}", v["tanggal"])
        cover_path = "../" + v["cover"] if not v["cover"].startswith("http") else v["cover"]
        output = output.replace("{{ COVER }}", cover_path)
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
