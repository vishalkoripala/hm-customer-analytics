import csv
import math
import os

base = os.path.expanduser("~/hm_clustering/data")
source = os.path.join(base, "customer_rfm.tsv")

scaled_file = os.path.join(base, "customer_rfm_scaled.tsv")
arff_file = os.path.join(base, "customer_rfm_scaled.arff")

mins = [float("inf")] * 3
maxs = [float("-inf")] * 3
count = 0

# Pass 1: Find exact feature ranges after transformations
with open(source, newline="") as f:
    for row in csv.reader(f, delimiter="\x01"):
        if len(row) != 4:
            raise ValueError(f"Invalid row: {row}")
        values = [
            float(row[1]),
            math.log1p(float(row[2])),
            math.log1p(float(row[3]))
        ]
        for i, value in enumerate(values):
            mins[i] = min(mins[i], value)
            maxs[i] = max(maxs[i], value)
        count += 1

print("Records inspected:", count)
print("Transformed minima:", mins)
print("Transformed maxima:", maxs)

# Pass 2: Scale all records and write outputs
with open(source, newline="") as src, \
     open(scaled_file, "w", newline="") as out, \
     open(arff_file, "w") as arff:

    writer = csv.writer(out, delimiter="\t")
    writer.writerow(["customer_id", "recency", "frequency", "monetary"])

    arff.write("@RELATION hm_customer_rfm\n\n")
    arff.write("@ATTRIBUTE recency NUMERIC\n")
    arff.write("@ATTRIBUTE frequency NUMERIC\n")
    arff.write("@ATTRIBUTE monetary NUMERIC\n\n")
    arff.write("@DATA\n")

    processed = 0

    for row in csv.reader(src, delimiter="\x01"):
        customer_id = row[0]

        values = [
            float(row[1]),
            math.log1p(float(row[2])),
            math.log1p(float(row[3]))
        ]

        scaled = [
            (v - mins[i]) / (maxs[i] - mins[i])
            for i, v in enumerate(values)
        ]

        writer.writerow([customer_id] + scaled)
        arff.write(",".join(f"{v:.10f}" for v in scaled) + "\n")
        processed += 1

print("\nPreprocessing completed.")
print("Customers processed:", processed)
print("Scaled TSV:", scaled_file)
print("Mahout ARFF:", arff_file)
