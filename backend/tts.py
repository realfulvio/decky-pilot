import asyncio
import base64
import shutil

from .errors import RpcError, require
from .transport import check_response
from .i18n import translate


def normalize_wav(audio):
    # espeak-ng --stdout streams placeholder RIFF/data sizes (0x7FFFF024/0x7FFFF000, observed
    # on SteamOS 3.8.28 with espeak-ng 1.52.0). Rewrite them for a canonical 44-byte PCM header.
    if (len(audio) >= 44 and audio[:4] == b"RIFF" and audio[8:16] == b"WAVEfmt " and
            audio[16:20] == (16).to_bytes(4, "little") and audio[36:40] == b"data"):
        fixed = bytearray(audio)
        fixed[4:8] = (len(audio) - 8).to_bytes(4, "little")
        fixed[40:44] = (len(audio) - 44).to_bytes(4, "little")
        return bytes(fixed)
    return audio


class TTS:
    def __init__(self, transport, executable=None, spawn=asyncio.create_subprocess_exec):
        self.transport = transport
        self.executable = executable if executable is not None else shutil.which("espeak-ng")
        self.spawn = spawn
        self.process = None

    def capabilities(self):
        return {"local": bool(self.executable), "openai": True, "syntheticVoice": True}

    async def synthesize(self, text, settings, secrets):
        text = text[:1000]
        require(settings["voiceEnabled"], "VOICE_UNAVAILABLE")
        if settings["ttsEngine"] == "openai":
            require(settings["ttsConsent"], "CONSENT_REQUIRED")
            require(secrets.get("openai"), "NOT_CONFIGURED")
            # This model documents the instructions field for pronunciation.
            # Latest product decision: assistant response language also governs speech.
            require(settings["ttsModel"] == "gpt-4o-mini-tts", "VOICE_UNAVAILABLE")
            response = await self.transport.request("https://api.openai.com/v1/audio/speech",
                {"Authorization": f"Bearer {secrets['openai']}"},
                {"model": settings["ttsModel"], "voice": settings["ttsVoice"],
                 "input": text, "response_format": "wav",
                 "instructions": translate("speechInstruction", settings["responseLanguage"])},
                limit=8_000_000, deadline=45)
            audio = check_response(response).body
        else:
            require(bool(self.executable), "VOICE_UNAVAILABLE")
            try:
                self.process = await self.spawn(self.executable, "-v", settings["responseLanguage"], "--stdout", "--stdin",
                    stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL)
                async with asyncio.timeout(30):
                    # Bound stdout while generating, rather than buffering unbounded communicate().
                    self.process.stdin.write(text.encode("utf-8"))
                    await self.process.stdin.drain()
                    self.process.stdin.close()
                    chunks = bytearray()
                    while True:
                        chunk = await self.process.stdout.read(65536)
                        if not chunk:
                            break
                        chunks.extend(chunk)
                        require(len(chunks) <= 8_000_000, "VOICE_UNAVAILABLE")
                    require(await self.process.wait() == 0, "VOICE_UNAVAILABLE")
                    audio = normalize_wav(bytes(chunks))
            except OSError as exc:
                raise RpcError("VOICE_UNAVAILABLE") from exc
            finally:
                await self.stop()
        require(len(audio) <= 8_000_000 and audio[:4] == b"RIFF" and audio[8:12] == b"WAVE",
                "VOICE_UNAVAILABLE")
        return {"mime": "audio/wav", "audioBase64": base64.b64encode(audio).decode("ascii")}

    async def stop(self):
        if self.process:
            process, self.process = self.process, None
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
                await process.wait()
