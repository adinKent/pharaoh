import logging

from google import genai

from utils.aws_helper import get_ssm_parameter

logger = logging.getLogger(__name__)
client = None

main_model = "gemini-3.5-flash"
fallback_model = "gemini-3.1-flash-lite"


def get_gemini_client():
    global client
    if client is None:
        client = genai.Client(api_key=get_ssm_parameter("google/gemini-api-key"))
    return client


def generate_gemini_technical_analysis_response(prompt_content: str) -> str:
    global main_model, fallback_model
    contents = f"根據以下資料用基本面與技術分析這檔股票目前狀況，基本面必需強調財務與股利面的數字，內容要在200字內:\n {prompt_content}"
    gemini_client = get_gemini_client()
    try:
        response = gemini_client.models.generate_content(
            model=main_model,
            contents=contents,
        )
    except Exception as e:
        # Sometimes 503 error occurs since model is currently experiencing high demand. Spikes in demand are usually temporary.
        # Use fallback model to send prompt again.
        logger.exception(e)
        response = gemini_client.models.generate_content(
            model=fallback_model,
            contents=contents,
        )

    return response.text
