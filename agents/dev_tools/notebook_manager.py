import subprocess
import requests
from typing import Dict, List

class NotebookManager:
    """
    [OMNI-NotebookManager v1.1]
    Google NotebookLM Enterprise API (v1alpha) 정석 규격을 준수합니다.
    """
    def __init__(self, project_number: str = "242599127465", location: str = "global"):
        self.project_number = project_number
        self.location = location
        # v1alpha 엔드포인트
        self.base_url = f"https://{location}-discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/{location}/notebooks"

    def _get_access_token(self) -> str:
        try:
            gcloud_cmd = r"C:\Users\d0419\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
            token = subprocess.check_output([gcloud_cmd, "auth", "print-access-token"], text=True).strip()
            return token
        except Exception as e:
            print(f"❌ 토큰 획득 실패: {e}")
            return ""

    def create_notebook(self, title: str) -> Dict:
        """새로운 NotebookLM 전략 노트북 생성 (정석 규격)"""
        token = self._get_access_token()
        if not token:
            return {"error": "No auth token"}

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": "gen-lang-client-0654094816"
        }
        
        # 문서 기반 확인된 규격: { "title": "..." }
        payload = {
            "title": title
        }

        print(f"📡 NotebookLM에 노트북 생성 중: {title}...")
        response = requests.post(self.base_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 노트북 생성 성공: {result.get('name')}")
            return result
        else:
            # 에러 상세 분석 출력
            print(f"❌ 생성 실패 ({response.status_code}): {response.text}")
            return {"error": response.text}

    def list_notebooks(self) -> List[Dict]:
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}", "X-Goog-User-Project": "gen-lang-client-0654094816"}
        response = requests.get(self.base_url, headers=headers)
        if response.status_code == 200:
            return response.json().get("notebooks", [])
        return []

if __name__ == "__main__":
    manager = NotebookManager()
    print("✨ NotebookManager v1.1: Standardized & Ready.")