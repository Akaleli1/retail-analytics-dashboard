# 🛒 E-Commerce & Retail Analytics Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Live Demo
👉 **[Click here to view the Live Dashboard](https://alaz-retail-analytics.streamlit.app/)** *(Replace the link above with your actual deployment URL)*

## 📖 Overview
This project is an end-to-end **Data Engineering & Business Intelligence** solution that analyzes sales data from a UK-based online retailer. It transforms raw transactional data into actionable insights using a custom ETL pipeline and visualizes key metrics through an interactive dashboard.

## ⚙️ Key Features
* **ETL Pipeline:** Built a robust data pipeline to ingest, clean, and transform raw CSV data (handling missing values, cancellations, and outliers).
* **Data Optimization:** Implemented ZIP file compression handling (`.zip` support) to optimize storage and deployment speed.
* **Interactive Filtering:** Users can filter data by **Country** and **Date Range**, with a smart "Select All" logic.
* **KPI Tracking:** Real-time calculation of Total Revenue, Order Count, and Average Order Value (AOV).
* **Advanced Visualization:**
    * **Sales Trends:** Time-series analysis with fixed-range, anti-pan interactions.
    * **Market Share:** Donut chart visualization for country-wise revenue distribution.
    * **Product Performance:** Top 5 best-selling products analysis.

## 🛠️ Tech Stack
* **Language:** Python 3.13
* **Framework:** Streamlit
* **Data Processing:** Pandas (ETL), SQLite (In-Memory SQL)
* **Visualization:** Plotly Express
* **Deployment:** Streamlit Community Cloud

## 📂 Project Structure
```bash
retail-analytics-dashboard/
├── data/
│   └── online_retail_II.zip    # Compressed raw dataset
├── src/
│   └── app.py                  # Main application source code
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation

🚀 How to Run Locally
Clone the repository

Bash

git clone [https://github.com/YourUsername/retail-analytics-dashboard.git](https://github.com/YourUsername/retail-analytics-dashboard.git)
cd retail-analytics-dashboard
Create a Virtual Environment (Optional but recommended)

Bash

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install Dependencies

Bash

pip install -r requirements.txt
Run the App

Bash

streamlit run src/app.py
Developed by Alaz