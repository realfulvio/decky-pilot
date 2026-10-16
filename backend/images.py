import base64
import io
import secrets
import warnings

from .errors import RpcError, require, string

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = ImageOps = None


class Images:
    """Explicit uploaded bytes only. No filesystem path or URL RPC exists."""
    def __init__(self, clock):
        self.clock = clock
        self.items = {}

    @property
    def available(self):
        return Image is not None

    def clear(self):
        self.items.clear()

    def prune(self):
        for ref in list(self.items):
            if self.items[ref]["expires"] <= self.clock():
                self.items.pop(ref)

    def prepare(self, data, mime, session, destination):
        require(self.available, "IMAGE_UNSUPPORTED")
        string(data, 7_000_000, 1)
        require(mime in ("image/png", "image/jpeg"))
        try:
            raw = base64.b64decode(data, validate=True)
            require(len(raw) <= 5 * 1024 * 1024)
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as original:
                    require(original.format in ("PNG", "JPEG"))
                    require(mime == ("image/png" if original.format == "PNG" else "image/jpeg"))
                    require(0 < original.width * original.height <= 20_000_000)
                    require(not getattr(original, "is_animated", False))
                    original.load()
                    image = ImageOps.exif_transpose(original).convert("RGB")
                    image.thumbnail((1280, 1280))
                    # New pixel image prevents copied EXIF, ICC, comments and ancillary chunks.
                    clean = Image.frombytes("RGB", image.size, image.tobytes())
                    output = io.BytesIO()
                    clean.save(output, format="JPEG", quality=85, optimize=True)
                    result = output.getvalue()
                    require(len(result) <= 1_500_000)
        except (ValueError, OSError, Image.DecompressionBombError,
                Image.DecompressionBombWarning) as exc:
            raise RpcError("INVALID_INPUT") from exc
        self.prune()
        # Only one pending image; preparing another explicitly replaces it.
        self.clear()
        ref = secrets.token_urlsafe(24)
        self.items[ref] = {"bytes": result, "mime": "image/jpeg", "session": session,
                           "destination": destination, "approved": False,
                           "preparedAt": self.clock(),
                           "expires": self.clock() + 300}
        return {"imageRef": ref, "preview": "data:image/jpeg;base64," +
                base64.b64encode(result).decode("ascii"), "width": clean.width,
                "height": clean.height, "destination": destination}

    def approve(self, ref, session, destination):
        self.prune()
        item = self.items.get(ref)
        require(item is not None and item["session"] == session and
                item["destination"] == destination, "CONSENT_REQUIRED")
        item["approved"] = True
        return {"approved": True}

    def take(self, ref, session, destination):
        self.prune()
        item = self.items.get(ref)
        require(item is not None and item["approved"] and item["session"] == session and
                item["destination"] == destination, "CONSENT_REQUIRED")
        require(self.clock() - item["preparedAt"] <= 45, "CONTEXT_STALE")
        return self.items.pop(ref)

    def discard(self, ref):
        self.items.pop(ref, None)
