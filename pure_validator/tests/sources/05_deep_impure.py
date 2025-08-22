
def a() -> None:
    print("impure")


def b() -> None:
    a()


def c() -> None:
    b()


def d() -> None:
    c()


def e() -> None:
    d()


def f() -> None:  # pragma: pure
    e()


# Expected:
# 23:4: Function 'f' calls non-pure function 'e'
