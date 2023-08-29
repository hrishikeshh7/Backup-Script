from fastapi import FastAPI
from uvicorn import run
from loguru import logger
from src.routes.all_routes import router as all_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Docker Service Manager")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.include_router(all_routes)

if __name__ == "__main__":
    logger.info("Started main")

    try:
        run("main:app", host="0.0.0.0", port=5000, reload=True)

    except Exception as err:
        logger.error("Some Error occurrred...{}".format(err))


