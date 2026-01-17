from google import genai

from src.utils.aws_helper import get_ssm_parameter

client = genai.Client(api_key=get_ssm_parameter("google/gemini-api-key"))


def generate_gemini_technical_analysis_response(prompt_content: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"根據以下資料用基本面與技術分析這檔股票目前狀況，內容要在100字內:\n {prompt_content}"
    )
    return response.text
