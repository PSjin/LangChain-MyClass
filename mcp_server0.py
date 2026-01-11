from fastmcp import FastMCP
from dotenv import load_dotenv
from notion_client import Client
import json
import os
import sys

# 1. 환경 변수 로드
load_dotenv()

mcp = FastMCP("ExperimentResultServer")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")

# 2. 클라이언트 초기화 (토큰이 없어도 서버가 죽지 않게 예외 처리)
notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

@mcp.tool()
def read_experiment_result(file_path: str) -> dict:
    """모델 학습 결과 JSON 파일을 읽어 반환합니다."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"파일 읽기 실패: {str(e)}"}

@mcp.tool()
def upload_experiment_to_notion(title: str, summary: str) -> str:
    """요약된 결과를 Notion으로 업로드합니다."""
    if not notion:
        return "❌ Notion 토큰이 설정되지 않았습니다."
    
    try:
        # ID 정제 로직 (에러의 핵심 원인 해결)
        clean_id = NOTION_PAGE_ID.replace("-", "")
        if len(clean_id) > 32:
            clean_id = clean_id[-32:]

        notion.pages.create(
            parent={"page_id": clean_id},
            properties={
                "title": {"title": [{"text": {"content": title}}]}
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": summary}}]
                    }
                }
            ]
        )
        return "✅ Notion 업로드 완료"
    except Exception as e:
        return f"❌ 업로드 실패: {str(e)}"

if __name__ == "__main__":
    # 절대 주의: stdio 통신 중에는 print()를 사용하면 안 됩니다.
    mcp.run(transport="stdio")