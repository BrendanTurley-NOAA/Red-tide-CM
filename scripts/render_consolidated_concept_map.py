from __future__ import annotations

import csv
import random
from pathlib import Path

from igraph import Graph, plot


REPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_PATH = REPO_ROOT / "data" / "consolidated" / "concept_presence_by_matrix.csv"
EDGES_PATH = REPO_ROOT / "data" / "consolidated" / "edge_support_summary.csv"
OUTPUT_PATH = REPO_ROOT / "data" / "consolidated" / "consolidated_concept_map.png"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_graph() -> Graph:
    concept_rows = read_csv_rows(CONCEPTS_PATH)
    edge_rows = read_csv_rows(EDGES_PATH)

    graph = Graph(directed=True)
    graph.add_vertices([row["concept"] for row in concept_rows])
    graph.add_edges([(row["source"], row["target"]) for row in edge_rows])

    matrix_counts = {row["concept"]: int(row["matrix_count"]) for row in concept_rows}
    degrees = graph.degree(mode="all")

    graph.vs["label"] = graph.vs["name"]
    graph.vs["matrix_count"] = [matrix_counts[name] for name in graph.vs["name"]]
    graph.vs["degree"] = degrees
    graph.vs["size"] = [14 + (degree ** 0.6) * 1.8 for degree in degrees]
    graph.vs["label_size"] = [7 + min(5, count) for count in graph.vs["matrix_count"]]
    graph.vs["label_dist"] = 0
    graph.vs["frame_color"] = "#1f2937"
    graph.vs["frame_width"] = 0.6
    graph.vs["color"] = [
        "#f59e0b" if count > 1 else "#60a5fa" for count in graph.vs["matrix_count"]
    ]

    graph.es["weight"] = [int(row["matrix_count"]) for row in edge_rows]
    graph.es["width"] = [0.8 + (weight - 1) * 2 for weight in graph.es["weight"]]
    graph.es["arrow_size"] = 0.3
    graph.es["arrow_width"] = 0.8
    graph.es["curved"] = 0.12
    graph.es["color"] = [
        "#dc2626AA" if weight > 1 else "#94a3b8AA" for weight in graph.es["weight"]
    ]

    return graph


def main() -> None:
    random.seed(42)
    graph = build_graph()
    layout = graph.layout_fruchterman_reingold(
        weights=graph.es["weight"],
        niter=5000,
        grid="nogrid",
    )

    plot(
        graph,
        target=str(OUTPUT_PATH),
        layout=layout,
        bbox=(4200, 3200),
        margin=120,
        background="white",
    )

    print(
        f"Saved conceptual model map to {OUTPUT_PATH} "
        f"({graph.vcount()} concepts, {graph.ecount()} directed relationships)."
    )


if __name__ == "__main__":
    main()
