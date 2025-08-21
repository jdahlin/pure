global_var: int = 10


def impure_func() -> None:
    global global_var  # noqa: PLW0603
    global_var += 1


def pure_func(i: int) -> int:
    return i + 1


pure_func.pure = True  # auto-detected pure function?


def f(n: int) -> int:
    y = global_var  # noqa: F841
    pure_func(10)
    impure_func()
    return f(1)


f.pure = True

# Expected:
# 19:4: Function 'f' calls non-pure function 'impure_func'
