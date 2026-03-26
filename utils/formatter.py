import numpy as np

def is_se3_like(obj) -> bool:
    """
    Check whether an object behaves like a spatialmath SE3 object.

    Parameters
    ----------
    obj : object
        Object to be checked.

    Returns
    -------
    bool
        True if the object exposes an SE3-like homogeneous matrix through `A`.
    """
    return hasattr(obj, "A")


def is_matrix_like(obj) -> bool:
    """
    Check whether an object behaves like a matrix wrapper.

    Parameters
    ----------
    obj : object
        Object to be checked.

    Returns
    -------
    bool
        True if the object exposes a matrix through `matrix()`.
    """
    return hasattr(obj, "matrix") and callable(obj.matrix)


def to_array(obj) -> np.ndarray:
    """
    Convert a supported object into a NumPy array.

    Parameters
    ----------
    obj : object
        Supported object to be converted.

    Returns
    -------
    np.ndarray
        Array representation of the input object.

    Raises
    ------
    TypeError
        If the object type is not supported.
    """
    if is_matrix_like(obj):
        return np.asarray(obj.matrix())

    if is_se3_like(obj):
        return np.asarray(obj.A)

    if isinstance(obj, (list, tuple, np.ndarray)):
        return np.asarray(obj)

    raise TypeError(f"Type {type(obj)} not serializable")


def serialize(obj):
    """
    Serialize supported objects into JSON-friendly structures.

    Parameters
    ----------
    obj : object
        Object to be serialized.

    Returns
    -------
    object
        JSON-friendly representation of the input object.

    Raises
    ------
    TypeError
        If the object type is not supported.
    """
    if is_matrix_like(obj) or is_se3_like(obj):
        arr = to_array(obj)
        return {
            "__type__": type(obj).__name__,
            "data": arr.tolist(),
        }

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, (list, tuple)):
        return list(obj)

    raise TypeError(f"Type {type(obj)} not serializable")


def pretty_format(obj, indent: int = 0) -> str:
    """
    Format supported objects into a readable multi-line string.

    Parameters
    ----------
    obj : object
        Object to be formatted.
    indent : int, optional
        Current indentation level.

    Returns
    -------
    str
        Pretty-formatted string representation.
    """
    space = " " * indent

    if isinstance(obj, dict):
        lines = ["{"]
        for key, value in obj.items():
            formatted = pretty_format(value, indent + 4)
            lines.append(f'{" " * (indent + 4)}"{key}": {formatted},')
        if len(lines) > 1:
            lines[-1] = lines[-1].rstrip(",")
        lines.append(space + "}")
        return "\n".join(lines)

    if isinstance(obj, (list, tuple)):
        if obj and all(not isinstance(x, (list, tuple, dict)) for x in obj):
            return "[" + ", ".join(repr(x) for x in obj) + "]"

        lines = ["["]
        for item in obj:
            lines.append(" " * (indent + 4) + pretty_format(item, indent + 4) + ",")
        if len(lines) > 1:
            lines[-1] = lines[-1].rstrip(",")
        lines.append(space + "]")
        return "\n".join(lines)

    if is_matrix_like(obj) or is_se3_like(obj) or isinstance(obj, (list, tuple, np.ndarray)):
        arr = to_array(obj)

        arr_str = np.array2string(
            arr,
            precision=6,
            suppress_small=False,
            separator=", ",
            threshold=20,
        )

        if is_se3_like(obj):
            return f"{type(obj).__name__}(array({arr_str}))"

        return arr_str

    return repr(obj)


def fmt_array(arr, decimals: int = 3) -> str:
    """
    Format a numerical array into a readable string.

    Parameters
    ----------
    arr : array-like | None
        Input array to be formatted.
    decimals : int, optional
        Number of decimal places for floating-point values.

    Returns
    -------
    str
        Formatted string representation of the array.
    """
    if arr is None:
        return "None"

    formatter = {
        "float_kind": lambda x: f"{x:.{decimals}f}"
    }

    return np.array2string(
        np.asarray(arr),
        formatter=formatter,
    )
