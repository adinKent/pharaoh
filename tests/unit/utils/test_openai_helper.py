from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from utils import openai_helper


@pytest.fixture(autouse=True)
def reset_openai_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    openai_helper.client = None
    yield
    openai_helper.client = None


def completion(content: str, tool_calls=None):
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or [])
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def response(content: str = "", output=None):
    return SimpleNamespace(output_text=content, output=output or [])


def tool_call(call_id: str, name: str, arguments: str):
    return SimpleNamespace(id=call_id, type="function", function=SimpleNamespace(name=name, arguments=arguments))


def response_tool_call(call_id: str, name: str, arguments: str):
    return SimpleNamespace(type="function_call", call_id=call_id, name=name, arguments=arguments)


def test_get_openai_client_falls_back_to_ssm_and_caches(mocker):
    get_ssm_parameter = mocker.patch.object(openai_helper, "get_ssm_parameter", return_value="ssm-key")
    openai = mocker.patch.object(openai_helper, "OpenAI")

    assert openai_helper.get_openai_client() is openai_helper.get_openai_client()

    get_ssm_parameter.assert_called_once_with("openai/api-key")
    openai.assert_called_once_with(
        api_key="ssm-key",
        base_url=None,
        default_headers={"User-Agent": openai_helper.DEFAULT_USER_AGENT},
    )


def test_get_openai_client_prefers_env_key(mocker, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    get_ssm_parameter = mocker.patch.object(openai_helper, "get_ssm_parameter")
    openai = mocker.patch.object(openai_helper, "OpenAI")

    openai_helper.get_openai_client()

    get_ssm_parameter.assert_not_called()
    assert openai.call_args.kwargs["api_key"] == "env-key"


def test_generate_response_uses_main_model(mocker):
    client = Mock()
    client.responses.create.return_value = response("analysis")
    mocker.patch.object(openai_helper, "get_openai_client", return_value=client)
    mocker.patch.object(openai_helper, "search_stock_by_market", return_value="")

    assert openai_helper.generate_openai_technical_analysis_response("stock data") == "analysis"

    request = client.responses.create.call_args.kwargs
    assert request["model"] == openai_helper.main_model
    assert request["tools"] == openai_helper.WEB_SEARCH_TOOLS
    assert all("name" in tool for tool in request["tools"])
    assert request["reasoning"] == {"effort": "none"}


def test_generate_response_runs_tool_calls(mocker):
    client = Mock()
    client.responses.create.side_effect = [
        response(output=[response_tool_call("c1", "web_search", '{"query": "tsmc"}')]),
        response("final"),
    ]
    mocker.patch.object(openai_helper, "get_openai_client", return_value=client)
    run_tool = mocker.patch.object(openai_helper, "_run_tool", return_value="result")

    assert openai_helper.generate_openai_technical_analysis_response("stock data") == "final"

    run_tool.assert_called_once_with("web_search", {"query": "tsmc"})
    second_messages = client.responses.create.call_args_list[1].kwargs["input"]
    assert second_messages[-1] == {"type": "function_call_output", "call_id": "c1", "output": "result"}


def test_infer_line_command_returns_high_confidence_candidate(mocker):
    client = Mock()
    client.chat.completions.create.return_value = completion('{"candidates":[{"command":"#2330","text":"台積電報價","confidence":0.95}]}')
    mocker.patch.object(openai_helper, "get_openai_client", return_value=client)

    assert openai_helper.infer_line_command("台積電多少") == "#2330"


def test_infer_line_command_ignores_low_confidence(mocker):
    client = Mock()
    client.chat.completions.create.return_value = completion('{"candidates":[{"command":"#2330","text":"台積電報價","confidence":0.3}]}')
    mocker.patch.object(openai_helper, "get_openai_client", return_value=client)

    assert openai_helper.infer_line_command("hmm") is None


def test_infer_line_candidates_returns_empty_on_failure(mocker):
    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError("boom")
    mocker.patch.object(openai_helper, "get_openai_client", return_value=client)

    assert openai_helper.infer_line_candidate_commands("台積電") == []
