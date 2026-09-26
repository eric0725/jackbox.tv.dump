"""Local server that mimics GitHub Pages hosting this repo at /jackbox.tv.dump/.

- Files are only served under PREFIX; anything else is a 404 (like the github.io root).
- Directories serve index.html; "/jackbox.tv.dump" redirects to "/jackbox.tv.dump/".
- Missing paths under PREFIX serve the repo's 404.html (status 404) if it exists,
  which is how GitHub Pages behaves for project sites.

Usage: python tools/pages_server.py [port]   (default 8000)
"""
import http.server
import os
import sys
from functools import partial

PREFIX = "/jackbox.tv.dump"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PagesHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".webmanifest": "application/manifest+json",
    }

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path == PREFIX:
            self.send_response(301)
            self.send_header("Location", PREFIX + "/")
            self.end_headers()
            return None
        if not path.startswith(PREFIX + "/"):
            return self._not_found(project=False)
        # Strip the prefix and let SimpleHTTPRequestHandler resolve the file.
        rel = path[len(PREFIX):]
        fs_path = self.translate_path(rel)
        if os.path.isdir(fs_path):
            if not os.path.exists(os.path.join(fs_path, "index.html")):
                return self._not_found(project=True)
        elif not os.path.exists(fs_path):
            return self._not_found(project=True)
        self.path = rel + (self.path[len(path):] if len(self.path) > len(path) else "")
        return super().send_head()

    def _not_found(self, project):
        page = os.path.join(ROOT, "404.html")
        if project and os.path.exists(page):
            with open(page, "rb") as f:
                body = f.read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return None
        self.send_error(404, "File not found")
        return None

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = partial(PagesHandler, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Serving {ROOT} at http://127.0.0.1:{port}{PREFIX}/", flush=True)
    server.serve_forever()
