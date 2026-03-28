import math
import random

from sim.coppelia_sim.sim_object import SimObject
from utils import DEG_TO_RAD, CM_TO_M, G_TO_KG

class Cuboids(SimObject):
    """Create and manage cuboid objects in CoppeliaSim."""

    path = "./ref_cuboid"          # CoppeliaSim reference cuboid path
    body_path = "./ref_body"       # CoppeliaSim reference body path
    marker_path = "./ref_marker{id}"  # Marker path template
    marker_length = 5 * CM_TO_M

    colors = {
        "red": [1, 0, 0],
        "green": [0, 1, 0],
        "blue": [0, 0, 1],
    }

    class Pending:
        """Parameters used to identify cuboids still in the creation region."""

        z = 22.5 * CM_TO_M
        tol = 1 * CM_TO_M

    class Create:
        """Parameters used during cuboid creation."""

        x = 95 * CM_TO_M
        z = 22.5 * CM_TO_M
        rx = 0
        ry = 0

        class Random:
            """Randomized creation ranges."""

            class Id:
                min = 1
                max = 10

            class Y:
                min = -20 * CM_TO_M
                max = 20 * CM_TO_M

            class Rz:
                min = -180 * DEG_TO_RAD
                max = 180 * DEG_TO_RAD

            class Mass:
                min = 125 * G_TO_KG
                max = 7

    def __init__(self, sim, max_creation=None) -> None:
        """
        Initialize the cuboid manager.

        Parameters
        ----------
        sim : object
            CoppeliaSim remote API or simulation interface.
        max_creation : int | None, optional
            Maximum number of cuboids to create. If None, creation is unlimited.
        """
        super().__init__(
            obj_name="ReferenceCuboid",
            client=None,
            sim=sim,
            is_thread=False,
        )

        self.max_creation = max_creation
        self.handle = self.sim.getObjectHandle(self.path)
        self.body_handle = self.sim.getObjectHandle(self.body_path)

        self.created = []
        self.available = []
        self.pending = []

    def check_available(self) -> None:
        """Update the list of currently available cuboid names."""
        self.available = []

        for color in ["red", "blue", "green"]:
            for marker_id in range(
                self.Create.Random.Id.min,
                self.Create.Random.Id.max + 1,
            ):
                obj_path = f"./{color}{marker_id}"

                try:
                    self.sim.getObject(obj_path)
                except Exception:
                    self.available.append(obj_path)

    def check_pending(self) -> bool:
        """
        Update and check whether there are cuboids still in the creation region.

        Returns
        -------
        bool
            True if at least one created cuboid is still pending, False otherwise.
        """
        self.pending = self.created.copy()

        def is_pending(obj_path: str) -> bool:
            handle = self.sim.getObject(obj_path)
            _, _, z = self.sim.getObjectPosition(handle)

            return math.isclose(z, self.Pending.z, abs_tol=self.Pending.tol)

        self.pending = list(filter(is_pending, self.pending))
        return len(self.pending) > 0

    def create_cuboid(self) -> None:
        """Create a new random cuboid from the available templates."""
        while True:
            marker_id = random.randint(
                self.Create.Random.Id.min,
                self.Create.Random.Id.max,
            )
            color_name, color = random.choice(list(self.colors.items()))
            obj_path = f"./{color_name}{marker_id}"

            if obj_path in self.available:
                break

        handle, marker, body = self.sim.copyPasteObjects(
            [
                self.handle,
                self.sim.getObjectHandle(
                    self.marker_path.replace("{id}", str(marker_id))
                ),
                self.body_handle,
            ],
            0,
        )

        self.sim.setObjectPosition(marker, handle, [0, 0, self.marker_length / 2])
        self.sim.setObjectPosition(body, handle, [0, 0, 0])

        self.sim.setObjectParent(marker, handle, True)
        self.sim.setObjectParent(body, handle)

        y = random.uniform(self.Create.Random.Y.min, self.Create.Random.Y.max)
        self.sim.setObjectPosition(handle, -1, [self.Create.x, y, self.Create.z])

        rz = random.uniform(self.Create.Random.Rz.min, self.Create.Random.Rz.max)
        self.sim.setObjectOrientation(handle, -1, [self.Create.rx, self.Create.ry, rz])

        mass = random.uniform(self.Create.Random.Mass.min, self.Create.Random.Mass.max)
        self.sim.setShapeMass(handle, mass)

        self.sim.setObjectAlias(marker, self.sim.getObjectAlias(marker).replace("ref_", ""))
        self.sim.setShapeColor(marker, None, self.sim.colorcomponent_ambient_diffuse, color)

        self.sim.setObjectAlias(body, self.sim.getObjectAlias(body).replace("ref_", ""))
        self.sim.setShapeColor(body, None, self.sim.colorcomponent_ambient_diffuse, color)

        self.sim.setObjectAlias(handle, f"{color_name}{marker_id}")

        self.created.append(obj_path)
        self.available.remove(obj_path)

    def step(self) -> None:
        """Create a new cuboid when there are no pending ones and the limit allows it."""
        self.check_available()

        can_create = self.max_creation is None or len(self.created) < self.max_creation

        if not self.check_pending() and can_create:
            self.create_cuboid()
