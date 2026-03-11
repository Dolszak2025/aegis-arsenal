# Aegis Arsenal

A FastAPI application with Vercel Speed Insights integration for real-time performance monitoring.

## Features

- 🚀 **FastAPI Backend**: High-performance Python web framework
- 📊 **Vercel Speed Insights**: Real-time performance monitoring
- ⚡ **Optimized Deployment**: Ready for Vercel serverless deployment
- 🔧 **RESTful API**: Clean API endpoints for health checks and information

## Local Development

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher (for Speed Insights package)

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
# or
uvicorn main:app --reload
```

4. Open [http://localhost:8000](http://localhost:8000) in your browser.

## Deployment

### Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel deploy
```

3. Enable Speed Insights:
   - Go to your Vercel dashboard
   - Select your project
   - Navigate to Speed Insights in the sidebar
   - Click "Enable"

## API Endpoints

- `GET /` - Main application page with Speed Insights
- `GET /api/health` - Health check endpoint
- `GET /api/info` - Application information

## Speed Insights

This project uses Vercel Speed Insights to monitor real user performance metrics. The Speed Insights script is automatically loaded on the main page using the recommended script injection method for non-framework applications.

## License

MIT
