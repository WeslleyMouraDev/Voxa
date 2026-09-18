from unittest.mock import MagicMock, patch
from backend.services.metrics_service import MetricsService
from backend.models.schemas import SystemMetricsSchema


def test_metrics_service_structure():
    metrics = MetricsService.get_current_metrics()
    assert "cpu_percent" in metrics
    assert "ram_used_gb" in metrics
    assert "ram_total_gb" in metrics
    assert "ram_percent" in metrics

    assert isinstance(metrics["cpu_percent"], (int, float))
    assert isinstance(metrics["ram_used_gb"], (int, float))
    assert isinstance(metrics["ram_total_gb"], (int, float))
    assert isinstance(metrics["ram_percent"], (int, float))

    assert metrics["ram_total_gb"] > 0
    assert metrics["ram_used_gb"] >= 0
    assert 0.0 <= metrics["ram_percent"] <= 100.0
    assert 0.0 <= metrics["cpu_percent"] <= 100.0

    # Valida com o schema Pydantic
    schema = SystemMetricsSchema(**metrics)
    assert schema.ram_total_gb == metrics["ram_total_gb"]
    assert schema.ram_used_gb == metrics["ram_used_gb"]
    assert schema.ram_percent == metrics["ram_percent"]
    assert schema.cpu_percent == metrics["cpu_percent"]


def test_metrics_service_mocked_values():
    mock_memory = MagicMock()
    # 8 GB usados, 16 GB total, 50.0%
    mock_memory.used = 8 * (1024 ** 3)
    mock_memory.total = 16 * (1024 ** 3)
    mock_memory.percent = 50.0

    with patch("psutil.cpu_percent", return_value=32.4) as mock_cpu, \
         patch("psutil.virtual_memory", return_value=mock_memory) as mock_mem:
        metrics = MetricsService.get_current_metrics()

        mock_cpu.assert_called_once_with(interval=None)
        mock_mem.assert_called_once()

        assert metrics["cpu_percent"] == 32.4
        assert metrics["ram_used_gb"] == 8.0
        assert metrics["ram_total_gb"] == 16.0
        assert metrics["ram_percent"] == 50.0
