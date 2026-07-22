import logging

from groq import Groq

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)
client = None

main_model = "openai/gpt-oss-20b"
fallback_model = "llama-3.1-8b-instant"


def get_groq_client():
    global client
    if client is None:
        client = Groq(api_key=get_ssm_parameter("groq/api-key"))
    return client


def generate_groq_technical_analysis_response(prompt_content: str) -> str:
    contents = (
        "根據以下資料用基本面與技術分析這檔股票目前狀況，基本面需要提供具體數字，"
        f"不要提及資料來源，內容要在500字內，不需要提醒投資者任何警語:\n {prompt_content}"
    )
    groq_client = get_groq_client()

    try:
        response = groq_client.chat.completions.create(
            model=main_model,
            messages=[{"role": "user", "content": contents}],
        )
    except Exception as error:
        logger.exception(error)
        response = groq_client.chat.completions.create(
            model=fallback_model,
            messages=[{"role": "user", "content": contents}],
        )

    return response.choices[0].message.content or ""
