import os
from datetime import datetime
import logging

class Logger(logging.Logger):
    def __init__(self, name="General", module_name="General", level=logging.DEBUG):
        super().__init__(module_name, level)

        current_date = datetime.now().strftime("%Y-%m-%d")
        log_dir = os.path.join(os.getcwd(), "Logs", current_date, module_name)

        os.makedirs(log_dir, exist_ok=True)
        log_filename = datetime.now().strftime("%H.%M.%S.log")
        log_path = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d : %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger instance
        self.addHandler(file_handler)

        self.create_symlink(log_path, os.path.join(log_dir, "log.log"))

    def create_symlink(self, target, link_name):
        try:
            if os.path.exists(link_name) or os.path.islink(link_name):
                os.remove(link_name)

            os.link(target, link_name)
            print("symlink created ", target, link_name)
        except OSError as e:
            print(f"Failed to create symlink: {e}")
