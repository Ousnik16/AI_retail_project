# Documentation

## Setup Guide

1. Install Python 3.11, Node.js 20, Docker, and MongoDB Atlas or local MongoDB.
2. Configure environment variables in `backend/.env`.
3. Seed sample datasets using `backend/scripts/sample_data.py`.
4. Run backend and frontend locally, or use Docker Compose.

## MongoDB Atlas

- Create a free cluster on MongoDB Atlas.
- Create a database named `retail_intelligence`.
- Add collections: `users`, `products`, `transactions`, `reviews`, `forecasts`, `recommendations`, `customer_segments`, `inventory`.
- Use the connection URI in `backend/.env`.

## PySpark Batch Jobs

- Run data cleaning job with:
  ```bash
  python backend/app/pyspark_jobs/cleaning.py
  ```
- Place raw CSV data in the root `data/` folder.
- Cleaned output is written to `data/cleaned_products`.
