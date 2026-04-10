"""
Simple script to run the Triage-X API server.
"""
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Triage-X API Server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 Interactive docs at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
