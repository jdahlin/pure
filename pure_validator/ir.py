import dataclasses
import pathlib

from pure_validator.message import Loc
from pure_validator.purity_types import PuritySource, PurityStatus


@dataclasses.dataclass
class Module:
    name: str
    path: pathlib.Path
    functions: dict[str, "FunctionReference"] = dataclasses.field(default_factory=dict)
    classes: dict[str, "Class"] = dataclasses.field(default_factory=dict)

    def get_or_create_function_ref(
        self,
        name: str,
        class_: "Class | None" = None,
        location: Loc | None = None,
    ) -> "FunctionReference":
        full_key = f"{class_.name}.{name}" if class_ else name
        if full_key not in self.functions:
            self.functions[full_key] = FunctionReference(
                name=name,
                module=self,
                class_=class_,
                loc=location,
            )
        return self.functions[full_key]

    def get_or_create_class_ref(self, name: str) -> "Class":
        if name not in self.classes:
            self.classes[name] = Class(name=name, module=self)
        return self.classes[name]

    def should_check_function(
        self,
        name: str,
        current_class: "Class | None" = None,
    ) -> bool:
        full_key = f"{current_class.name}.{name}" if current_class else name
        if full_key in self.functions:
            return self.functions[full_key].is_pure_marked
        return False


@dataclasses.dataclass(frozen=True)
class Class:
    name: str
    module: Module


@dataclasses.dataclass(frozen=True)
class FunctionCall:
    function_ref: "FunctionReference"
    loc: Loc


@dataclasses.dataclass
class FunctionReference:
    name: str
    module: Module
    class_: Class | None = None
    calls: list["FunctionCall"] = dataclasses.field(default_factory=list)
    variables: list["VariableReference"] = dataclasses.field(default_factory=list)
    is_pure_marked: bool = False
    loc: Loc | None = None
    purity_status: PurityStatus = PurityStatus.UNKNOWN
    purity_source: PuritySource = PuritySource.UNKNOWN


@dataclasses.dataclass
class VariableReference:
    name: str
    module: Module
    function: FunctionReference | None = None
    class_: Class | None = None
    is_global: bool = False
    loc: Loc | None = None
    from_global_stmt: bool = False

