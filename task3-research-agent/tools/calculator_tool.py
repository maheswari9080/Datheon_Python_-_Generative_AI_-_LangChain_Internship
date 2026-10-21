"""
Restricted Python Mathematical Calculator for Task 3 Agent.
Evaluates mathematical expressions strictly using AST parsing with whitelisted operators and math functions.
Never invokes raw eval() or exec(), eliminating arbitrary code execution risks.
"""

import ast
import math
import operator
from typing import Dict, Any, Callable
from pydantic import BaseModel, Field

try:
    from .base import BaseTool
except ImportError:
    from base import BaseTool


class CalculatorInput(BaseModel):
    expression: str = Field(
        description="Mathematical expression to evaluate e.g. 'sqrt(144) + 25 * 4' or '(12000 * 0.15) / 12'"
    )


class CalculatorSecurityError(Exception):
    """Raised when an expression attempts unsafe operations, imports, or attributes."""
    pass


# Whitelisted safe math functions and constants
SAFE_FUNCTIONS: Dict[str, Callable] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
}

SAFE_CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}

# Whitelisted binary operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

SAFE_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    """Recursively evaluates an AST node strictly against safe whitelisted constructs."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise CalculatorSecurityError(f"Disallowed constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Name):
        if node.id in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[node.id]
        raise CalculatorSecurityError(f"Access to variable or identifier '{node.id}' is forbidden.")

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in SAFE_UNARY_OPERATORS:
            val = _eval_node(node.operand)
            return SAFE_UNARY_OPERATORS[op_type](val)
        raise CalculatorSecurityError(f"Disallowed unary operator: {op_type.__name__}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            
            # Guard against resource exhaustion via massive exponents
            if op_type is ast.Pow:
                if abs(right) > 100:
                    raise ValueError("Exponent exceeds maximum permitted threshold of 100.")
                if abs(left) > 100000 and right > 5:
                    raise ValueError("Base value too large for exponential computation.")

            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ZeroDivisionError("Division by zero is undefined.")

            return SAFE_OPERATORS[op_type](left, right)
        raise CalculatorSecurityError(f"Disallowed binary operator: {op_type.__name__}")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise CalculatorSecurityError("Dynamic function lookups or attribute calls are forbidden.")
        fn_name = node.func.id
        if fn_name not in SAFE_FUNCTIONS:
            raise CalculatorSecurityError(f"Function '{fn_name}' is not in the safe calculation whitelist.")
        
        args = [_eval_node(arg) for arg in node.args]
        return float(SAFE_FUNCTIONS[fn_name](*args))

    # Reject everything else (Attribute, Subscript, List, Import, Call on expr, etc.)
    raise CalculatorSecurityError(f"Disallowed syntax node '{type(node).__name__}'. Only arithmetic expressions are permitted.")


class SafeCalculatorTool(BaseTool):
    """Restricted mathematical evaluation tool running strictly under an AST sandbox."""

    name = "calculator"
    description = (
        "Calculates mathematical and arithmetic expressions safely. "
        "Supports operators (+, -, *, /, //, %, **) and functions (sqrt, sin, cos, tan, log, log10, exp, round, abs). "
        "Input must be a valid mathematical expression string e.g. 'sqrt(100) + 42'."
    )
    args_schema = CalculatorInput

    def _run(self, expression: str) -> str:
        clean_expr = expression.strip()
        if not clean_expr:
            raise ValueError("Empty calculation expression provided.")
        if len(clean_expr) > 400:
            raise ValueError("Expression length exceeds maximum safe limit of 400 characters.")

        try:
            parsed = ast.parse(clean_expr, mode="eval")
            result = _eval_node(parsed)
            # Format cleanly if whole number
            if result.is_integer():
                return str(int(result))
            return f"{result:.6f}".rstrip("0").rstrip(".")
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as e:
            return f"Calculation Error: {type(e).__name__}: {str(e)}"
        except CalculatorSecurityError as se:
            return f"Security Violation: {str(se)}"
