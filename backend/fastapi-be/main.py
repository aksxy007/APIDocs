# main.py
import uvicorn
from app import app

def main():
    from configs.logger import get_custom_logger
    logger = get_custom_logger(__name__)
    logger.info("Starting the FastAPI application with Uvicorn")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_config=None,  # disable default logging, because we configured our own
        reload=True       # enable reload, logger setup will rerun thanks to main() guard
    )

if __name__ == "__main__":
    main()
