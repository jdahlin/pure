from pure_validator.ir import (
    FunctionCall,
    FunctionReference,
    Module,
    VariableReference,
)
from pure_validator.ir_constructor import is_pure_builtin
from pure_validator.message import Loc, Message
from pure_validator.purity_types import PuritySource, PurityStatus


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
        # Compute-only entry point (no messages). Public for tests/other callers.
        return self._compute_purity(func_ref)

    def _compute_purity(self, func_ref: FunctionReference) -> bool:
        func_key = self.get_function_key(func_ref)
        if func_key in self.call_stack:
            # Recursion cycle encountered; only trust user-mark
            if func_ref.is_pure_marked:
                if func_ref.purity_source is PuritySource.UNKNOWN:
                    func_ref.purity_source = PuritySource.DEFERRED
                func_ref.purity_status = PurityStatus.PURE
                self.pure_functions.add(func_key)
                return True
            func_ref.purity_status = PurityStatus.IMPURE
            if func_ref.purity_source is PuritySource.UNKNOWN:
                func_ref.purity_source = PuritySource.IMPLICIT
            return False
        if func_key in self.visited_functions:
            return func_key in self.pure_functions
        self.visited_functions.add(func_key)
        self.call_stack.add(func_key)

        try:
            # Global variables (declared via 'global') make a function impure
            for var_ref in func_ref.variables:
                if var_ref.from_global_stmt and var_ref.is_global and not is_pure_builtin(var_ref.name):
                    func_ref.purity_status = PurityStatus.IMPURE
                    if func_ref.purity_source is PuritySource.UNKNOWN:
                        func_ref.purity_source = PuritySource.IMPLICIT
                    return False

            # Check all calls
            for func_call in func_ref.calls:
                called = func_call.function_ref
                if is_pure_builtin(called.name):
                    called.purity_status = PurityStatus.PURE
                    called.purity_source = PuritySource.BUILTIN
                    continue
                if called.loc is None:
                    called.purity_status = PurityStatus.IMPURE
                    called.purity_source = PuritySource.EXTERNAL
                    func_ref.purity_status = PurityStatus.IMPURE
                    if func_ref.purity_source is PuritySource.UNKNOWN:
                        func_ref.purity_source = PuritySource.IMPLICIT
                    return False
                if not self._compute_purity(called):
                    func_ref.purity_status = PurityStatus.IMPURE
                    if func_ref.purity_source is PuritySource.UNKNOWN:
                        func_ref.purity_source = PuritySource.IMPLICIT
                    return False

            self.pure_functions.add(func_key)
            func_ref.purity_status = PurityStatus.PURE
            if func_ref.is_pure_marked:
                if func_ref.purity_source not in (PuritySource.USER_MARK, PuritySource.DEFERRED):
                    func_ref.purity_source = PuritySource.USER_MARK
            else:
                if func_ref.purity_source is PuritySource.UNKNOWN:
                    func_ref.purity_source = PuritySource.IMPLICIT
            return True
        finally:
            self.call_stack.remove(func_key)

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
        var_name: str,
        loc: Loc,
    ) -> None:
        self.msg(
            f"Function '{func_ref.name}' uses global variable '{var_name}'",
            loc=loc,
        )

    def check(self) -> None:
        roots = [f for f in self.module.functions.values() if f.is_pure_marked]
        for root in roots:
            self._compute_purity(root)
        for root in roots:
            for var_ref in root.variables:
                if (
                    var_ref.from_global_stmt
                    and var_ref.is_global
                    and not is_pure_builtin(var_ref.name)
                    and var_ref.loc
                ):
                    self._report_global_variable_usage(root, var_ref.name, var_ref.loc)
            for func_call in root.calls:
                callee = func_call.function_ref
                if is_pure_builtin(callee.name):
                    continue
                if self.get_function_key(callee) == self.get_function_key(root):
                    continue
                if callee.loc is not None and callee.purity_status is not PurityStatus.PURE:
                    self._report_impure_call(root, func_call, "non-pure function")
                elif callee.loc is None:
                    self._report_impure_call(root, func_call, "impure function")
