from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from utils import opencode_helper


@pytest.fixture(autouse=True)
def reset_opencode_client():
    opencode_helper.client = None
    yield
    opencode_helper.client = None


def completion(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_get_opencode_client_uses_ssm_api_key_and_caches_client(mocker):
    get_ssm_parameter = mocker.patch.object(opencode_helper, "get_ssm_parameter", return_value="test-api-key")
    openai = mocker.patch.object(opencode_helper, "OpenAI")

    first_client = opencode_helper.get_opencode_client()
    second_client = opencode_helper.get_opencode_client()

    assert first_client is second_client
    get_ssm_parameter.assert_called_once_with("opencode/api-key")
    openai.assert_called_once_with(api_key="test-api-key", base_url=opencode_helper.base_url)


def test_generate_response_uses_main_model(mocker):
    client = Mock()
    client.chat.completions.create.return_value = completion("analysis")
    mocker.patch.object(opencode_helper, "get_opencode_client", return_value=client)

    result = opencode_helper.generate_opencode_technical_analysis_response("stock data")

    assert result == "analysis"
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == opencode_helper.main_model
    assert request["messages"][0]["role"] == "user"
    assert "stock data" in request["messages"][0]["content"]


def test_generate_response_retries_with_fallback_model(mocker):
    client = Mock()
    client.chat.completions.create.side_effect = [
        RuntimeError("primary unavailable"),
        completion("fallback analysis"),
    ]
    mocker.patch.object(opencode_helper, "get_opencode_client", return_value=client)
    mocker.patch.object(opencode_helper.logger, "exception")

    result = opencode_helper.generate_opencode_technical_analysis_response("stock data")

    assert result == "fallback analysis"
    assert client.chat.completions.create.call_args_list == [
        call(model=opencode_helper.main_model, messages=[{"role": "user", "content": mocker.ANY}]),
        call(model=opencode_helper.fallback_model, messages=[{"role": "user", "content": mocker.ANY}]),
    ]
