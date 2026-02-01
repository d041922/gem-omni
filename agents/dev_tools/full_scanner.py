"""
Full Project Scanner [Safe Edition]
Scans codebase for anti-patterns with safe AST parsing.
"""
import ast
import os
from typing import Dict, List

class ProjectScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.issues = []

    def scan_project(self) -> Dict[str, List[str]]:
        target_dirs = ["pages", "skills", "agents"]
        for d in target_dirs:
            p = os.path.join(self.root_dir, d)
            if not os.path.exists(p):
                continue
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith(".py"):
                        self._scan_file(os.path.join(root, f))
        return self._generate_report()

    def _scan_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                # Safe checks
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'button':
                    if not any(k.arg == 'key' for k in node.keywords):
                        self.issues.append(f"[UX_TEST] {os.path.basename(path)}:{node.lineno} - Missing key")
        except Exception:
            pass

    def _generate_report(self) -> Dict[str, List[str]]:
        report = {}
        for issue in self.issues:
            fname = issue.split(' ')[1].split(':')[0]
            if fname not in report:
                report[fname] = []
            report[fname].append(issue)
        return report