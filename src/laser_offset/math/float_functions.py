### Match functions

def fzero(a: float, tolerance: float = 1e-5) -> bool:
    """Compares float with zero using tolerance

    Parameters:
    a (float): value to compare with zero
    tolerance (float): tolerance of compare

    Returns:
    bool:True if near zero
    """

    if abs(a) < tolerance:
        return True
    else:
        return False

def fclose(a: float, b: float, tolerance: float = 1e-5) -> bool:
    return fzero(a-b, tolerance)

def fge(a: float, b: float, tolerance: float = 1e-5) -> bool:
    return fzero(a-b, tolerance) or a > b

def fle(a: float, b: float, tolerance: float = 1e-5) -> bool:
    return fzero(a-b, tolerance) or a < b
