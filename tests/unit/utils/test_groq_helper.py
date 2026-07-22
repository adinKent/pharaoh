from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from utils import groq_helper


@pytest.fixture(autouse=True)
def reset_groq_client():
    groq_helper.client = None
    yield
    groq_helper.client = None


def completion(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_get_groq_client_uses_ssm_api_key_and_caches_client(mocker):
    get_ssm_parameter = mocker.patch.object(groq_helper, "get_ssm_parameter", return_value="test-api-key")
    groq = mocker.patch.object(groq_helper, "Groq")

    first_client = groq_helper.get_groq_client()
    second_client = groq_helper.get_groq_client()

    assert first_client is second_client
    get_ssm_parameter.assert_called_once_with("groq/api-key")
    groq.assert_called_once_with(api_key="test-api-key")


def test_generate_response_uses_main_model(mocker):
    client = Mock()
    client.chat.completions.create.return_value = completion("analysis")
    mocker.patch.object(groq_helper, "get_groq_client", return_value=client)

    result = groq_helper.generate_groq_technical_analysis_response("stock data")

    assert result == "analysis"
    client.chat.completions.create.assert_called_once()
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == groq_helper.main_model
    assert request["messages"][0]["role"] == "user"
    assert "stock data" in request["messages"][0]["content"]


def test_generate_response_retries_with_fallback_model(mocker):
    client = Mock()
    client.chat.completions.create.side_effect = [
        RuntimeError("primary unavailable"),
        completion("fallback analysis"),
    ]
    mocker.patch.object(groq_helper, "get_groq_client", return_value=client)
    mocker.patch.object(groq_helper.logger, "exception")

    result = groq_helper.generate_groq_technical_analysis_response("stock data")

    assert result == "fallback analysis"
    assert client.chat.completions.create.call_args_list == [
        call(
            model=groq_helper.main_model,
            messages=[{"role": "user", "content": mocker.ANY}],
        ),
        call(
            model=groq_helper.fallback_model,
            messages=[{"role": "user", "content": mocker.ANY}],
        ),
    ]
