import os
import re
from pathlib import Path

class StyleScrubber:
    """
    [OMNI-Scrubber v1.2]
    Diamond-Standard Style Enforcer with Self-Awareness.
    Prevents breaking comments and regex patterns.
    """
    def __init__(self, target_dir="."):
        self.target_dir = Path(target_dir)
        self.exclude_dirs = ["venv", ".git", "__pycache__", "docs", "archive", "tmp"]

    def scrub_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        modified = False

        for line in lines:
            original_line = line
            
            # 주석 라인은 건드리지 않음 (가장 중요한 안전 장치)
            if line.strip().startswith('#'):
                new_lines.append(line)
                continue

            indent = len(line) - len(line.lstrip())
            spacing = " " * indent
            
            # 1. Fix Bare except: -> except Exception:
            if re.search(r'^\s*except:\s*$', line):
                line = line.replace('except:', 'except Exception:')
            
            # 2. Fix except: statement -> except Exception: 
            # statement
            elif re.search(r'^\s*except:\s+[^\s]', line):
                line = line.replace('except:', 'except Exception:\n' + spacing + '    ')
                modified = True

            # 3. Fix if/elif/else cond: statement -> Expand to 2 lines
            # re.search 등을 포함한 복잡한 라인은 무시
            one_liner_match = re.search(r'^(\s*(?:if|elif|else|with|for|while).*?:)\s*([^\s].*)$', line)
            if one_liner_match and 're.search' not in line:
                prefix = one_liner_match.group(1)
                statement = one_liner_match.group(2).strip()
                if not (statement.startswith('st.') or statement.startswith('components.')):
                    line = f"{prefix}\n{spacing}    {statement}\n"
                    modified = True

            # 4. Fix semicolons (stmt1; stmt2) -> 2 lines
            # 문자열이나 정규표현식 내의 세미콜론은 무시
            if ';' in line and not any(q in line for q in ['"', "'", "r'"]):
                parts = line.split(';')
                line = f"\n{spacing}    ".join([p.strip() for p in parts]) + "\n"
                modified = True

            new_lines.append(line)
            if line != original_line:
                modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
        return False

    def run(self):
        print(f"🧼 [OMNI-Scrubber] Deep cleaning in {self.target_dir.absolute()}...")
        count = 0
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    if self.scrub_file(full_path):
                        print(f"  ✨ Cleaned: {full_path}")
                        count += 1
        print(f"✅ Scrubbing complete. {count} files polished.")

if __name__ == "__main__":
    scrubber = StyleScrubber()
    scrubber.run()
