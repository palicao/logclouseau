import logging
from typing import Dict, Any, Callable, Tuple

from expressions import Compiler, Variable


class CompilerError(Exception):
    pass


class TokensAwareExpressionCompiler(Compiler):
    def compile_variable(
            self, tokens: Dict[str, Any], variable: Variable
    ) -> Variable:
        if variable.name not in tokens.keys():
            raise CompilerError(f'variable {variable} is not allowed')
        return variable

    @staticmethod
    def fix_types(
            a: Any, b: Any, tokens: Dict[str, Any]
    ) -> Tuple[Any, Any]:
        try:
            if isinstance(a, Variable) and isinstance(b, Variable):
                return tokens[a.name], tokens[b.name]
            elif isinstance(a, Variable) and not isinstance(b, Variable):
                type_of_b = type(b)
                return type_of_b(tokens[a.name]), b
            elif isinstance(b, Variable) and not isinstance(a, Variable):
                type_of_a = type(a)
                return a, type_of_a(tokens[b.name])
            return str(a), str(b)
        except KeyError as err:
            raise CompilerError(f'error: {err}')

    @staticmethod
    def bitwise_operation(
            op: str, a: Any, b: Any, tokens: Dict[str, Any]
    ) -> int:
        try:
            if isinstance(a, Variable):
                a = int(tokens[a.name])
            if isinstance(b, Variable):
                b = int(tokens[b.name])
            if not isinstance(a, int) or not isinstance(b, int):
                raise CompilerError(
                    'bitwise or is only allowed between integers')
            if op == '|':
                return a | b
            return a & b
        except KeyError as err:
            raise CompilerError(f'error: {err}')

    @staticmethod
    def in_operation(a: Any, b: Any, tokens: Dict[str, Any]) -> bool:
        try:
            if isinstance(a, Variable):
                a = str(tokens[a.name])
            if isinstance(b, Variable):
                b = str(tokens[b.name])
            if not isinstance(a, str) or not isinstance(b, str):
                raise CompilerError('in requires two strings as operands')
            return a in b
        except KeyError as err:
            raise CompilerError(f'error: {err}')

    def compile_binary(
            self,
            tokens: Dict[str, Any],
            operator: str,
            op1: Any,
            op2: Any
    ) -> Any:
        operations: Dict[str, Callable[[Any, Any], Any]] = {
            '+': (lambda a, b: a + b),
            '-': (lambda a, b: a - b),
            '*': (lambda a, b: a * b),
            '^': (lambda a, b: a ** b),
            '/': (lambda a, b: a / b),
            '%': (lambda a, b: a % b),
            '>': (lambda a, b: a > b),
            '>=': (lambda a, b: a >= b),
            '<': (lambda a, b: a < b),
            '<=': (lambda a, b: a <= b),
            '=': (lambda a, b: a == b),
            'is': (lambda a, b: a == b),
            '!=': (lambda a, b: a != b),
            'and': (lambda a, b: a and b),
            'or': (lambda a, b: a or b),
        }

        if operator in operations.keys():
            fix_op1, fix_op2 = self.fix_types(op1, op2, tokens)
            return operations[operator](fix_op1, fix_op2)
        elif operator in ['|', '&']:
            return self.bitwise_operation('|', op1, op2, tokens)
        elif operator == 'in':
            return self.in_operation(op1, op2, tokens)
        else:
            raise CompilerError(f'operator {operator} is not allowed')
