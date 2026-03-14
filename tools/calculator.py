"""Calculator tool: percentage change, growth rates, financial ratio calculations."""

import ast
import operator
from langchain_core.tools import tool

# Only allow safe math operations
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand)
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op = ALLOWED_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError("Operator not allowed")
        return op(left, right)
    raise ValueError("Unsupported expression")


def _safe_eval(expr: str) -> float:
    """Evaluate a numeric expression (numbers and + - * / // ** only)."""
    tree = ast.parse(expr.strip(), mode="eval")
    if not isinstance(tree.body, (ast.BinOp, ast.UnaryOp, ast.Constant)):
        raise ValueError("Only numeric expressions allowed")
    return _eval_node(tree.body)


@tool
def financial_calculator(
    operation: str,
    value1: float | None = None,
    value2: float | None = None,
    expression: str | None = None,
) -> str:
    """Perform financial numeric operations: percentage change, growth rates, ratios, or a math expression.

    operation: one of 'percent_change', 'growth_rate', 'ratio', or 'expression'.
    For percent_change: set value1=old_value, value2=new_value. Returns (new-old)/old * 100.
    For growth_rate: set value1=earlier, value2=later (e.g. revenue). Returns (v2/v1 - 1) * 100.
    For ratio: set value1=numerator, value2=denominator.
    For expression: set expression to a math string (e.g. '(250-200)/200', '100 * 1.05'). Only + - * / ** allowed.
    """
    operation = (operation or "").strip().lower()
    if not operation:
        return "Error: operation is required (percent_change, growth_rate, ratio, or expression)."

    try:
        if operation == "expression":
            if not expression:
                return "Error: for 'expression' set the 'expression' parameter (e.g. '(250-200)/200')."
            result = _safe_eval(expression.strip())
            return f"Result: {result}"
        if operation == "percent_change":
            if value1 is None or value2 is None:
                return "Error: percent_change requires value1 (old) and value2 (new)."
            if value1 == 0:
                return "Error: value1 (old) cannot be zero."
            pct = (value2 - value1) / value1 * 100
            return f"Percent change: {pct:.2f}%"
        if operation == "growth_rate":
            if value1 is None or value2 is None:
                return "Error: growth_rate requires value1 and value2."
            if value1 == 0:
                return "Error: value1 cannot be zero."
            rate = (value2 / value1 - 1) * 100
            return f"Growth rate: {rate:.2f}%"
        if operation == "ratio":
            if value1 is None or value2 is None:
                return "Error: ratio requires value1 (numerator) and value2 (denominator)."
            if value2 == 0:
                return "Error: value2 (denominator) cannot be zero."
            return f"Ratio: {value1 / value2:.4f}"
        return f"Error: unknown operation '{operation}'. Use percent_change, growth_rate, ratio, or expression."
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"
