import os
import zipfile
import shutil

def create_lambda_deployment_package():
    # Define paths
    base_dir = r"c:\Repositories\ai-chatbot-backend"
    venv_site_packages = os.path.join(base_dir, "venv", "Lib", "site-packages")
    zip_path = os.path.join(base_dir, "deployment.zip")
    
    # Files/folders to include from base_dir
    include_from_base = ["app", ".env", "requirements.txt"]
    
    # Remove existing zip if it exists
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"Creating deployment package at {zip_path}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add site-packages
        print(f"Adding dependencies from {venv_site_packages}...")
        for root, dirs, files in os.walk(venv_site_packages):
            # Skip some unnecessary directories to reduce size
            if "__pycache__" in root or "pip" in root or "setuptools" in root:
                continue
            for file in files:
                if file.endswith(".pyc"):
                    continue
                file_path = os.path.join(root, file)
                # The archive name should be relative to site-packages
                arcname = os.path.relpath(file_path, venv_site_packages)
                zipf.write(file_path, arcname)
                
        # 2. Add base files/folders
        for item in include_from_base:
            item_path = os.path.join(base_dir, item)
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    print(f"Adding directory {item}...")
                    for root, dirs, files in os.walk(item_path):
                        # skip __pycache__ etc
                        if "__pycache__" in root:
                            continue
                        for file in files:
                            if file.endswith(".pyc"):
                                continue
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, base_dir)
                            zipf.write(file_path, arcname)
                else:
                    print(f"Adding file {item}...")
                    zipf.write(item_path, item)
                    
    print("Deployment package created successfully!")

if __name__ == "__main__":
    create_lambda_deployment_package()
