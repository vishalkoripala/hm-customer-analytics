import argparse
import csv
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"


def vector_key(values):
    return tuple(f"{float(value):.10f}" for value in values)


def load_cluster_assignments(cluster_file):
    vector_to_cluster = {}

    with cluster_file.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            fields = line.rstrip("\r\n").split("\t")

            if len(fields) != 4:
                raise ValueError(
                    f"Invalid cluster record at line {line_number}: "
                    "expected 4 tab-separated fields."
                )

            cluster, recency, frequency, monetary = fields

            try:
                key = vector_key((recency, frequency, monetary))
            except ValueError as exc:
                raise ValueError(
                    f"Invalid vector values at cluster line {line_number}"
                ) from exc

            if key in vector_to_cluster:
                if vector_to_cluster[key] != cluster:
                    raise ValueError(
                        f"Conflicting cluster assignments for vector: {key}"
                    )
                continue

            vector_to_cluster[key] = cluster

    if not vector_to_cluster:
        raise ValueError("No cluster assignments were found.")

    return vector_to_cluster


def main():
    parser = argparse.ArgumentParser(
        description="Map customer IDs to Mahout cluster assignments."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing the intermediate data files."
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=1_362_281,
        help="Expected number of customers (default: 1362281)."
    )
    args = parser.parse_args()

    data_dir = args.data_dir.expanduser()
    scaled_file = data_dir / "customer_rfm_scaled.tsv"
    cluster_file = data_dir / "extracted_clusters.tsv"
    output_file = data_dir / "customer_clusters_final.csv"

    for path in (scaled_file, cluster_file):
        if not path.is_file():
            raise FileNotFoundError(f"Required file not found: {path}")

    if args.expected_count < 1:
        raise ValueError("Expected customer count must be positive.")

    # Build vector-to-cluster lookup.
    vector_to_cluster = load_cluster_assignments(cluster_file)

    print("Unique vector mappings:", len(vector_to_cluster))

    matched = 0
    unmatched = 0
    cluster_counts = Counter()
    seen_customer_ids = set()

    with scaled_file.open(
        newline="", encoding="utf-8"
    ) as source, output_file.open(
        "w", newline="", encoding="utf-8"
    ) as destination:

        reader = csv.reader(source, delimiter="\t")
        writer = csv.writer(destination)

        header = next(reader, None)

        expected_header = [
            "customer_id", "recency", "frequency", "monetary"
        ]

        if header != expected_header:
            raise ValueError(
                f"Unexpected input header: {header}. "
                f"Expected: {expected_header}"
            )

        writer.writerow(["customer_id", "cluster_id"])

        for line_number, row in enumerate(reader, start=2):
            if len(row) != 4:
                raise ValueError(
                    f"Invalid customer record at line {line_number}: "
                    "expected 4 tab-separated fields."
                )

            customer_id = row[0].strip()

            if not customer_id:
                raise ValueError(
                    f"Empty customer ID at line {line_number}"
                )

            if customer_id in seen_customer_ids:
                raise ValueError(
                    f"Duplicate customer ID at line {line_number}: "
                    f"{customer_id}"
                )

            seen_customer_ids.add(customer_id)

            try:
                key = vector_key(row[1:4])
            except ValueError as exc:
                raise ValueError(
                    f"Invalid RFM vector at line {line_number}"
                ) from exc

            cluster = vector_to_cluster.get(key)

            if cluster is None:
                unmatched += 1
                continue

            writer.writerow([customer_id, cluster])
            cluster_counts[cluster] += 1
            matched += 1

    print("\nMapping results")
    print("Matched customers:", matched)
    print("Unmatched customers:", unmatched)
    print("Unique customer IDs:", len(seen_customer_ids))
    print("Cluster distribution:")

    for cluster, count in sorted(cluster_counts.items()):
        print(cluster, count)

    print("Total mapped:", sum(cluster_counts.values()))
    print("Output:", output_file)

    if matched != args.expected_count:
        raise SystemExit(
            f"VALIDATION FAILED: expected {args.expected_count} "
            f"mappings, found {matched}."
        )

    if unmatched != 0:
        raise SystemExit(
            f"VALIDATION FAILED: {unmatched} customers were unmatched."
        )

    print("\nSUCCESS: All customer IDs mapped and validated.")


if __name__ == "__main__":
    main()
