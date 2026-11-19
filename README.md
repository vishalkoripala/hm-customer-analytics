# H&M Customer Analytics and Customer Segmentation

A Big Data Analytics project that uses **Apache Hadoop, HDFS, Apache Hive, and Apache Mahout** to analyze the H&M Personalized Fashion Recommendations dataset. The project performs large-scale retail transaction analysis, RFM-based customer segmentation using K-Means clustering, and interactive visualization through a Streamlit dashboard.

---

## 1. Project Overview

The project analyzes customer transactions, demographic information, and product details from the H&M retail dataset to identify purchasing patterns and understand customer behavior.

It combines distributed data storage, SQL-based analytics, customer-level feature engineering, and unsupervised machine learning to generate meaningful business insights.

### Objectives

- Process large-scale retail transaction data using Hadoop and HDFS.
- Perform structured analytics using Apache Hive.
- Analyze customer purchasing behavior using Recency, Frequency, and Monetary (RFM) metrics.
- Apply K-Means clustering using Apache Mahout.
- Map clustering results back to individual customer records.
- Visualize customer segments and analytical findings through an interactive dashboard.

---

## 2. Dataset

**Dataset:** H&M Personalized Fashion Recommendations
**Source:** Kaggle

Dataset: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data

The dataset contains three primary files:

| File | Description |
|---|---|
| `transactions_train.csv` | Customer purchase transaction records |
| `customers.csv` | Customer demographic and profile information |
| `articles.csv` | Product and article information |

### Dataset Characteristics

| Attribute | Approximate Records |
|---|---:|
| Transactions | 31.8 million |
| Customers | 1.37 million |
| Articles | 105,542 |

The original Kaggle dataset is not included in this repository. It must be downloaded separately from Kaggle.

---

## 3. Technology Stack

| Technology | Version / Purpose |
|---|---|
| Apache Hadoop | 3.3.6 – Distributed processing |
| HDFS | Distributed file storage |
| Apache Hive | 4.1.0 – SQL-based analytics |
| Apache Mahout | 0.13.0 – K-Means clustering |
| Java | 17 – Cluster extraction utility |
| Python | Data preprocessing and customer mapping |
| Pandas | Data manipulation |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |

---

## 4. Project Architecture

```text
                 H&M Kaggle Dataset
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
     Transactions      Customers        Articles
          |               |               |
          +---------------+---------------+
                          |
                          v
                     Hadoop HDFS
                          |
                          v
                     Apache Hive
                          |
             +------------+------------+
             |                         |
             v                         v
     Transaction Analytics       Customer RFM
             |                         |
             |                         v
             |                  RFM Preprocessing
             |                         |
             |                         v
             |                   Feature Scaling
             |                         |
             |                         v
             |                  Apache Mahout
             |                    K-Means
             |                         |
             |                         v
             |                  Cluster Extraction
             |                         |
             |                         v
             |                  Customer Mapping
             |                         |
             +------------+------------+
                          |
                          v
                 Analytical CSV Files
                          |
                          v
                 Streamlit Dashboard
                          |
                          v
                  Business Insights
```

---

## 5. Implementation

### 5.1 Hadoop and HDFS

Apache Hadoop was configured to support distributed storage and processing.

HDFS was used to store the large-scale H&M transaction dataset and provide the storage foundation for subsequent analytics.

The implementation included:
- Hadoop service configuration.
- HDFS directory creation and dataset storage.
- Data reading and storage verification.
- Hadoop and YARN service monitoring.

### 5.2 Apache Hive Analytics

A Hive database named `hm_customer_analytics` was created.

The following tables were used:

- `transactions`
- `customers`
- `articles`
- `customer_rfm`

The Hive analysis covered:

| Analysis | Purpose |
|---|---|
| Monthly transaction trends | Understand purchasing activity over time |
| Sales channel distribution | Compare transaction channels |
| Product category analysis | Identify popular product categories |
| Customer age-group analysis | Understand purchasing patterns across age groups |
| Top-selling articles | Identify frequently purchased articles |

The transaction analytics covered approximately 31.8 million transaction records.

### 5.3 RFM Feature Engineering

Customer purchasing behavior was represented using three metrics:

| Metric | Description |
|---|---|
| Recency | Number of days since the customer's latest purchase |
| Frequency | Number of transactions made by the customer |
| Monetary | Sum of the customer's transaction price values |

The reference date used for calculating recency was **September 22, 2020**.

#### Preprocessing Steps

1. Aggregate transaction records at the customer level.
2. Calculate Recency, Frequency, and Monetary values.
3. Apply `log1p` transformation to Frequency and Monetary.
4. Apply Min-Max scaling to the three RFM features.
5. Prepare the scaled feature vectors for clustering.

