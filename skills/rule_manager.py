import os

def fetch_and_update_rules(topic: str, target_file: str):
    """
    인터넷에서 특정 주제(topic)의 최신 코딩 규칙(Best Practices)을 검색하여
    규칙 파일(target_file)을 업데이트하거나 생성합니다.
    (실제 구현은 Agent가 web_fetch 도구를 사용하여 내용을 가져온 뒤 이 함수를 통해 파일에 씀)
    """
    # 이 함수는 에이전트가 내용을 이미 정리해서 'content'로 넘겨준다고 가정하고
    # 파일을 쓰는 역할에 집중하거나, 혹은 직접 검색 로직을 가질 수도 있습니다.
    # 현재 구조에서는 에이전트가 '검색 -> 요약 -> 파일작성' 흐름을 타므로,
    # 여기서는 상징적인 헬퍼 함수로 둡니다.

def apply_cursor_rules(content: str, rule_name: str):
    """
    가져온 규칙 내용을 .cursor/rules/ 폴더에 저장합니다.
    """
    rule_dir = "rules"
    if not os.path.exists(rule_dir):
        os.makedirs(rule_dir)
        
    file_path = os.path.join(rule_dir, rule_name)
    
    # 헤더 추가 (.mdc 포맷)
    formatted_content = f"""---
alwaysApply: true
---

# {rule_name.replace('.mdc', '').replace('-', ' ').title()}

{content}
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    
    return f"Rule updated: {file_path}"
