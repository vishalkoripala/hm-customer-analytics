import argparse
import csv
import math
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = PROJECT_DIR / "data"


def parse_record(row, line_number):
    if len(row) != 4:
        raise ValueError(
            f"Invalid record at line {line_number}: expected 4 fields, "
            f"received {len(row)}"
        )

    customer_id = row[0].strip()

    if not customer_id:
        raise ValueError(f"Empty customer ID at line {line_number}")

    try:
        recency = float(row[1])
        frequency = float(row[2])
        monetary = float(row[3])
    except ValueError as exc:
        raise ValueError(
            f"Non-numeric RFM value at line {line_number}"
        ) from exc

    values = [recency, frequency, monetary]

    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"Non-finite RFM value at line {line_number}")

    if any(value < 0 for value in values):
        raise ValueError(f"Negative RFM value at line {line_number}")

    return customer_id, [
        recency,
        math.log1p(frequency),
        math.log1p(monetary)
    ]


def main():
    parser = argparse.ArgumentParser(
        description="Transform and Min-Max scale customer RFM features."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_DATA_DIR / "customer_rfm.tsv",
        help="Input RFM file (default: data/customer_rfm.tsv)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory for generated TSV and ARFF files"
    )
    args = parser.parse_args()

    source = args.input.expanduser()
    output_dir = args.output_dir.expanduser()

    if not source.is_file():
        raise FileNotFoundError(f"Input file not found: {source}")

    output_dir.mkdir(parents=True, exist_ok=True)

    scaled_file = output_dir / "customer_rfm_scaled.tsv"
    arff_file = output_dir / "customer_rfm_scaled.arff"

    mins = [float("inf")] * 3
    maxs = [float("-inf")] * 3
    count = 0

    # Pass 1: Calculate transformed feature ranges.
    with source.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="\x01")

        for line_number, row in enumerate(reader, start=1):
            _, values = parse_record(row, line_number)

            for index, value in enumerate(values):
                mins[index] = min(mins[index], value)
                maxs[index] = max(maxs[index], value)

            count += 1

    if count == 0:
        raise ValueError("Input RFM file is empty.")

    print("Records inspected:", count)
    print("Transformed minima:", mins)
    print("Transformed maxima:", maxs)

    # Handle constant features safely.
    ranges = [
        maxs[index] - mins[index]
        for index in range(3)
    ]

    # Pass 2: Scale records and generate TSV and ARFF.
    processed = 0

    with source.open(newline="", encoding="utf-8") as src, \
         scaled_file.open("w", newline="", encoding="utf-8") as tsv_out, \
         arff_file.open("w", encoding="utf-8") as arff_out:

        reader = csv.reader(src, delimiter="\x01")
        writer = csv.writer(tsv_out, delimiter="\t")

        writer.writerow([
            "customer_id",
            "recency",
            "frequency",
            "monetary"
        ])

        arff_out.write("@RELATION hm_customer_rfm\n\n")
        arff_out.write("@ATTRIBUTE recency NUMERIC\n")
        arff_out.write("@ATTRIBUTE frequency NUMERIC\n")
        arff_out.write("@ATTRIBUTE monetary NUMERIC\n\n")
        arff_out.write("@DATA\n")

        for line_number, row in enumerate(reader, start=1):
            customer_id, values = parse_record(row, line_number)

            scaled = [
                (value - mins[index]) / ranges[index]
                if ranges[index] > 0 else 0.0
                for index, value in enumerate(values)
            ]

            writer.writerow([customer_id] + scaled)

            arff_out.write(
                ",".join(f"{value:.10f}" for value in scaled) + "\n"
            )

            processed += 1

    if processed != count:
        raise RuntimeError(
            f"Record count changed between passes: "
            f"{count} inspected, {processed} processed"
        )

    print("\nPreprocessing completed successfully.")
    print("Customers processed:", processed)
    print("Scaled TSV:", scaled_file)
    print("Mahout ARFF:", arff_file)


if __name__ == "__main__":
    main()