The resulting customer-level dataset was used as the input for Apache Mahout.

**Note:** Monetary values represent the normalized source price values and should not be interpreted as Indian Rupees.

### 5.4 Customer Segmentation Using Apache Mahout

Apache Mahout was used to perform K-Means clustering on the scaled RFM feature vectors.

**Selected number of clusters: K = 5**

The clustering process was executed using Hadoop MapReduce.

The implementation included:
- Preparing customer RFM vectors.
- Executing Mahout K-Means clustering.
- Extracting cluster assignments using `ExtractClusters.java`.
- Mapping cluster assignments to customer-level records using Python.

### 5.5 Customer Mapping and Validation

The extracted cluster assignments were mapped back to the original customer RFM records.

The final mapping was validated to check for unmatched and duplicate customer identifiers.

| Validation Metric | Result |
|---|---:|
| Total customer records mapped | 1,362,281 |
| Unmatched records | 0 |
| Duplicate customer IDs | 0 |
| Number of clusters | 5 |

This validation confirms that every customer record in the processed RFM dataset was successfully associated with a cluster.

### 5.6 Interactive Streamlit Dashboard

A Streamlit dashboard was developed to make the analytical results accessible through an interactive interface.

The dashboard contains six sections:

| Section | Description |
|---|---|
| Dataset Overview | Dataset summary and key metrics |
| Customer Segmentation | Cluster distribution and customer segmentation visualization |
| RFM Analysis | Recency, Frequency, and Monetary analysis |
| Customer Explorer | Explore customer-level records |
| Business Insights | Interpret customer behavior and segment characteristics |
| Sales & Transaction Analytics | Monthly trends, channels, categories, age groups, and top articles |

Plotly is used to provide interactive charts and visualizations.

For performance, the RFM scatter visualization uses a sample of up to 30,000 records. Other customer-level metrics use the full available dataset.

---

## 6. Key Results

### 6.1 Transaction Analytics

The Hive analysis produced the following findings:

| Finding | Result |
|---|---:|
| Transactions analyzed | Approximately 31.8 million |
| Channel 1 transaction share | 29.60% |
| Channel 2 transaction share | 70.40% |
| Highest transaction age group | 20–29 years |
| Leading product type | Trousers |
| Trousers transactions | 4,217,017 |
| Top-selling article | `0706016001` |
| Transactions for top article | 50,287 |

### 6.2 Customer Segmentation Results

The K-Means implementation generated five customer clusters.

Their characteristics were interpreted using the cluster RFM profiles:

| Cluster ID | Customer Characteristics |
|---|---|
| 737932 | Very recent purchases, high frequency, and high monetary value |
| 1325946 | Less recent or inactive customers with low frequency and monetary value |
| 332505 | Recent customers with low frequency and monetary value |
| 652544 | Recent customers with medium-to-high frequency and moderate monetary value |
| 781725 | Customers with moderate recency, lower frequency, and lower spending |

**Important:** Cluster IDs are identifiers generated by Mahout. They do not represent rankings or customer value scores.

---

## 7. Repository Structure

```text
hm-customer-analytics/
│
├── dashboard/
│   ├── app.py
│   └── data/
│       ├── age_groups.csv
│       ├── channel_distribution.csv
│       ├── monthly_trends.csv
│       ├── product_categories.csv
│       └── top_articles.csv
│
├── data/
│   ├── customer_clusters_final.csv.gz
│   └── customer_rfm.tsv.gz
│
├── screenshots/
│   ├── dashboard/
│   ├── hadoop/
│   ├── hdfs/
│   ├── hive/
│   ├── mahout/
│   └── rfm/
│
├── ExtractClusters.java
├── create_customer_mapping.py
├── preprocess_rfm.py
├── rfm_dictionary
├── requirements.txt
├── .gitignore
└── README.md
```

### Important Files

| File | Purpose |
|---|---|
| `dashboard/app.py` | Streamlit dashboard application |
| `preprocess_rfm.py` | RFM feature preprocessing and scaling |
| `ExtractClusters.java` | Extracts cluster assignments from Mahout output |
| `create_customer_mapping.py` | Maps extracted clusters to customer records |
| `rfm_dictionary` | RFM feature description |
| `requirements.txt` | Python dashboard dependencies |
| `data/customer_rfm.tsv.gz` | Compressed customer RFM data |
| `data/customer_clusters_final.csv.gz` | Compressed final customer-cluster mapping |

Intermediate Hadoop, Hive, and Mahout files are generated during processing and are not required to launch the dashboard.

---

## 8. Running the Dashboard

The repository includes the analytical CSV files and compressed customer-level datasets required by the dashboard.

### Prerequisites

