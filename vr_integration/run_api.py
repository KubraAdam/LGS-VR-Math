"""
API Server Runner
Convenience script to run the API server
"""

import os
import sys
import uvicorn

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Run API server
    uvicorn.run(
        "vr_integration.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

