"""
Monte Carlo Tree Search for Language Agent Tree Search.

From lesson: 'create a tree structure of possible plans and outcomes'
Implements 4-phase MCTS loop: Selection, Expansion, Simulation, Back-propagation
"""

import math
import uuid
from dataclasses import dataclass, field


@dataclass
class MCTSNode:
    """A node in the Monte Carlo Tree Search tree."""

    node_id: str
    action: str
    thought: str
    parent_id: str | None
    children: list[str] = field(default_factory=list)
    visit_count: int = 0
    total_score: float = 0.0
    simulated: bool = False

    @property
    def average_score(self) -> float:
        return self.total_score / self.visit_count if self.visit_count > 0 else 0.0


class MCTSTree:
    """
    The search tree for Language Agent Tree Search.
    Implements 4-phase MCTS loop.
    """

    def __init__(self, root_task: str):
        self.root_task = root_task
        self.nodes: dict[str, MCTSNode] = {}
        self.root_id: str = "root"
        self._create_root()

    def _create_root(self):
        root = MCTSNode(
            node_id=self.root_id,
            action="start",
            thought=f"Starting task: {self.root_task}",
            parent_id=None,
        )
        self.nodes[self.root_id] = root

    def selection_phase(self) -> MCTSNode:
        """Follow most promising path to unexplored node. Uses UCB1."""
        path = []
        current = self.nodes[self.root_id]

        while current.children:
            best_child = None
            best_ucb = -float("inf")
            for cid in current.children:
                child = self.nodes[cid]
                if child.visit_count == 0:
                    path.append(current)
                    print(f"[LATS-SELECTION] Following path... → {cid} (unexplored)")
                    return child
                ucb = child.average_score + 1.4 * math.sqrt(
                    math.log(current.visit_count + 1) / (child.visit_count + 1)
                )
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            if best_child:
                path.append(current)
                current = best_child

        if current.node_id == self.root_id and not current.children:
            print(f"[LATS-SELECTION] → root (no children yet, will expand)")
        else:
            print(f"[LATS-SELECTION] → {current.node_id} (score: {current.average_score:.2f})")
        return current

    def expansion_phase(self, parent_node: MCTSNode, new_actions: list[dict]) -> list[MCTSNode]:
        """Add new hypothetical action nodes."""
        added = []
        for i, a in enumerate(new_actions):
            nid = f"{parent_node.node_id}_c{i}_{uuid.uuid4().hex[:4]}"
            node = MCTSNode(
                node_id=nid,
                action=a.get("action", str(a)),
                thought=a.get("thought", ""),
                parent_id=parent_node.node_id,
            )
            self.nodes[nid] = node
            parent_node.children.append(nid)
            added.append(node)
        print(f"[LATS-EXPANSION] Adding {len(added)} branches:")
        for i, n in enumerate(added):
            print(f"  Branch {chr(65+i)}: \"{n.action[:40]}...\"" if len(n.action) > 40 else f"  Branch {chr(65+i)}: \"{n.action}\"")
        return added

    def simulation_phase(self, node: MCTSNode, llm_score: float, reasoning: str) -> float:
        """Simulate and score the scenario."""
        node.simulated = True
        node.visit_count += 1
        node.total_score += llm_score
        print(f"[LATS-SIMULATION] Action: {node.action[:50]}...")
        print(f"  Score: {llm_score:.2f} | Reasoning: {reasoning[:60]}...")
        return llm_score

    def backpropagation_phase(self, leaf_node: MCTSNode, score: float):
        """Update scores up the tree."""
        path = []
        current = leaf_node
        while current:
            current.visit_count += 1
            current.total_score += score
            path.append(current.node_id)
            current = self.nodes.get(current.parent_id) if current.parent_id else None
        print(f"[LATS-BACKPROP] Propagating score {score:.2f}: {' → '.join(reversed(path))}")

    def get_best_action(self) -> MCTSNode | None:
        """Select child of root with highest average score."""
        if not self.nodes[self.root_id].children:
            return None
        best = None
        best_score = -1
        for cid in self.nodes[self.root_id].children:
            child = self.nodes[cid]
            if child.visit_count > 0 and child.average_score > best_score:
                best_score = child.average_score
                best = child
        if best:
            print(f"[LATS-DECISION] Best action: \"{best.action}\" (avg: {best.average_score:.2f})")
        return best

    def visualize(self) -> str:
        lines = [f"root [{self.root_id}]"]
        for cid in self.nodes.get(self.root_id, MCTSNode("", "", "", None)).children:
            child = self.nodes.get(cid)
            if child:
                lines.append(f"  └─ {child.action[:40]} (score: {child.average_score:.2f})")
        return "\n".join(lines)
