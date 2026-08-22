import logging

from openai import OpenAI

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)
client = None

base_url = "https://opencode.ai/zen/go/v1"
main_model = "glm-5.3"
fallback_model = "kimi-k2.7-code"


def get_opencode_client():
    global client
    if client is None:
        client = OpenAI(
            api_key=get_ssm_parameter("opencode/api-key"),
            base_url=base_url,
        )
    return client


def generate_opencode_technical_analysis_response(prompt_content: str) -> str:
    contents = (
        "根據以下資料用技術分析與基本面分析這檔股票，技術分析為主，基本面需要提供具體數字，"
        f"不要提及資料來源，不要markdown格式，內容要在500字內，不需要提醒投資者任何警語:\n {prompt_content}"
    )
    opencode_client = get_opencode_client()

    try:
        response = opencode_client.chat.completions.create(
            model=main_model,
            messages=[{"role": "user", "content": contents}],
        )
    except Exception as error:
        logger.exception(error)
        response = opencode_client.chat.completions.create(
            model=fallback_model,
            messages=[{"role": "user", "content": contents}],
        )

    return response.choices[0].message.content or ""
