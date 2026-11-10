from __future__ import annotations
from dataclasses import dataclass
import re
from math import ceil
from typing import ClassVar, Final

@dataclass(frozen=True)
class Material:
    name: str
    qty: int

    ORE: ClassVar[str] = "ORE"
    FUEL: ClassVar[str] = "FUEL"

    @classmethod
    def empty(cls, name: str) -> Material:
        return cls(name, 0)

    def __repr__(self) -> str:
        return f"{self.qty} {self.name}"

    def __neg__(self) -> Material:
        return Material(self.name, -self.qty)

    def __add__(self, other: Material) -> Material:
        return Material(self.name, self.qty + other.qty)

    def __sub__(self, other: Material) -> Material:
        return self.__add__(other.__neg__())

    def __mul__(self, ratio: int) -> Material:
        return Material(self.name, self.qty * ratio)

    def __rmul__(self, ratio: int) -> Material:
        return self.__mul__(ratio)

    def is_empty(self) -> bool:
        return self.qty == 0

    def needs_production(self) -> bool:
        if self.name == Material.ORE:
            return False
        else:
            return self.qty < 0

    def divide_by(self, recipe: Material) -> int:
        if isinstance(recipe, Material) and self.name == recipe.name:
            ratio = ceil(abs(self.qty) / abs(recipe.qty))
            return ratio
        else:
            return 0


class Nanofactory:
    _MAX_ITERS: Final[int] = 100

    def __init__(self, reaction_list: list[str]):
        self.reaction_dict: Final[dict[str, tuple[tuple[Material, ...], Material]]] \
            = Nanofactory._parse_reaction_list(reaction_list)
        self.material_list: Final[set[str]] \
            = set(self.reaction_dict.keys()) | {Material.ORE, Material.FUEL}
        self._inventory: dict[str, Material] = dict()

    @staticmethod
    def _parse_reaction_list(reaction_list: list[str]) -> dict[str, tuple[tuple[Material, ...], Material]]:
        """
        For a given reaction
        Material input_1, ..., Material input_n -> Material output

        Related entry in reaction_dict is stored as
        key: output.name
        value: ((input_1, ..., input_n), output)
        """
        material_regex = re.compile(r"(\d+) ([A-Z]+)")
        reaction_dict: dict[str, tuple[tuple[Material, ...], Material]] = dict()
        for reaction in reaction_list:
            lhs, rhs = reaction.split(" => ")
            output_qty, output_name = material_regex.fullmatch(rhs).groups()
            output = Material(output_name, int(output_qty))
            inputs = tuple(Material(input_name, int(input_qty)) for input_qty, input_name in material_regex.findall(lhs))
            reaction_dict[output.name] = (inputs, output)
        return reaction_dict

    def get_ore_cost(self, name: str, qty: int) -> int:
        material = Material(name, qty)
        self._clear_inventory()
        self._add_to_inventory(-material)
        self._reduce_to_ore()
        ore = self._inventory.get(Material.ORE, Material.empty(Material.ORE))
        return abs(ore.qty)

    def _clear_inventory(self) -> None:
        self._inventory = dict()

    def _add_to_inventory(self, material: Material) -> None:
        name = material.name
        if name not in self.material_list:
            return
        existing_material = self._inventory.get(name, Material.empty(name))
        self._inventory[name] = existing_material + material
        if self._inventory[name].is_empty():
            self._inventory.pop(name)

    def _reduce_to_ore(self) -> None:
        for _ in range(Nanofactory._MAX_ITERS):
            done = True
            for name, material in list(self._inventory.items()):
                if material.needs_production():
                    done = False
                    inputs, output = self.reaction_dict.get(name)
                    ratio = material.divide_by(output)
                    for inp in inputs:
                        self._add_to_inventory(-inp * ratio)
                    self._add_to_inventory(output * ratio)
            if done:
                break