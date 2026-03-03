import logging

from google import genai

from utils.aws_helper import get_ssm_parameter

client = genai.Client(api_key=get_ssm_parameter("google/gemini-api-key"))

logger = logging.getLogger(__name__)


def generate_gemini_technical_analysis_response(prompt_content: str) -> str:
    contents = f"根據以下資料用基本面與技術分析這檔股票目前狀況，基本面必需強調財務與股利面的數字，內容要在200字內:\n {prompt_content}"
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=contents,
        )
    except Exception as e:
        # Sometimes 503 error occurs since model is currently experiencing high demand. Spikes in demand are usually temporary.
        # Use fallback model to send prompt again.
        logger.exception(e)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )

    return response.text
