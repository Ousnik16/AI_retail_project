# Smart Retail Intelligence & Recommendation System

A beginner-friendly, production-style AI-powered retail analytics platform built with FastAPI, React, MongoDB Atlas, PySpark data processing, and ML/LLM modules.

## Features

- Transaction management API for customers, orders, products, inventory, and reviews
- Batch analytics and customer segmentation
- Product recommendation engine with content-based and collaborative filtering
- Demand forecasting using Prophet
- Sentiment analysis for customer reviews
- LLM-powered retail intelligence summaries
- React dashboard with Tailwind UI and charts
- Docker and Docker Compose for local development
- GitHub Actions CI pipeline

## Architecture

React Dashboard -> FastAPI Backend -> MongoDB Atlas -> PySpark Batch Processing -> ML Recommendation Engine -> LLM Retail Intelligence

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- MongoDB Atlas or local MongoDB instance
- Ollama Cloud account with API key

### Local setup

1. Copy environment variables:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Update `backend/.env` with your MongoDB connection and Ollama Cloud API credentials:
   ```
   OLLAMA_API_KEY=your_ollama_cloud_api_key
   OLLAMA_BASE_URL=https://ollama.com
   OLLAMA_MODEL=gpt-oss:20b
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd ../frontend
   npm install
   ```
5. Run the backend:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
6. Run the frontend:
   ```bash
   cd ../frontend
   npm run dev -- --host 0.0.0.0
   ```

## Project Structure

- `backend/app` - FastAPI application, routes, services, models, ML modules, and PySpark jobs
- `frontend` - React dashboard and UI components
- `data` - sample CSV dataset for product cleaning and analytics
- `.github/workflows/ci.yml` - CI pipeline for build checks

## API Endpoints

- `POST /api/auth/login`
- `POST /api/auth/register`
- `GET /api/products`
- `POST /api/products`
- `POST /api/transactions`
- `GET /api/analytics/customers`
- `GET /api/analytics/sales`
- `GET /api/recommendations/user/{user_id}`
- `GET /api/recommendations/product/{product_id}`
- `GET /api/forecasting/product/{product_id}`
- `GET /api/reviews/sentiment`
- `GET /api/insights/summary?question=...`

## Notes

- Replace placeholder API keys and hashed passwords before production use.
- Use MongoDB Atlas connection string in `backend/.env`.
- The LLM module uses Ollama Cloud with the configured `OLLAMA_MODEL`.
- Use `backend/scripts/sample_data.py` to seed sample documents in MongoDB.

## Next Improvements

- Add full role-based authorization and admin dashboards
- Implement reusable token refresh flows and secure auth middleware
- Add more advanced PySpark batch analytics and scheduled jobs
- Integrate additional Ollama models for specialized retail analytics
- Add product clustering, basket analysis, and association rule mining
