from unittest.mock import MagicMock, patch
import pytest

from backend.services.cpu_limiter import CPULimiter


def test_calculate_threads():
    limiter = CPULimiter()

    with patch("os.cpu_count", return_value=8):
        assert limiter.calculate_threads(25) == 2
        assert limiter.calculate_threads(50) == 4
        assert limiter.calculate_threads(75) == 6
        assert limiter.calculate_threads(100) == 8

    # Edge cases: 1 core
    with patch("os.cpu_count", return_value=1):
        assert limiter.calculate_threads(25) == 1
        assert limiter.calculate_threads(50) == 1
        assert limiter.calculate_threads(100) == 1

    # Edge cases: cpu_count returns None
    with patch("os.cpu_count", return_value=None):
        assert limiter.calculate_threads(50) == 1


def test_apply_limits_windows():
    limiter = CPULimiter()

    mock_process = MagicMock()
    with patch("os.name", "nt"), \
         patch("psutil.Process", return_value=mock_process), \
         patch("backend.services.cpu_limiter.psutil.BELOW_NORMAL_PRIORITY_CLASS", 0x00004000, create=True), \
         patch("os.cpu_count", return_value=8):
        
        info = limiter.apply_limits(cpu_percent=50)

        assert info["cpu_percent"] == 50
        assert info["threads"] == 4
        assert info["total_cores"] == 8
        assert info["nice_applied"] is True
        mock_process.nice.assert_called_once_with(0x00004000)


def test_apply_limits_posix():
    limiter = CPULimiter()

    mock_process = MagicMock()
    with patch("os.name", "posix"), \
         patch("psutil.Process", return_value=mock_process), \
         patch("os.cpu_count", return_value=4):
        
        info = limiter.apply_limits(cpu_percent=75)

        assert info["cpu_percent"] == 75
        assert info["threads"] == 3
        assert info["total_cores"] == 4
        assert info["nice_applied"] is True
        mock_process.nice.assert_called_once_with(10)


def test_apply_limits_torch_handling():
    limiter = CPULimiter()

    mock_torch = MagicMock()
    with patch.dict("sys.modules", {"torch": mock_torch}), \
         patch("os.cpu_count", return_value=8), \
         patch("psutil.Process"):
        
        info = limiter.apply_limits(cpu_percent=50)
        mock_torch.set_num_threads.assert_called_once_with(4)
        assert info["threads"] == 4


def test_apply_limits_handles_permission_error():
    limiter = CPULimiter()

    mock_process = MagicMock()
    mock_process.nice.side_effect = Exception("Permission denied")

    with patch("psutil.Process", return_value=mock_process), \
         patch("os.cpu_count", return_value=4):
        
        info = limiter.apply_limits(cpu_percent=50)
        assert info["nice_applied"] is False
