import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger
import paramiko
from typing import List

from pydantic import BaseModel
import datetime

router = APIRouter()


class BackupRequest(BaseModel):
    host: str
    username: str
    password: str
    container_name: str
    database_names: List[str]


@router.post("/backup", tags=["Backup"])
def perform_backup(
        request: BackupRequest
):
    try:
        host = request.host
        username = request.username
        password = request.password
        container_name = request.container_name
        database_names = request.database_names

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        logger.debug(f"SSH Connection Established")

        for database_name in database_names:

            timestamp = datetime.datetime.now().strftime('%d-%m-%Y_%H_%M_%S')
            filename = f"dump_{timestamp}.sql"

            command = f'echo "{password}" | sudo -S docker exec -i {container_name} pg_dump -c -U postgres -h localhost -f - {database_name}'

            _, stdout, stderr = ssh.exec_command(command)

            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                error_message = stderr.read().decode('utf-8')
                logger.error(f"{error_message}")
                return {
                    "message": f"Error occurred during backup: {error_message}"
                }

            output = stdout.read().decode('utf-8')

            # Create a folder for the database if it doesn't exist
            folder_name = f"{database_name}_backups"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            file_path = os.path.join(folder_name, filename)

            with open(file_path, 'w') as f:
                logger.debug(f"Created .sql file")
                f.write(output)
            logger.debug(f"Backup completed successfully")

        ssh.close()
        logger.debug(f"SSH Connection Closed")

        return {
            "message": "Backup completed successfully."
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f'{e}')
        raise HTTPException(status_code=500, detail=f'{e}')

# import subprocess
# import datetime
# import getpass
# from loguru import logger
#
# def perform_backup(container_id, database_names_file):
#
#     with open(database_names_file, 'r') as f:
#         database_names = f.read().splitlines()
#         logger.debug(f"Database Names : {database_names}")
#
#     sudo_password = getpass.getpass("Enter the sudo password: ")
#
#     for database_name in database_names:
#
#         command = [
#             'sudo', '-S', 'docker', 'exec', '-t', container_id, 'pg_dump', '-c', '-U', 'postgres', database_name
#         ]
#
#         timestamp = datetime.datetime.now().strftime('%d-%m-%Y_%H_%M_%S')
#         filename = f"dump_{database_name}_{timestamp}.sql"
#
#         with open(filename, 'w') as f:
#             logger.debug(f"Taking backup of {database_name}...")
#             subprocess.run(command, input=sudo_password, encoding='utf-8', stdout=f)
#
#
#
# container_id = "aabf8316e748"
# database_names_file = "database_names.txt"
# logger.debug(f"Container ID : {container_id}")
# perform_backup(container_id, database_names_file)
