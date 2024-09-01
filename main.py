import uvicorn
import sys


if __name__ == "__main__":
    print("Running main.py")
    
    uvicorn.run(
        "app.api:apiApp",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # ssl_keyfile="./key.pem",
        # ssl_certfile="./cert.pem"
        log_level="info",
    )
