"""
Startup script for the RAG chatbot backend with visual progress indicators.
This ensures all services are pre-warmed before accepting requests.
"""

import sys
import time
import uvicorn
from app.core.config import settings


def print_banner():
    """Print startup banner."""
    print("\n" + "=" * 70)
    print(" 🚀 AAOIFI Standards RAG Chatbot - Backend Server")
    print("=" * 70)
    print(f" Mode: {'🔧 Development' if settings.debug else '🚀 Production'}")
    print(f" API: http://localhost:8000")
    print(f" Docs: http://localhost:8000/docs")
    print("=" * 70 + "\n")


def main():
    """Start the server with pre-warming."""
    print_banner()

    print("📦 Loading application...")

    # Run the server (pre-warming happens in lifespan)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Server failed to start: {e}")
        sys.exit(1)
