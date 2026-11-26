# E-Commerce SQL Business Analytics

An end-to-end relational database and SQL business intelligence project demonstrating normalized star-schema design, advanced SQL querying (**CTEs**, **Window Functions**, **CLV Segmentation**), and automated KPI visualization.

## Database & Analytics Architecture
```mermaid
flowchart LR
    A[Normalized SQLite Schema<br/>Customers • Products • Orders] --> B[Advanced SQL Queries<br/>CTEs • LAG • DENSE_RANK]
    B --> C[Python & Pandas<br/>KPI Aggregation]
    C --> D[Executive Dashboard<br/>revenue_kpis.png]
<img width="1950" height="750" alt="descarga" src="https://github.com/user-attachments/assets/c8980b6a-77c0-45d6-872e-8ee305013df1" />

