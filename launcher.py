import subprocess
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, shell=False):
    logging.info(f"Running command: {command}")
    result = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(f"STDOUT: {result.stdout.decode()}")
    logging.error(f"STDERR: {result.stderr.decode()}")
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}")

def main():
    activate_script = ".\\env\\Scripts\\activate.bat"
    batch_script = "temp_script.bat"
    with open(batch_script, "w") as file:
        file.write(f"@echo off\n")
        file.write(f"call {activate_script}\n")
        file.write(f"pip install ffmpeg\n")
        file.write(f"pip install -r requirements.txt\n")
        file.write(f"streamlit run app.py\n")

    run_command(batch_script, shell=True)
    os.remove(batch_script)

if __name__ == "__main__":
    main()
