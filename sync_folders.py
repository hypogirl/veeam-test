import os
import shutil
import time
import argparse
import logging
from hashlib import md5

def calculate_md5(file_path):
    hash_md5 = md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_folders(source, replica):
    if not os.path.exists(replica):
        os.makedirs(replica)
    
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)
        
        for dir in dirs:
            replica_dir = os.path.join(replica_root, dir)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                logging.info(f"created directory: {replica_dir}")
        
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)
            
            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"copied file: {source_file} to {replica_file}")
    
    for root, dirs, files in os.walk(replica):
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"removed file: {replica_file}")

        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_root, dir)
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logging.info(f"removed directory: {replica_dir}")

def main():
    parser = argparse.ArgumentParser(description="folder synchronization program")
    parser.add_argument("source", help="source folder path")
    parser.add_argument("replica", help="replica folder path")
    parser.add_argument("interval", type=int, help="synchronization interval in seconds")
    parser.add_argument("log_file", help="log file path")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[
        logging.FileHandler(args.log_file),
        logging.StreamHandler()
    ])
    
    source = args.source
    replica = args.replica
    interval = args.interval
    
    logging.info("starting synchronization")

    while True:
        sync_folders(source, replica)
        logging.info(f"synchronization complete. sleeping for {interval} second{'' if interval == 1 else 's'}")
        time.sleep(interval)
        logging.info("starting synchronization")

if __name__ == "__main__":
    main()