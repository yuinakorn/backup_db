import os
import time
import datetime
import pipes
from dotenv import dotenv_values

config_env = {
    **dotenv_values(".env"),  # load local file development variables
    **os.environ,  # override loaded values with system environment variables
}

BACKUP_PATH = '/backup/dbbackup'
DATETIME = time.strftime('%Y%m')
CUR_DIR = os.getcwd()

TODAYBACKUPPATH = CUR_DIR + BACKUP_PATH + '/' + DATETIME

# Checking if backup folder already exists or not. If not exists will create it.
try:
    os.stat(TODAYBACKUPPATH)
except:
    os.mkdir(TODAYBACKUPPATH, 0o755)

# print("checking for databases names file.")
# print(os.path.exists(CUR_DIR + DB_NAME))

# Starting actual database backup process.

DB_TABLE = '/backup/tableslist.txt'
print("[1].Checking for tables names file.")
print(os.path.exists(CUR_DIR + DB_TABLE))
file1 = open(CUR_DIR + DB_TABLE, "r")
Lines = file1.readlines()

count = 0
ln = ''
for line in Lines:
    count += 1
    ln += " " + line.strip()  # Strips the newline character

print("[2].Starting backup " + config_env['DB_NAME'] + " at " + time.strftime('%Y-%m-%d %H:%M:%S'))
db = config_env['DB_NAME']

dumpcmd = "mysqldump -h " + config_env['DB_HOST'] + " -u " + config_env['DB_USER'] + " -p" + \
          config_env['DB_USER_PASSWORD'] + " " + db + " " + \
          ln + " > " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
os.system(dumpcmd)

gzipcmd = "gzip " + pipes.quote(TODAYBACKUPPATH) + "/" + db + ".sql"
os.system(gzipcmd)

print("")

print("[3].The backup file have been created in '" + TODAYBACKUPPATH + "' directory")

print("Backup completed at " + time.strftime('%Y-%m-%d %H:%M:%S'))

print("")

print("[4].Starting to upload the backup to the server")

scpcmd = "sshpass -p " + "\"" + config_env['ROMOTE_PASSWORD'] + "\"" + " scp -P " + config_env['SSH_PORT'] + " " + \
         pipes.quote(TODAYBACKUPPATH) + \
         "/" + db + ".sql.gz " + config_env['REMOTE_USER'] + ":/var/backup/" + db + ".sql.gz"

if os.system(scpcmd) == 0:
    print("[5].Upload success")
    time.sleep(0.5)

    # write log file
    logfile = open(TODAYBACKUPPATH + '/log.txt', 'a')
    logfile.write(time.strftime('%Y-%m-%d %H:%M:%S') + " - Backup script completed." + "\n")
    print("[6].Upload completed to /var/backup/ directory")
    time.sleep(0.5)

    print("[7].Write log file success")
    time.sleep(0.5)

    # delete the local backup file
    os.remove(TODAYBACKUPPATH + "/" + db + ".sql.gz")
    print("[8].Local backup file deleted")

else:
    logfile = open(TODAYBACKUPPATH + '/log.txt', 'a')
    logfile.write(time.strftime('%Y-%m-%d %H:%M:%S') + " - Upload fail." + "\n")
    print("[8].Upload fail")
