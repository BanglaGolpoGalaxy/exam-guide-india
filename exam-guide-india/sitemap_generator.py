import os
import datetime

BASE_URL = "https://banglagolpogalaxy.github.io/exam-guide-india"
ROOT_DIR = "."

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

for root, dirs, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            url_path = file_path.replace("\\", "/").replace("./", "")
            full_url = f"{BASE_URL}/{url_path}"
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            lastmod = mod_time.strftime("%Y-%m-%d")
            sitemap += f"  <url>\n"
            sitemap += f"    <loc>{full_url}</loc>\n"
            sitemap += f"    <lastmod>{lastmod}</lastmod>\n"
            sitemap += f"    <changefreq>weekly</changefreq>\n"
            sitemap += f"    <priority>0.8</priority>\n"
            sitemap += f"  </url>\n"

sitemap += '</urlset>'

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(sitemap)

print("✅ sitemap.xml generated successfully!")
