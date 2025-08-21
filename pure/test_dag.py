# Test file to demonstrate the DAG purity checker

# Global variable (makes functions impure)
global_var = 42


def pure_function(x, y):
    """A pure function - only uses parameters and pure builtins"""
    return x + y + abs(x - y)


def impure_function(x):
    """Impure function - uses global variable"""
    return x + global_var


def calls_pure_function(a, b):
    """Function that calls another pure function"""
    return pure_function(a, b) * 2


def calls_impure_function(x):
    """Function that calls an impure function"""
    return impure_function(x) + 1


def recursive_function(n):
    """Pure recursive function"""
    if n <= 1:
        return 1
    return n * recursive_function(n - 1)


# Mark functions as pure for checking
pure_function.pure = True
calls_pure_function.pure = True  # This should be valid - only calls pure functions
calls_impure_function.pure = True  # This should fail - calls impure function
impure_function.pure = True  # This should fail - uses global variable
recursive_function.pure = True  # This should be valid - pure recursion
