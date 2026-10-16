"""Validate relative presentation links and decode every public presentation image."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

DOCUMENTS = ("README.md", "README.it.md", "docs/UI_GALLERY.md",
             "docs/PRESENTATION_ASSETS.md", "docs/PUBLICATION_REVIEW.md", "docs/PROVIDER_VERIFICATION.md")


def verify(root):
    root = root.resolve()
    links = 0
    for name in DOCUMENTS:
        path = root / name
        text = path.read_text(encoding="utf-8")
        # Ignore fenced examples: only actual rendered links are navigable.
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        targets = re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text)
        targets += re.findall(r'(?:src|href)="([^"]+)"', text)
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#"):
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root) or not destination.is_file():
                raise ValueError(f"Broken/conflicting relative link in {name}: {target}")
            links += 1
    images = list((root / "docs/images/ui").glob("*.png"))
    images += list((root / "assets").rglob("*.png"))
    for path in images:
        with Image.open(path) as image:
            image.load()
            if min(image.size) < 20 or image.getexif():
                raise ValueError(f"Invalid image/metadata: {path.relative_to(root)}")
    metadata = json.loads((root / "docs/images/ui/source.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-f0-9]{40}", metadata["commit"]):
        raise ValueError("Missing committed gallery provenance")
    if len(list((root / "docs/images/ui").glob("*.png"))) != metadata["images"]:
        raise ValueError("Gallery image count does not match provenance")
    print(f"Presentation verified: {links} relative links, {len(images)} decoded PNGs, "
          f"gallery source {metadata['commit']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    verify(parser.parse_args().root)
