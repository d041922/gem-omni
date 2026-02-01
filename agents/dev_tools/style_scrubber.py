import os
import re
from pathlib import Path

class StyleScrubber:
    """
    [OMNI-Scrubber] Diamond-Standard Style Enforcer
    Automatically fixes E701 (One-liners) and E722 (Bare except).
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
            indent = len(line) - len(line.lstrip())
            spacing = " " * indent
            
            # 1. Fix Bare except: -> except Exception: (Safe Match)
            if re.search(r'^\s*except:\s*$', line):
                line = line.replace('except:', 'except Exception:')
            
            # 2. Fix except: statement -> except Exception: \n statement
            elif re.search(r'^\s*except:\s+[^\s]', line):
                line = line.replace('except:', 'except Exception:\n' + spacing + '    ')
                modified = True

            # 3. Fix if/elif/else cond: statement -> Expand to 2 lines
            # Using simpler regex to avoid breaking the scrubber itself
            one_liner_match = re.search(r'^(\s*(?:if|elif|else|with|for|while).*?:)\s*([^\s].*)$', line)
            if one_liner_match:
                prefix = one_liner_match.group(1)
                statement = one_liner_match.group(2).strip()
                # Skip if it's already a multi-line structure or regex
                if not (statement.startswith('st.') or 're.search' in line or statement.startswith('components.')):
                    line = f"{prefix}\n{spacing}    {statement}\n"
                    modified = True

            # 4. Fix semicolons (stmt1; stmt2) -> 2 lines
            if ';' in line and not ('"' in line or "'" in line or 'r\'' in line):
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
        print(f"🧼 [OMNI-Scrubber] Starting deep cleaning in {self.target_dir.absolute()}...")
        count = 0
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    if self.scrub_file(full_path):
                        print(f"  ✨ Cleaned: {full_path}")
                        count += 1
        print(f"✅ Scrubbing complete. {count} files polished to Diamond-Standard.")

if __name__ == "__main__":
    scrubber = StyleScrubber()
    scrubber.run()