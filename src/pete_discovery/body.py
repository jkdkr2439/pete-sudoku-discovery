from __future__ import annotations

from .journal import HashJournal


class Body:
    """Typed transducer. It moves signals; it owns no world interpretation."""

    def __init__(self, world, journal: HashJournal, life=100_000):
        self.__world = world
        self.journal = journal
        self.life = int(life)
        self.energy = int(life)

    def sense(self):
        packet = self.__world.observe()
        return {"vision": packet, "interoception": {"life": self.life, "energy": self.energy}}

    def reset_experiment(self):
        packet = self.__world.begin_experiment()
        self.energy -= 1
        self.journal.append("body.reset_experiment", {"world_id": packet["world_id"], "energy": self.energy})
        return packet

    def reset_challenge(self):
        self.__world.reset_challenge()
        return self.sense()

    def act(self, position, value, purpose="commit"):
        before = self.__world.observe()
        receipt = self.__world.place(position, value)
        self.energy -= 1
        self.life += receipt.life_delta
        after = self.__world.observe()
        public = receipt.public()
        self.journal.append("body.action", {
            "purpose": purpose,
            "position": position if isinstance(position, str) else list(position),
            "value": value,
            "before_board": before["board"],
            "receipt": public,
            "after_board": after["board"],
            "life": self.life,
            "energy": self.energy,
        })
        return {"receipt": public, "observation": after, "interoception": {"life": self.life, "energy": self.energy}}
