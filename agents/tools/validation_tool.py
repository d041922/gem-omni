"""
Portfolio Validation Tool for CrewAI
4-Step Validation System inspired by ppt_team_agent

Validates portfolio analysis results for:
1. Data Integrity
2. Numeric Sanity
3. Risk Limits
4. Output Format
"""
from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
from pydantic import BaseModel, Field


class ValidationInput(BaseModel):
    """Input schema for Validation Tool"""
    analysis_result: Dict[str, Any] = Field(..., description="Portfolio analysis result to validate")
    validation_level: str = Field(default="strict", description="Validation level: strict, normal, lenient")


class PortfolioValidationTool(BaseTool):
    name: str = "Validate Portfolio Analysis"
    description: str = (
        "Validates portfolio analysis results using a 4-step validation system. "
        "Checks data integrity, numeric sanity, risk limits, and output format. "
        "Returns all errors at once for comprehensive review (multi-error detection pattern). "
        "Use this tool to ensure analysis quality before presenting to user."
    )
    args_schema: Type[BaseModel] = ValidationInput

    def _run(
        self,
        analysis_result: Dict[str, Any],
        validation_level: str = "strict"
    ) -> Dict[str, Any]:
        """
        Validate portfolio analysis (4-Step System)

        Args:
            analysis_result: Analysis result dictionary
            validation_level: strict, normal, or lenient

        Returns:
            Dictionary with validation status and errors
        """
        errors = []
        warnings = []

        # Step 1: Data Integrity Validation
        integrity_errors = self._validate_data_integrity(analysis_result)
        errors.extend(integrity_errors)

        # Step 2: Numeric Sanity Validation
        sanity_errors = self._validate_numeric_sanity(analysis_result, validation_level)
        errors.extend(sanity_errors)

        # Step 3: Risk Limits Validation
        risk_errors, risk_warnings = self._validate_risk_limits(analysis_result, validation_level)
        errors.extend(risk_errors)
        warnings.extend(risk_warnings)

        # Step 4: Output Format Validation
        format_errors = self._validate_output_format(analysis_result)
        errors.extend(format_errors)

        # Return all errors at once (ppt_team_agent pattern)
        return {
            "success": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "validated_result": analysis_result if len(errors) == 0 else None,
            "message": self._generate_validation_message(errors, warnings)
        }

    def _validate_data_integrity(self, result: Dict[str, Any]) -> List[str]:
        """Step 1: Data Integrity Check"""
        errors = []

        # Check required fields
        if 'summary' not in result:
            errors.append("Missing 'summary' field in analysis result")
            return errors  # Cannot continue without summary

        summary = result['summary']

        # Required metrics
        required_fields = ['total_cost_krw', 'total_eval_krw', 'total_profit_krw', 'total_return_pct']
        for field in required_fields:
            if field not in summary:
                errors.append(f"Missing required field: {field}")

        # Check calculation integrity
        if all(f in summary for f in required_fields):
            total_cost = summary['total_cost_krw']
            total_eval = summary['total_eval_krw']
            total_profit = summary['total_profit_krw']

            # Formula: 매수금액 + 손익 = 평가금액
            expected_eval = total_cost + total_profit
            tolerance = max(1, abs(expected_eval) * 0.0001)  # 0.01% tolerance

            if abs(expected_eval - total_eval) > tolerance:
                errors.append(
                    f"Data integrity check failed: "
                    f"Cost({total_cost:,.0f}) + Profit({total_profit:,.0f}) "
                    f"!= Evaluation({total_eval:,.0f}). "
                    f"Difference: {abs(expected_eval - total_eval):,.0f} KRW"
                )

        return errors

    def _validate_numeric_sanity(self, result: Dict[str, Any], level: str) -> List[str]:
        """Step 2: Numeric Sanity Check"""
        errors = []

        if 'summary' not in result:
            return errors

        summary = result['summary']

        # Return rate sanity check
        if 'total_return_pct' in summary:
            return_pct = summary['total_return_pct']

            # Realistic range: -99% to +1000%
            if return_pct < -99:
                errors.append(f"Unrealistic return: {return_pct:.2f}% (< -99%)")
            elif return_pct > 1000:
                errors.append(f"Unrealistic return: {return_pct:.2f}% (> 1000%)")

        # Amount sanity check
        amount_fields = ['total_cost_krw', 'total_eval_krw', 'total_profit_krw']
        for field in amount_fields:
            if field in summary:
                amount = summary[field]
                if abs(amount) > 10_000_000_000:  # 100억
                    if level == "strict":
                        errors.append(f"{field}: {amount:,.0f} exceeds 100억 (sanity check)")

        # Beta sanity check (if present)
        if 'portfolio_beta' in summary:
            beta = summary['portfolio_beta']
            if beta < -2 or beta > 3:
                errors.append(f"Unrealistic beta: {beta:.2f} (range: -2 to 3)")

        # Sharpe ratio sanity check
        if 'sharpe_ratio' in summary:
            sharpe = summary['sharpe_ratio']
            if sharpe < -5 or sharpe > 10:
                errors.append(f"Unrealistic Sharpe ratio: {sharpe:.2f} (range: -5 to 10)")

        return errors

    def _validate_risk_limits(
        self,
        result: Dict[str, Any],
        level: str
    ) -> tuple[List[str], List[str]]:
        """Step 3: Risk Limits Check"""
        errors = []
        warnings = []

        if 'summary' not in result:
            return errors, warnings

        summary = result['summary']

        # Single position concentration risk
        if 'max_position_pct' in summary:
            max_position = summary['max_position_pct']

            if max_position > 20:
                errors.append(
                    f"⚠️ RISK LIMIT EXCEEDED: "
                    f"Max position {max_position:.1f}% > 20% (extreme concentration)"
                )
            elif max_position > 15:
                warnings.append(
                    f"⚠️ Risk warning: Max position {max_position:.1f}% > 15% (recommended limit)"
                )

        # Top 3 concentration risk
        if 'concentration_risk' in summary:
            top3 = summary['concentration_risk']
            if top3 > 50:
                errors.append(
                    f"⚠️ RISK LIMIT EXCEEDED: "
                    f"Top 3 concentration {top3:.1f}% > 50% (extreme concentration)"
                )
            elif top3 > 40:
                warnings.append(
                    f"⚠️ Risk warning: Top 3 concentration {top3:.1f}% > 40% (recommended limit)"
                )

        # Portfolio beta risk
        if 'portfolio_beta' in summary:
            beta = summary['portfolio_beta']
            if beta > 1.5:
                if level == "strict":
                    errors.append(
                        f"⚠️ RISK LIMIT EXCEEDED: "
                        f"Portfolio beta {beta:.2f} > 1.5 (excessive market risk)"
                    )
                else:
                    warnings.append(
                        f"⚠️ High beta warning: {beta:.2f} > 1.5 (35%+ volatility vs market)"
                    )

        # Volatility check
        if 'volatility_pct' in summary:
            vol = summary['volatility_pct']
            if vol > 30:
                warnings.append(
                    f"⚠️ High volatility: {vol:.1f}% (consider risk tolerance)"
                )

        return errors, warnings

    def _validate_output_format(self, result: Dict[str, Any]) -> List[str]:
        """Step 4: Output Format Check"""
        errors = []

        # Check if output is dict
        if not isinstance(result, dict):
            errors.append(f"Output must be dict, got {type(result)}")
            return errors

        # Check for success field
        if 'success' not in result:
            errors.append("Missing 'success' field in output")

        # Check for file paths (token optimization)
        if 'metrics_file' in result:
            file_path = result['metrics_file']
            if not isinstance(file_path, str) or not file_path.endswith('.json'):
                errors.append(f"Invalid metrics_file format: {file_path}")

        # Check summary size (token optimization)
        if 'summary' in result:
            import json
            summary_str = json.dumps(result['summary'], ensure_ascii=False)
            summary_tokens = len(summary_str) // 4  # Rough estimation

            if summary_tokens > 1000:
                errors.append(
                    f"Summary too large: {summary_tokens} tokens (limit: 1000). "
                    f"Use file caching instead."
                )

        return errors

    def _generate_validation_message(self, errors: List[str], warnings: List[str]) -> str:
        """Generate validation result message"""
        if not errors and not warnings:
            return "✅ All validations passed"

        messages = []
        if errors:
            messages.append(f"❌ {len(errors)} error(s) found:")
            for i, error in enumerate(errors, 1):
                messages.append(f"   {i}. {error}")

        if warnings:
            messages.append(f"⚠️ {len(warnings)} warning(s):")
            for i, warning in enumerate(warnings, 1):
                messages.append(f"   {i}. {warning}")

        return "\n".join(messages)
