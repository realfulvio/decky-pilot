"""Closed production capture gate: no acquisition or provider side effects."""
from unittest.mock import AsyncMock

import pytest

from backend.capture import CAPTURE_SAFETY_VALIDATED, GameCapture
from backend.errors import RpcError
from test_service import configured, finish, tick_at


async def test_closed_gate_overrides_cached_availability(tmp_path):
    assert CAPTURE_SAFETY_VALIDATED is False
    spawn = AsyncMock(side_effect=AssertionError('No subprocess is allowed'))
    capture = GameCapture(tmp_path / 'frames', spawn=spawn)
    capture.available = capture.probed = True
    assert await capture.probe() is False
    assert capture.available is False
    spawn.assert_not_awaited()
    assert not capture.root.exists()


@pytest.mark.parametrize('context', [
    {'source': 'steam_internal', 'appId': '123'},
    {'source': 'manual', 'appId': '123'},
    {'source': 'unknown', 'appId': ''},
])
async def test_capture_checks_gate_before_probe_or_focus(tmp_path, context):
    capture = GameCapture(tmp_path / 'frames')
    capture.probe = AsyncMock(return_value=True)
    capture.assert_game = AsyncMock(side_effect=AssertionError('Focus is not a safety proof'))
    with pytest.raises(RpcError) as error:
        await capture.capture(context)
    assert error.value.code == 'CAPTURE_UNAVAILABLE'
    capture.probe.assert_not_awaited()
    capture.assert_game.assert_not_awaited()
    assert not capture.root.exists()


@pytest.mark.parametrize('provider', ['ollama', 'chatgpt', 'grok'])
@pytest.mark.parametrize('mode', ['manual', 'automatic'])
async def test_unavailable_capture_rejects_before_credentials_or_provider(
        tmp_path, clock, transport, monkeypatch, provider, mode):
    service, events = await configured(tmp_path, clock, transport)
    try:
        await service.rpc('update_settings', {'imagesEnabled': True, 'captureEnabled': True})
        await service.rpc('set_capture_guard', {'blocked': False})
        # Simulate stale cached backend state and an already admitted automatic session.
        service.capture.available = service.capture.probed = True
        service.config.settings['provider'] = provider
        credentials = AsyncMock(side_effect=AssertionError('No credential refresh is allowed'))
        discover = AsyncMock(side_effect=AssertionError('No provider catalog request is allowed'))
        monkeypatch.setattr(service, 'credentials', credentials)
        monkeypatch.setattr('backend.service.discover', discover)
        session = service.context['sessionId']
        if mode == 'manual':
            result = await service.rpc('prepare_capture', {
                'sessionId': session, 'confirmGameplay': True})
            assert result['error']['code'] == 'CAPTURE_UNAVAILABLE'
        else:
            service.config.settings['autoHints'] = True
            service.auto_session_consent = service.auto_visual = True
            await tick_at(service, clock, 90)
            await finish(service)
            assert service.auto_attempts == service.auto_errors == 1
            assert not service.records
        credentials.assert_not_awaited()
        discover.assert_not_awaited()
        assert not transport.calls and not service.images.items
        assert service.capture_task is None and service.active is None
        assert not any(name == 'assistant_result' for name, _ in events)
        assert not service.capture.root.exists()
    finally:
        await service.close()


async def test_closed_gate_refuses_new_automatic_consent(tmp_path, clock, transport):
    service, _ = await configured(tmp_path, clock, transport)
    try:
        await service.rpc('update_settings', {'imagesEnabled': True, 'captureEnabled': True})
        service.capture.available = service.capture.probed = True
        result = await service.rpc('set_auto_hints', {
            'enabled': True, 'consent': True, 'visual': True,
            'sessionId': service.context['sessionId']})
        assert result['error']['code'] == 'CAPTURE_UNAVAILABLE'
        assert not service.auto_session_consent
        assert not transport.calls
    finally:
        await service.close()


@pytest.mark.parametrize('failure,code', [
    ('writer-error', 'CAPTURE_UNAVAILABLE'), ('writer-timeout', 'CAPTURE_UNAVAILABLE'),
    ('oversized', 'INVALID_INPUT'), ('cancel', None),
])
async def test_synthetic_capture_failure_removes_private_partial_files(
        tmp_path, monkeypatch, failure, code):
    import asyncio
    from pathlib import Path

    # Test-only override: injected command writes synthetic bytes, never spawns a process.
    monkeypatch.setattr('backend.capture.CAPTURE_SAFETY_VALIDATED', True)
    capture = GameCapture(tmp_path / 'frames')
    capture.probe = AsyncMock(return_value=True)
    capture.assert_game = AsyncMock()
    started = asyncio.Event()
    target = None

    def write_partial(path):
        path.write_bytes(b'synthetic partial image')
        if failure == 'oversized':
            with path.open('wb') as file:
                file.truncate(5 * 1024 * 1024 + 1)

    async def command(*args):
        nonlocal target
        target = Path(args[-1])
        await asyncio.to_thread(write_partial, target)
        started.set()
        if failure == 'writer-error':
            raise OSError('synthetic writer failure')
        if failure == 'writer-timeout':
            raise TimeoutError('synthetic deadline')
        if failure == 'cancel':
            await asyncio.Event().wait()

    capture.command = command
    task = asyncio.create_task(capture.capture({'source': 'steam_internal', 'appId': '123'}))
    try:
        await asyncio.wait_for(started.wait(), 2)
        if failure == 'cancel':
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            with pytest.raises(RpcError) as error:
                await task
            assert error.value.code == code
        assert target is not None and not target.exists()
        assert not list(capture.root.iterdir())
        assert capture.process is None
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
