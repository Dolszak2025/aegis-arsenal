from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Aegis Arsenal")

# Mount static files directory if it exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page with Vercel Speed Insights"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aegis Arsenal</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #fff;
                min-height: 100vh;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            p {
                font-size: 1.2rem;
                line-height: 1.6;
                opacity: 0.9;
            }
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 30px;
                margin-top: 30px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            .feature {
                margin: 20px 0;
                padding: 15px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <h1>🛡️ Aegis Arsenal</h1>
        <p>A FastAPI-powered application with Vercel Speed Insights</p>
        
        <div class="card">
            <h2>Features</h2>
            <div class="feature">
                <strong>⚡ Fast API Backend</strong>
                <p>Built with FastAPI for high performance</p>
            </div>
            <div class="feature">
                <strong>📊 Vercel Speed Insights</strong>
                <p>Real-time performance monitoring enabled</p>
            </div>
            <div class="feature">
                <strong>🚀 Production Ready</strong>
                <p>Optimized for deployment on Vercel</p>
            </div>
        </div>

        <!-- Vercel Speed Insights -->
        <script>
            window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
        </script>
        <script defer src="/_vercel/speed-insights/script.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Aegis Arsenal is running"}


@app.get("/api/info")
async def info():
    """Application information endpoint"""
    return {
        "name": "Aegis Arsenal",
        "version": "1.0.0",
        "framework": "FastAPI",
        "features": [
            "Vercel Speed Insights",
            "RESTful API",
            "Static File Serving"
        ]
    }
