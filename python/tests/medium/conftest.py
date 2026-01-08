"""Configuration and fixtures for medium-sized integration tests."""

import asyncio
import os
from typing import AsyncGenerator

import httpx
import pytest
from wave_client import WaveClient


@pytest.fixture(scope="session")
def localhost_url() -> str:
    """Localhost URL for integration testing."""
    return "http://localhost:8000"


async def check_localhost_availability(url: str) -> bool:
    """Check if WAVE backend is available on localhost."""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/health")
            return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def integration_client(localhost_url) -> AsyncGenerator[WaveClient, None]:
    """Create a WAVE client for integration testing.

    Explicitly configures client to use localhost, independent of environment variables.
    Automatically skips tests if backend is unavailable or API key is missing.

    Requires:
    - WAVE backend running on localhost
    - WAVE_API_KEY environment variable with ADMIN/TEST level key
    """
    # Check backend availability
    if not await check_localhost_availability(localhost_url):
        pytest.skip(f"WAVE backend not available on {localhost_url}")

    # Check API key
    api_key = os.getenv("WAVE_API_KEY")
    if not api_key:
        pytest.skip("WAVE_API_KEY environment variable not set")

    # Explicitly specify localhost - don't rely on environment variables
    client = WaveClient(api_key=api_key, base_url=localhost_url)

    try:
        async with client:
            # Test connection
            health = await client.get_health()
            if not health.get("status") == "healthy":
                pytest.skip("WAVE backend health check failed")
            yield client
    except Exception as e:
        pytest.skip(f"Failed to connect to WAVE backend: {e}")


@pytest.fixture
def sample_experiment_type_data():
    """Sample experiment type data for testing."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"integration_test_rt_{unique_id}",
        "description": "Integration test for reaction time experiments",
        "table_name": f"int_test_rt_data_{unique_id}",
        "schema_definition": {
            "reaction_time": "FLOAT",
            "accuracy": "FLOAT",
            "stimulus_type": "STRING",
            "difficulty_level": "INTEGER",
            "correct": "BOOLEAN",
        },
    }


@pytest.fixture
def sample_experiment_data():
    """Sample experiment data for testing."""
    return {
        "description": "Integration test experiment instance",
        # TODO: Using empty tags for now to avoid dependency on pre-existing tags.
        # Should create tags within test client for better test coverage.
        "tags": [],
        "additional_data": {"test_session": "integration_test_session", "researcher": "pytest"},
    }


@pytest.fixture
def sample_tag_data():
    """Sample tag data for testing."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"integration_test_tag_{unique_id}",
        "description": "Tag created during integration testing",
    }


@pytest.fixture
def sample_experiment_data_rows():
    """Sample experiment data rows for testing."""
    return [
        {
            "participant_id": "INT_TEST_001",
            "reaction_time": 0.543,
            "accuracy": 0.95,
            "stimulus_type": "visual",
            "difficulty_level": 1,
            "correct": True,
        },
        {
            "participant_id": "INT_TEST_001",
            "reaction_time": 0.721,
            "accuracy": 0.85,
            "stimulus_type": "auditory",
            "difficulty_level": 2,
            "correct": True,
        },
        {
            "participant_id": "INT_TEST_002",
            "reaction_time": 0.692,
            "accuracy": 0.90,
            "stimulus_type": "visual",
            "difficulty_level": 1,
            "correct": True,
        },
    ]
