import subprocess
import os
from datetime import date


db_passwd = os.getenv("DB_PASSWD", 'postgres')
pg_dump_path =  os.getenv("PG_DUMP_PATH")

def backup(db_url: str, backup_dir_path: str):
    command = '"{}" --format=c --dbname=postgresql://{} > "{}".dmp' \
              .format(pg_dump_path, db_url, os.path.join(backup_dir_path, str(date.today())))
    try:
        proc = subprocess.Popen(command, shell=True, env={
            'PGPASSWORD': db_passwd,
            'SYSTEMROOT': os.environ['SYSTEMROOT']  # Windows-only; https://stackoverflow.com/a/73317093
        })
        proc.wait()
        print('Backup successful')
    except Exception as e:
        print('Exception happened during backup:\n', e)