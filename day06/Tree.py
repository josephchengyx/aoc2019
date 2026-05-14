from __future__ import annotations
from typing import Any

class TreeNode:
    def __init__(self, value: str) -> None:
        self.value: str = value
        self.parent: TreeNode | None = None
        self._depth: int | None = None

    def __repr__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TreeNode):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)

    def is_root(self) -> bool:
        return self.parent is None

    def depth(self) -> int:
        if self._depth is None:
            self._depth = 0 if self.is_root() else self.parent.depth() + 1
        return self._depth

    def path_to_node(self, target: TreeNode | None = None) -> list[TreeNode]:
        path: list[TreeNode] = list()
        curr_node = self
        while not (curr_node == target or curr_node.is_root()):
            path.append(curr_node)
            curr_node = curr_node.parent
        return path

    def nearest_common_ancestor(self, other: TreeNode) -> TreeNode:
        other_ancestors = set(other.path_to_node())
        curr_node = self
        while not (curr_node in other_ancestors or curr_node.is_root()):
            curr_node = curr_node.parent
        return curr_node


class Tree:
    def __init__(self):
        self._nodes: dict[str, TreeNode] = dict()

    def get_node(self, node: str) -> TreeNode | None:
        return self._nodes.get(node, None)

    def nodes(self) -> list[str]:
        return list(self._nodes.keys())

    def add_edge(self, parent: str, child: str) -> None:
        if parent not in self._nodes:
            self._nodes[parent] = TreeNode(parent)
        if child not in self._nodes:
            self._nodes[child] = TreeNode(child)
        self._nodes[child].parent = self._nodes[parent]

    def depth(self, node: str) -> int:
        node = self.get_node(node)
        return node.depth() if node is not None else 0

    def path_to_node(self, start: str, end: str | None = None) -> list[str]:
        start, end = self.get_node(start), self.get_node(end)
        return list(map(lambda node: node.value, start.path_to_node(end)))

    def nearest_common_ancestor(self, node1: str, node2: str) -> str:
        node1, node2 = self.get_node(node1), self.get_node(node2)
        return node1.nearest_common_ancestor(node2).value