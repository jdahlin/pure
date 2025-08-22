
def a() -> None:
    pass


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
