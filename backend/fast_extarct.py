import os
import zipfile

# Set up the paths
base_dir = os.getcwd()
zip_dir = os.path.join(base_dir, 'zip_files')
parsed_dir = os.path.join(base_dir, 'parsed_files')

# Loop through every zip file you just pasted
for zip_name in os.listdir(zip_dir):
    if zip_name.endswith('.zip'):
        # Create a matching folder name (e.g., 'ash_handling' for 'ash_handling.zip')
        folder_name = zip_name.replace('.zip', '')
        extract_path = os.path.join(parsed_dir, folder_name)
        
        # Make the individual folder
        os.makedirs(extract_path, exist_ok=True)
        
        # Extract the contents into that folder
        zip_path = os.path.join(zip_dir, zip_name)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
            
        print(f"Successfully extracted into parsed_files/{folder_name}")

print("\nTime skip complete: All documents are 'parsed' and ready!")