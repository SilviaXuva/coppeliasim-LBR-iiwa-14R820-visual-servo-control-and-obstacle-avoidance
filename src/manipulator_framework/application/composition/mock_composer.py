from __future__ import annotations

from dataclasses import dataclass

from manipulator_framework.application.composition.application_composer import ApplicationComposer


@dataclass
class MockApplicationComposer(ApplicationComposer):
    """
    Minimal application composition root for tests and examples.
    """
    pass
