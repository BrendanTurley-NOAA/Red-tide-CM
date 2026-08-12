from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "data" / "raw_matrices"
OUTPUT_DIR = REPO_ROOT / "data" / "consolidated"


def clean_label(value: str) -> str:
    return " ".join(value.replace("\ufeff", "").split())


def load_matrix(path: Path) -> tuple[str, list[str], list[tuple[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))

    headers = [clean_label(cell) for cell in rows[0][1:] if clean_label(cell)]
    edges: list[tuple[str, str]] = []

    for raw_row in rows[1:]:
        if not raw_row:
            continue

        source = clean_label(raw_row[0])
        if not source:
            continue

        cells = raw_row[1 : len(headers) + 1]
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))

        for target, cell in zip(headers, cells):
            if clean_label(cell) and clean_label(cell) != "0":
                edges.append((source, target))

    matrix_name = path.stem.replace("Matrix.", "", 1)
    concepts = sorted(set(headers) | {source for source, _ in edges}, key=str.casefold)
    return matrix_name, concepts, edges


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def main() -> None:
    matrices = [load_matrix(path) for path in sorted(INPUT_DIR.glob("Matrix.*.csv"))]
    matrix_names = [name for name, _, _ in matrices]

    concept_membership: dict[str, set[str]] = defaultdict(set)
    edge_membership: dict[tuple[str, str], set[str]] = defaultdict(set)
    long_edges: list[list[str]] = []

    for matrix_name, concepts, edges in matrices:
        for concept in concepts:
            concept_membership[concept].add(matrix_name)

        for source, target in edges:
            edge_membership[(source, target)].add(matrix_name)
            long_edges.append([matrix_name, source, target])

    concept_rows: list[list[str]] = []
    for concept in sorted(concept_membership, key=str.casefold):
        present_in = concept_membership[concept]
        concept_rows.append(
            [concept, str(len(present_in)), "; ".join(sorted(present_in))]
            + ["1" if matrix_name in present_in else "0" for matrix_name in matrix_names]
        )

    edge_rows: list[list[str]] = []
    for source, target in sorted(edge_membership, key=lambda item: (item[0][0].casefold(), item[0][1].casefold())):
        present_in = edge_membership[(source, target)]
        edge_rows.append([source, target, str(len(present_in)), "; ".join(sorted(present_in))])

    long_edges.sort(key=lambda row: (row[0].casefold(), row[1].casefold(), row[2].casefold()))

    write_csv(
        OUTPUT_DIR / "concept_presence_by_matrix.csv",
        ["concept", "matrix_count", "matrices", *matrix_names],
        concept_rows,
    )
    write_csv(
        OUTPUT_DIR / "edge_support_summary.csv",
        ["source", "target", "matrix_count", "matrices"],
        edge_rows,
    )
    write_csv(
        OUTPUT_DIR / "matrix_edges_long.csv",
        ["matrix", "source", "target"],
        long_edges,
    )


if __name__ == "__main__":
    main()
