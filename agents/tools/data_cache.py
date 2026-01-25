"""
Data Cache Module for Token Optimization
Saves large dataframes to files and returns only summaries to LLM agents
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


# Cache directory setup
CACHE_DIR = Path("D:/rogicx_dev/projects/GEM_OMNI/tmp/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def save_portfolio_data(df: pd.DataFrame, filename: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Save portfolio dataframe to file and return only summary (to minimize tokens)

    Args:
        df: Portfolio DataFrame
        filename: Filename to save (e.g., "portfolio.json")
        metadata: Optional metadata to include in summary

    Returns:
        Dictionary with file path and summary statistics (< 500 tokens)
    """
    if df.empty:
        return {
            "success": False,
            "file_path": None,
            "summary": {
                "total_positions": 0,
                "message": "Empty dataframe"
            }
        }

    # Save full data to file
    file_path = CACHE_DIR / filename
    df.to_json(file_path, orient='records', force_ascii=False, indent=2)

    # Generate compact summary
    summary = {
        "total_positions": len(df),
        "columns": df.columns.tolist(),
        "timestamp": datetime.now().isoformat()
    }

    # Add value metrics if available
    if '평가금액(KRW)' in df.columns:
        summary["total_value_krw"] = float(df['평가금액(KRW)'].sum())

    if '매수금액(KRW)' in df.columns:
        summary["total_cost_krw"] = float(df['매수금액(KRW)'].sum())

    if '손익(KRW)' in df.columns:
        summary["total_profit_krw"] = float(df['손익(KRW)'].sum())

    if '수익률(%)' in df.columns:
        # Calculate weighted average return
        if '매수금액(KRW)' in df.columns:
            total_cost = df['매수금액(KRW)'].sum()
            if total_cost > 0:
                weighted_return = (df['수익률(%)'] * df['매수금액(KRW)']).sum() / total_cost
                summary["avg_return_pct"] = float(weighted_return)

    # Add top 3 and bottom 3 holdings (for context)
    if '종목명' in df.columns and '수익률(%)' in df.columns:
        top_3 = df.nlargest(3, '수익률(%)')
        bottom_3 = df.nsmallest(3, '수익률(%)')

        summary["top_3_performers"] = [
            {"name": row['종목명'], "return_pct": float(row['수익률(%)'])}
            for _, row in top_3.iterrows()
        ]

        summary["bottom_3_performers"] = [
            {"name": row['종목명'], "return_pct": float(row['수익률(%)'])}
            for _, row in bottom_3.iterrows()
        ]

    # Add metadata if provided
    if metadata:
        summary["metadata"] = metadata

    return {
        "success": True,
        "file_path": str(file_path),
        "summary": summary,
        "message": f"Saved {len(df)} positions to {filename}"
    }


def load_portfolio_data(file_path: str) -> pd.DataFrame:
    """
    Load portfolio dataframe from cached file

    Args:
        file_path: Path to cached JSON file

    Returns:
        DataFrame with portfolio data
    """
    try:
        df = pd.read_json(file_path, orient='records')
        return df
    except Exception as e:
        raise ValueError(f"Failed to load portfolio data from {file_path}: {str(e)}")


def save_analysis_result(result_dict: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    Save analysis result to file and return compact reference

    Args:
        result_dict: Analysis result dictionary
        filename: Filename to save (e.g., "risk_analysis.json")

    Returns:
        Dictionary with file path and key highlights
    """
    file_path = CACHE_DIR / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)

    # Extract key highlights only
    highlights = {
        "file_path": str(file_path),
        "timestamp": datetime.now().isoformat()
    }

    # Extract top-level summary keys (avoid nested data)
    if isinstance(result_dict, dict):
        for key in ['total_value', 'total_return', 'risk_score', 'sharpe_ratio', 'beta', 'max_drawdown']:
            if key in result_dict:
                highlights[key] = result_dict[key]

    return highlights


def load_analysis_result(file_path: str) -> Dict[str, Any]:
    """
    Load analysis result from cached file

    Args:
        file_path: Path to cached JSON file

    Returns:
        Dictionary with analysis results
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        return result
    except Exception as e:
        raise ValueError(f"Failed to load analysis result from {file_path}: {str(e)}")


def get_cache_summary() -> Dict[str, Any]:
    """
    Get summary of all cached files

    Returns:
        Dictionary with cache directory info
    """
    cached_files = list(CACHE_DIR.glob("*.json"))

    return {
        "cache_dir": str(CACHE_DIR),
        "total_files": len(cached_files),
        "files": [
            {
                "name": f.name,
                "size_kb": f.stat().st_size / 1024,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in cached_files
        ]
    }


def clear_cache(older_than_hours: Optional[int] = None) -> int:
    """
    Clear cached files

    Args:
        older_than_hours: Only delete files older than N hours (None = delete all)

    Returns:
        Number of files deleted
    """
    deleted_count = 0
    current_time = datetime.now().timestamp()

    for file_path in CACHE_DIR.glob("*.json"):
        file_age_hours = (current_time - file_path.stat().st_mtime) / 3600

        if older_than_hours is None or file_age_hours > older_than_hours:
            file_path.unlink()
            deleted_count += 1

    return deleted_count
