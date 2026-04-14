import inspect

from manipulator_framework.core.ports.drawing_port import DrawingPort


def test_drawing_port_exposes_required_api() -> None:
    required = {
        "draw_point": ("self", "position"),
        "draw_line": ("self", "start", "end"),
        "draw_path": ("self", "points"),
        "draw_frame": ("self", "pose"),
        "clear": ("self",),
    }
    for method_name, expected_params in required.items():
        method = getattr(DrawingPort, method_name, None)
        assert callable(method)
        signature = inspect.signature(method)
        assert tuple(signature.parameters.keys()) == expected_params
