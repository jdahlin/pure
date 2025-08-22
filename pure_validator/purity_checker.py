from pure_validator.ir import (
    FunctionCall,
    FunctionReference,
    Module,
    VariableReference,
)
from pure_validator.ir_constructor import is_pure_builtin
from pure_validator.message import Loc, Message


class PurityChecker:
    def __init__(self, module: Module):
        self.module = module
        self.messages: list[Message] = []
        self.visited_functions: set[str] = set()
        self.pure_functions: set[str] = set()
        self.call_stack: set[str] = set()

    def msg(self, message: str, *, loc: Loc) -> None:
        self.messages.append(Message(message=message, loc=loc))

    def get_function_key(self, func_ref: FunctionReference) -> str:
        if func_ref.class_ is not None:
            return f"{func_ref.class_.name}.{func_ref.name}"
        return func_ref.name

    def check_function_purity(self, func_ref: FunctionReference) -> bool:
        func_key = self.get_function_key(func_ref)
        if func_key in self.call_stack:
            return func_ref.is_pure_marked
        if func_key in self.visited_functions:
            return func_key in self.pure_functions
        self.visited_functions.add(func_key)
        self.call_stack.add(func_key)

        try:
            is_pure = self._analyze_function_purity(func_ref)
            if is_pure:
                self.pure_functions.add(func_key)
            return is_pure
        finally:
            self.call_stack.remove(func_key)

    def _analyze_function_purity(self, func_ref: FunctionReference) -> bool:
        return self._check_function_calls(func_ref) and self._check_global_variables(
            func_ref,
        )

    def _check_function_calls(self, func_ref: FunctionReference) -> bool:
        for func_call in func_ref.calls:
            if not self._is_function_call_pure(func_ref, func_call):
                return False
        return True

    def _is_function_call_pure(
        self,
        caller: FunctionReference,
        func_call: FunctionCall,
    ) -> bool:
        called_func = func_call.function_ref
        called_key = self.get_function_key(called_func)
        if is_pure_builtin(called_func.name):
            return True
        if not called_func.is_pure_marked and called_key not in self.module.functions:
            self._report_impure_call(caller, func_call, "impure function")
            return False
        if called_func.is_pure_marked:
            if not self.check_function_purity(called_func):
                self._report_impure_call(caller, func_call, "impure function")
                return False
        else:
            self._report_impure_call(caller, func_call, "non-pure function")
            return False
        return True

    def _check_global_variables(self, func_ref: FunctionReference) -> bool:
        lacks_globals = True
        for var_ref in func_ref.variables:
            if is_pure_builtin(var_ref.name) or not var_ref.is_global:
                continue
            self._report_global_variable_usage(func_ref, var_ref)
            lacks_globals = False
        return lacks_globals

    def _report_impure_call(
        self,
        caller: FunctionReference,
        func_call: FunctionCall,
        reason: str,
    ) -> None:
        if not func_call.loc:
            return
        self.msg(
            f"Function '{caller.name}' calls {reason} '{func_call.function_ref.name}'",
            loc=func_call.loc,
        )

    def _report_global_variable_usage(
        self,
        func_ref: FunctionReference,
        var_ref: VariableReference,
    ) -> None:
        if not var_ref.loc:
            return
        self.msg(
            f"Function '{func_ref.name}' uses global variable '{var_ref.name}'",
            loc=var_ref.loc,
        )

    def check(self) -> None:
        for func_ref in self.module.functions.values():
            if func_ref.is_pure_marked:
                self.check_function_purity(func_ref)
