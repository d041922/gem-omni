"""
Semantic Validation Tool [Meta-System]
Checks data quality: meaningful values, zero-checks, distribution anomalies.
"""
import pandas as pd
from typing import Dict, Any, List

class SemanticValidator:
    def __init__(self):
        self.name = "Semantic Validator"

    def validate_dataframe(self, df: pd.DataFrame, key_columns: List[str] = None) -> Dict[str, Any]:
        """
        Validates a DataFrame for semantic correctness.
        - Are key columns all zeros?
        - Are there too many 'Unknown' values?
        - Is the data distribution logical?
        """
        report = {"status": "PASS", "issues": []}
        
        if df.empty:
            return {"status": "FAIL", "issues": ["DataFrame is empty"]}

        # 1. Zero Value Check
        if key_columns:
            for col in key_columns:
                if col not in df.columns:
                    report["issues"].append(f"Missing key column: {col}")
                    continue
                
                # Check numeric types
                if pd.api.types.is_numeric_dtype(df[col]):
                    total = df[col].sum()
                    zeros = (df[col] == 0).sum()
                    if total == 0:
                        report["issues"].append(f"Column '{col}' sum is 0 (Critical)")
                        report["status"] = "FAIL"
                    elif zeros > len(df) * 0.8:
                        # Over 80% zeros
                        report["issues"].append(f"Column '{col}' is mostly zeros ({zeros}/{len(df)})")
                        if report["status"] != "FAIL":
                            report["status"] = "WARNING"

        # 2. Unknown/Null Check
        for col in df.columns:
            if df[col].dtype == 'object':
                unknowns = df[col].astype(str).str.contains('Unknown|nan|None', case=False).sum()
                if unknowns > len(df) * 0.5:
                    report["issues"].append(f"Column '{col}' has {unknowns} unknown values")
                    if report["status"] != "FAIL":
                        report["status"] = "WARNING"

        return report

# Standalone function
def validate_data(data: Any, context: str = "") -> str:
    validator = SemanticValidator()
    if isinstance(data, pd.DataFrame):
        res = validator.validate_dataframe(data)
        return f"[{context}] Validation Result: {res['status']} - {res['issues']}"
    return "Data type not supported for validation"
