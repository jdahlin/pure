import ast
import pathlib

from pure_validator.builtins import pure_builtins
from pure_validator.ir import (
    Class,
    FunctionCall,
    FunctionReference,
    Module,
    VariableReference,
)
from pure_validator.message import Loc
from pure_validator.purity_types import PuritySource


def is_global(
    name: str,
    local_vars: set[str],
    args: dict[str, str | None],
) -> bool:
    if name in pure_builtins:
        return False
    return name not in local_vars and name not in args


def is_pure_builtin(name: str) -> bool:
    return name in pure_builtins


class IRConstructor(ast.NodeVisitor):
    def __init__(self, path: pathlib.Path, source: str) -> None:
        super().__init__()
        self.source_lines = ["", *source.splitlines()]
        self.path = path
        self.local_vars = set()
        self.args = {}
        self.module = Module(name=path.stem, path=path)
        self.current_class: Class | None = None
        self.current_function_ref: FunctionReference | None = None

    def get_or_create_variable_ref(self, name: str, node: ast.AST) -> VariableReference:
        return VariableReference(
            name=name,
            module=self.module,
            function=self.current_function_ref,
            class_=self.current_class,
            is_global=is_global(name, self.local_vars, self.args),
            loc=Loc.from_node(self.path, node),
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = self.module.get_or_create_class_ref(node.name)
        for stmt in node.body:
            self.visit(stmt)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function_ref = self.current_function_ref
        old_local_vars = self.local_vars.copy()
        old_args = self.args.copy()
        self.local_vars = set()
        self.args = {arg.arg: None for arg in node.args.args}
        for arg in node.args.args:
            self.local_vars.add(arg.arg)
        self.current_function_ref = self.module.get_or_create_function_ref(
            node.name,
            self.current_class,
            Loc.from_node(self.path, node),
        )
        doc_string = ast.get_docstring(node)
        if doc_string and ("@pure" in doc_string or ":pure: true" in doc_string):
            self.current_function_ref.is_pure_marked = True
            self.current_function_ref.purity_source = PuritySource.USER_MARK
        for line in [node.lineno, node.lineno + 1]:
            if "# pragma: pure" in self.source_lines[line]:
                self.current_function_ref.is_pure_marked = True
                self.current_function_ref.purity_source = PuritySource.USER_MARK

        for stmt in node.body:
            self.visit(stmt)
        self.current_function_ref = old_function_ref
        self.local_vars = old_local_vars
        self.args = old_args

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            match target:
                case ast.Name() as name if func := self.current_function_ref:
                    self.local_vars.add(name.id)
                    var_ref = self.get_or_create_variable_ref(name.id, name)
                    if var_ref not in func.variables:
                        func.variables.append(var_ref)
                case ast.Attribute(ast.Name() as obj_name, attr="pure"):
                    func_ref = self.module.get_or_create_function_ref(
                        obj_name.id,
                        self.current_class,
                    )
                    func_ref.is_pure_marked = True
                    func_ref.purity_source = PuritySource.USER_MARK
        self.visit(node.value)

    def visit_Name(self, node: ast.Name) -> None:
        if not isinstance(node.ctx, ast.Load):
            return
        if is_pure_builtin(node.id):
            return
        if node.id in self.module.functions:
            return
        if not (func := self.current_function_ref):
            return
        var_ref = self.get_or_create_variable_ref(node.id, node)
        if var_ref not in func.variables:
            func.variables.append(var_ref)

    def visit_Call(self, node: ast.Call) -> None:
        match node.func:
            case ast.Name() as name:
                func_name = name.id
            case ast.Attribute(attr=ast.Name()):
                func_name = f"{node.func.value.id}.{node.func.attr}"
            case _:
                func_name = None
        if func_name and not is_pure_builtin(func_name):
            func_call = FunctionCall(
                function_ref=self.module.get_or_create_function_ref(func_name),
                loc=Loc.from_node(self.path, node),
            )
            if (func := self.current_function_ref) and func_call not in func.calls:
                func.calls.append(func_call)
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            if not (func := self.current_function_ref):
                continue
            var_ref = self.get_or_create_variable_ref(name, node)
            var_ref.is_global = True
            var_ref.from_global_stmt = True
            if var_ref not in func.variables:
                func.variables.append(var_ref)
