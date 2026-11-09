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

    def __repr__(self) -> str:
        return f"{self.qty} {self.name}"

    def same_as(self, other: str | Material) -> bool:
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Material):
            return self.name == other.name
        else:
            return False

    def is_empty(self) -> bool:
        return self.qty == 0

    def needs_production(self) -> bool:
        return self.qty < 0

    def combine(self, other: Material) -> Material | None:
        if isinstance(other, Material) and self.same_as(other):
            return Material(self.name, self.qty + other.qty)
        else:
            return None

    def divide(self, other: Material) -> tuple[int, int] | None:
        if isinstance(other, Material) and self.name == other.name:
            ratio = ceil(self.qty / other.qty)
            leftover = ratio * other.qty - self.qty
            return ratio, leftover
        else:
            return None

    def add(self, amount: int) -> Material:
        return Material(self.name, self.qty + amount)

    def multiply(self, ratio: int) -> Material:
        return Material(self.name, self.qty * ratio)


class Nanofactory:
    def __init__(self, reaction_list: list[str]):
        self.reaction_dict: Final[dict[str, tuple[tuple[Material, ...], Material]]] \
            = Nanofactory.parse_reaction_list(reaction_list)
        self.inventory: dict[str, Material] = dict()

    @staticmethod
    def parse_reaction_list(reaction_list: list[str]) -> dict[str, tuple[tuple[Material, ...], Material]]:
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

    def get_chemical_list(self) -> list[str]:
        return list(self.reaction_dict.keys())

    def reduce_to_ore(self, material: Material) -> Material:
        pass