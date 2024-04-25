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


##########
import subprocess
import datetime
import getpass
from loguru import logger

def perform_backup(container_id, database_names_file):

    with open(database_names_file, 'r') as f:
        database_names = f.read().splitlines()
        logger.debug(f"Database Names : {database_names}")

    sudo_password = getpass.getpass("Enter the sudo password: ")

    for database_name in database_names:

        command = [
            'sudo', '-S', 'docker', 'exec', '-t', container_id, 'pg_dump', '-c', '-U', 'postgres', database_name
        ]

        timestamp = datetime.datetime.now().strftime('%d-%m-%Y_%H_%M_%S')
        filename = f"dump_{database_name}_{timestamp}.sql"

        with open(filename, 'w') as f:
            logger.debug(f"Taking backup of {database_name}...")
            subprocess.run(command, input=sudo_password, encoding='utf-8', stdout=f)



container_id = "aabf8316e748"
database_names_file = "database_names.txt"
logger.debug(f"Container ID : {container_id}")
perform_backup(container_id, database_names_file)
