"""Unit tests for the experiments resource — config support."""

import pytest


@pytest.mark.asyncio
async def test_create_passes_config(wave_client, sample_experiment):
    """create() forwards `config` in the POST body."""
    wave_client._http_client.request.return_value = sample_experiment

    await wave_client.experiments.create(
        experiment_type_id=1,
        description="with config",
        config={"number_of_repetitions": 3},
    )

    method, url, json_data, _params = wave_client._http_client.request.await_args.args
    assert method == "POST"
    assert url == "/api/v1/experiments/"
    assert json_data["config"] == {"number_of_repetitions": 3}


@pytest.mark.asyncio
async def test_create_defaults_config_to_empty(wave_client, sample_experiment):
    """Omitting config sends an empty object (not null)."""
    wave_client._http_client.request.return_value = sample_experiment

    await wave_client.experiments.create(experiment_type_id=1, description="no config")

    _method, _url, json_data, _params = wave_client._http_client.request.await_args.args
    assert json_data["config"] == {}


@pytest.mark.asyncio
async def test_update_includes_config_when_provided(wave_client, sample_experiment):
    """update() includes config when set; exclude_none drops it when not."""
    wave_client._http_client.request.return_value = sample_experiment

    await wave_client.experiments.update(
        "550e8400-e29b-41d4-a716-446655440000", config={"number_of_repetitions": 5}
    )
    _m, _u, json_data, _p = wave_client._http_client.request.await_args.args
    assert json_data["config"] == {"number_of_repetitions": 5}


@pytest.mark.asyncio
async def test_update_omits_config_when_none(wave_client, sample_experiment):
    """update() with no config must not send a null config (exclude_none)."""
    wave_client._http_client.request.return_value = sample_experiment

    await wave_client.experiments.update(
        "550e8400-e29b-41d4-a716-446655440000", description="just a description"
    )
    _m, _u, json_data, _p = wave_client._http_client.request.await_args.args
    assert "config" not in json_data


@pytest.mark.asyncio
async def test_get_config_hits_config_endpoint(wave_client):
    """get_config() issues a GET to the narrow config endpoint."""
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    wave_client._http_client.request.return_value = {
        "experiment_uuid": uuid,
        "config": {"number_of_repetitions": 2},
    }

    result = await wave_client.experiments.get_config(uuid)

    method, url, _json, _params = wave_client._http_client.request.await_args.args
    assert method == "GET"
    assert url == f"/api/v1/experiments/{uuid}/config"
    assert result["config"] == {"number_of_repetitions": 2}


@pytest.mark.asyncio
async def test_set_config_puts_wrapped_body(wave_client):
    """set_config() PUTs a {"config": ...} body to the config endpoint."""
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    config = {"number_of_repetitions": 4}
    wave_client._http_client.request.return_value = {"experiment_uuid": uuid, "config": config}

    await wave_client.experiments.set_config(uuid, config)

    method, url, json_data, _params = wave_client._http_client.request.await_args.args
    assert method == "PUT"
    assert url == f"/api/v1/experiments/{uuid}/config"
    assert json_data == {"config": config}
