"""Small tests for WaveClient."""

from wave_client import WaveClient


def test_basic_assertion():
    """Basic test that always passes."""
    assert True


def test_wave_client_init():
    """Test WaveClient can be instantiated."""
    client = WaveClient()
    assert client is not None


def test_get_experiment_data():
    """Test get_experiment_data returns expected format."""
    client = WaveClient()
    result = client.get_experiment_data("test-exp-123")
    assert "test-exp-123" in result
    assert isinstance(result, str)
