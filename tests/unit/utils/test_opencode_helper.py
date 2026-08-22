from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest

from utils import opencode_helper


@pytest.fixture(autouse=True)
def reset_opencode_client():
    opencode_helper.client = None
    yield
    opencode_helper.client = None


def completion(content: str, tool_calls=None):
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls or [])
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def tool_call(call_id: str, name: str, arguments: str):
    return SimpleNamespace(
        id=call_id,
        type="function",
        function=SimpleNamespace(name=name, arguments=arguments),
    )


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
    mocker.patch.object(opencode_helper, "search_stock_by_market", return_value="")

    result = opencode_helper.generate_opencode_technical_analysis_response("stock data")

    assert result == "analysis"
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == opencode_helper.main_model
    assert request["tools"] == opencode_helper.WEB_SEARCH_TOOLS
    assert request["messages"][0]["role"] == "user"
    assert "stock data" in request["messages"][0]["content"]


def test_generate_response_prefetches_market_search(mocker):
    client = Mock()
    client.chat.completions.create.return_value = completion("analysis")
    mocker.patch.object(opencode_helper, "get_opencode_client", return_value=client)
    search = mocker.patch.object(opencode_helper, "search_stock_by_market", return_value="latest fundamentals")

    result = opencode_helper.generate_opencode_technical_analysis_response(
        "stock data",
        symbol="2330",
        market_type="TW",
        name="台積電",
    )

    assert result == "analysis"
    search.assert_called_once_with("2330", "TW", name="台積電")
    prompt = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "latest fundamentals" in prompt


def test_generate_response_handles_tool_calls(mocker):
    client = Mock()
    client.chat.completions.create.side_effect = [
        completion(
            "",
            tool_calls=[tool_call("c1", "search_us_stock", '{"symbol":"AAPL","name":"Apple"}')],
        ),
        completion("final analysis"),
    ]
    mocker.patch.object(opencode_helper, "get_opencode_client", return_value=client)
    mocker.patch.object(opencode_helper, "search_stock_by_market", return_value="")
    run_tool = mocker.patch.object(opencode_helper, "_run_tool", return_value="us data")

    result = opencode_helper.generate_opencode_technical_analysis_response(
        "stock data",
        symbol="AAPL",
        market_type="US",
        name="Apple",
    )

    assert result == "final analysis"
    run_tool.assert_called_once_with("search_us_stock", {"symbol": "AAPL", "name": "Apple"})
    second_messages = client.chat.completions.create.call_args_list[1].kwargs["messages"]
    assert second_messages[-1] == {
        "role": "tool",
        "tool_call_id": "c1",
        "content": "us data",
    }


def test_generate_response_retries_with_fallback_model(mocker):
    client = Mock()
    client.chat.completions.create.side_effect = [
        RuntimeError("primary unavailable"),
        completion("fallback analysis"),
    ]
    mocker.patch.object(opencode_helper, "get_opencode_client", return_value=client)
    mocker.patch.object(opencode_helper, "search_stock_by_market", return_value="")
    mocker.patch.object(opencode_helper.logger, "exception")

    result = opencode_helper.generate_opencode_technical_analysis_response("stock data")

    assert result == "fallback analysis"
    assert client.chat.completions.create.call_args_list == [
        call(
            model=opencode_helper.main_model,
            messages=[{"role": "user", "content": mocker.ANY}],
            tools=opencode_helper.WEB_SEARCH_TOOLS,
            tool_choice="auto",
        ),
        call(
            model=opencode_helper.fallback_model,
            messages=[{"role": "user", "content": mocker.ANY}],
            tools=opencode_helper.WEB_SEARCH_TOOLS,
            tool_choice="auto",
        ),
    ]


def test_run_tool_routes(mocker):
    mocker.patch.object(opencode_helper, "web_search", return_value="g")
    mocker.patch.object(opencode_helper, "search_tw_stock", return_value="tw")
    mocker.patch.object(opencode_helper, "search_us_stock", return_value="us")

    assert opencode_helper._run_tool("web_search", {"query": "q"}) == "g"
    assert opencode_helper._run_tool("search_tw_stock", {"symbol": "2330"}) == "tw"
    assert opencode_helper._run_tool("search_us_stock", {"symbol": "AAPL"}) == "us"
    assert "Unknown" in opencode_helper._run_tool("nope", {})
