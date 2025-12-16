import platform
import pytest
from app import probe


def test_probe_on_non_windows():
    if platform.system() == 'Windows':
        pytest.skip('Non-windows test only')
    res = probe.probe_window('NoSuchWindow', max_elems=10)
    assert res.get('found') is False


@pytest.mark.skipif(platform.system() != 'Windows', reason='Windows only')
def test_probe_windows_smoke():
    # This smoke test will run on Windows runners; it's a best-effort validation
    res = probe.probe_window('A Welcome Soap Box', max_elems=10)
    assert isinstance(res, dict)
    assert 'found' in res