- Python 3.10 or later
- pip
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/vishalkoripala/hm-customer-analytics.git
cd hm-customer-analytics
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The project dependencies are:

```text
streamlit==1.67.0
pandas==3.1.1
plotly==7.1.0
```

### Step 4: Launch the Dashboard

Run the following command from the project root:

```bash
streamlit run dashboard/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

The dashboard reads the analytical CSV files from `dashboard/data/` and the compressed customer-level datasets from `data/`.

---

## 9. Limitations

- The original H&M dataset must be downloaded separately from Kaggle.
- The monetary metric uses normalized source price values and should not be interpreted as Indian Rupees.
- The project analyzes historical transaction data rather than real-time transaction streams.
- The RFM scatter visualization uses a sample of up to 30,000 records to improve rendering performance.
- The project uses five clusters; other values of K and alternative clustering algorithms could be explored.
- The dashboard depends on the availability of its included analytical data files.

---

## 10. Future Enhancements

- Integrate recommendation algorithms for personalized product suggestions.
- Introduce customer lifetime value estimation.
- Explore alternative clustering algorithms and compare segmentation quality.
- Implement incremental processing for newly arriving transactions.
- Extend the dashboard with predictive analytics.
- Deploy the dashboard to a cloud platform.

---

## 11. Author

**Vishal Koripala**

B.Tech – Computer Science and Engineering (AI & ML)
Anil Neerukonda Institute of Technology & Sciences

---

## 12. License and Dataset Attribution

This repository contains project source code, implementation evidence, and derived analytical outputs.

The original dataset is provided by H&M through the Kaggle competition. Users should obtain the dataset directly from Kaggle and follow its competition rules and applicable terms.

---

## 13. Implementation Screenshots

The following screenshots provide evidence of the practical implementation of Hadoop, HDFS, Apache Hive, RFM preprocessing, Apache Mahout, and the interactive dashboard.

### 13.1 Hadoop and YARN

**Hadoop Services**

![Hadoop Services](screenshots/hadoop/hadoop-services.png)

**YARN Node Status**

![YARN Node Status](screenshots/hadoop/yarn-node-status.png)

**YARN Job History**

![Job History](screenshots/hadoop/job-history.png)

### 13.2 HDFS – Distributed Storage

**HDFS Directory Structure**

![HDFS Directory Structure](screenshots/hdfs/hdfs-directory-structure.png)

**Dataset Storage**

![HDFS Dataset Storage](screenshots/hdfs/hdfs-dataset-storage.png)

**HDFS Storage Usage**

![HDFS Storage Usage](screenshots/hdfs/hdfs-storage-usage.png)

**Reading Dataset from HDFS**

![HDFS Data Read](screenshots/hdfs/hdfs-data-read.png)

**HDFS Block Verification**

![HDFS Block Verification](screenshots/hdfs/hdfs-block-verification.png)

### 13.3 Apache Hive – Data Analytics

**Transaction Data Preview**

![Hive Transaction Preview](screenshots/hive/hive-transaction-data-preview.png)

**Monthly Transaction Analysis**

![Monthly Transaction Analysis](screenshots/hive/hive-monthly-transaction-analysis.png)

**Sales Channel Distribution**

![Sales Channel Distribution](screenshots/hive/hive-sales-channel-distribution.png)

**Product Category Analysis**

![Product Category Analysis](screenshots/hive/hive-product-category-analysis.png)

**Customer Age-Group Analysis**

![Hive Customer Age Analysis](screenshots/hive/hive-customer-age-analysis.png)

**Top-Selling Articles**

![Hive Top Selling Articles](screenshots/hive/hive-top-selling-articles.png)

### 13.4 RFM Feature Engineering

**RFM Preprocessing, Statistical Summary and Feature Scaling**

![RFM Preprocessing and Scaling](screenshots/rfm/rfm-preprocessing-and-scaling.png)

### 13.5 Apache Mahout – K-Means Clustering

**K-Means Cluster Distribution and Customer Mapping Validation**

![Mahout K-Means Clustering and Validation](screenshots/mahout/mahout-kmeans-clustering-validation.png)

### 13.6 Interactive Dashboard

**Dataset Overview**

![Dataset Overview](screenshots/dashboard/dataset-overview.png)

**Customer Segmentation**

![Customer Segmentation](screenshots/dashboard/customer-segmentation.png)

**RFM Analysis**

![RFM Analysis 1](screenshots/dashboard/rfm-analysis-1.png)

![RFM Analysis 2](screenshots/dashboard/rfm-analysis-2.png)

**Sales and Transaction Analytics**

![Sales Analytics 1](screenshots/dashboard/sales-analytics-1.png)

![Sales Analytics 2](screenshots/dashboard/sales-analytics-2.png)
