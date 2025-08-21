bad = 0


def prop_true(n: int) -> int:
    global bad
    bad += 1
    return n


prop_true.pure = True


def prop_false(n: int) -> int:
    return n


prop_false.pure = False


def doc_string(n: int) -> int:
    """
    @pure
    """
    return n


def doc_string2(n: int) -> int:
    """
    :param n:
    :pure: true
    :return:
    """
    return n


def comment_body(n: int) -> int:
    # @pure
    return n


# @pure
def comment_before(n: int) -> int:
    return n


# Expected:
# 5:4: Function 'prop_true' uses global variable 'bad'
