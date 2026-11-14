import csv
from collections import Counter

BASE = "/home/vishalkoripala/hm_clustering/data"

scaled_file = f"{BASE}/customer_rfm_scaled.tsv"
cluster_file = f"{BASE}/extracted_clusters.tsv"
output_file = f"{BASE}/customer_clusters_final.csv"

def vector_key(values):
    return tuple(f"{float(x):.10f}" for x in values)

# Build vector-to-cluster lookup
vector_to_cluster = {}

with open(cluster_file) as f:
    for line in f:
        cluster, r, freq, monetary = line.strip().split("\t")
        key = vector_key((r, freq, monetary))

        if key in vector_to_cluster and vector_to_cluster[key] != cluster:
            raise ValueError(f"Conflicting cluster assignment: {key}")

        vector_to_cluster[key] = cluster

print("Unique vector mappings:", len(vector_to_cluster))

matched = 0
unmatched = 0
cluster_counts = Counter()

with open(scaled_file, newline="") as source, \
     open(output_file, "w", newline="") as destination:

    reader = csv.reader(source, delimiter="\t")
    writer = csv.writer(destination)

    header = next(reader)
    writer.writerow(["customer_id", "cluster_id"])

    for row in reader:
        if len(row) < 4:
            continue

        customer_id = row[0]
        key = vector_key(row[1:4])

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
print("Cluster distribution:")

for cluster, count in sorted(cluster_counts.items()):
    print(cluster, count)

print("Total mapped:", sum(cluster_counts.values()))
print("Output:", output_file)

if matched != 1362281 or unmatched != 0:
    raise SystemExit("VALIDATION FAILED")

print("\nSUCCESS: All customer IDs mapped and validated.")
