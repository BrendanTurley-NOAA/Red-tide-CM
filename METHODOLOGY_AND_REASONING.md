# Methodology and Reasoning

## Purpose

This repository contains multiple raw conceptual model matrices in `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices`. The goal of the consolidation step is to turn those separate matrices into a set of repository-tracked outputs that make it easier to compare concepts and relationships across locations.

## Source Inputs

The current consolidation uses these raw input files:

- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices/Matrix.Group1.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices/Matrix.Madeira.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices/Matrix.PanamaCity.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices/Matrix.PineIsl.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/raw_matrices/Matrix.StPete.csv`

## Consolidation Method

The script `/home/runner/work/Red-tide-CM/Red-tide-CM/scripts/consolidate_feature_matrices.py` performs the consolidation.

Its method is:

1. Read each raw CSV matrix.
2. Normalize concept labels by removing any byte order mark artifacts and collapsing repeated whitespace.
3. Treat the first row as the set of target concepts for that matrix.
4. Treat the first column of each remaining row as the source concept.
5. Interpret any non-empty, non-zero cell as a directed relationship from the row concept to the column concept.
6. Build the full concept list for each matrix from the union of header concepts and row-label concepts.
7. Aggregate concept presence across matrices.
8. Aggregate directed edges across matrices.
9. Write the consolidated outputs back into the repository.

## Output Files

The consolidation currently produces:

- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/consolidated/concept_presence_by_matrix.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/consolidated/edge_support_summary.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/consolidated/matrix_edges_long.csv`
- `/home/runner/work/Red-tide-CM/Red-tide-CM/data/consolidated/consolidated_concept_map.png`

### `concept_presence_by_matrix.csv`

This file shows whether each concept appears in each matrix. It includes:

- the concept name
- the number of matrices in which that concept appears
- a semicolon-delimited list of matrix names
- one indicator column per matrix

This supports cross-site comparison of concept coverage.

### `edge_support_summary.csv`

This file lists unique directed source-target relationships and summarizes:

- the source concept
- the target concept
- the number of matrices supporting that relationship
- the matrices in which the relationship appears

This supports comparison of shared and location-specific causal structure.

### `matrix_edges_long.csv`

This file stores one row per observed edge per matrix:

- matrix
- source
- target

This is the most analysis-friendly format for downstream filtering, counting, visualization, or graph-based workflows.

### `consolidated_concept_map.png`

This PNG provides a single network view of the consolidated conceptual model using igraph. The rendering uses:

- one node per concept
- one directed edge per consolidated source-target relationship
- larger node sizes for more connected concepts
- highlighted node and edge styling for concepts or relationships that appear in more than one source matrix

This supports quick visual inspection of the overall consolidated structure.

## Reasoning Behind the Approach

This approach was chosen because it is simple, reproducible, and closely aligned with the structure of the existing source files.

- It preserves the raw matrix meaning without inventing new semantics.
- It uses a transparent rule for detecting relationships: non-empty and non-zero cells indicate an edge.
- It keeps outputs in plain CSV so they are easy to inspect and reuse.
- It separates concept-level presence from edge-level structure, which supports different types of comparison.
- It provides both summary outputs and a long-format edge table for downstream analysis.

## Assumptions and Limitations

- The raw matrices are assumed to represent directed relationships from rows to columns.
- The current process does not attempt synonym resolution beyond basic whitespace cleanup.
- Differences in spelling, capitalization, or wording across matrices are preserved unless they are already identical after normalization.
- Cell values are treated as presence/absence, not weighted strength.
- The outputs are descriptive consolidations of the provided files, not an expert-resolved ontology.

## Regeneration

To regenerate the outputs, run:

`python /home/runner/work/Red-tide-CM/Red-tide-CM/scripts/consolidate_feature_matrices.py`

To regenerate the network map, run:

`python /home/runner/work/Red-tide-CM/Red-tide-CM/scripts/render_consolidated_concept_map.py`
