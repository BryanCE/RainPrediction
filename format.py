import os
import json

def process_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            year = int(filename.split('_')[1].split('.')[0])
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)

            modified_data = []
            for item in data:
                item['Year'] = year
                modified_data.append(item)

            output_filename = f"output_{filename}"
            output_file_path = os.path.join(directory, output_filename)
            with open(output_file_path, 'w') as file:
                json.dump(modified_data, file, indent=4)

            print(f"Processed file: {filename}")

if __name__ == '__main__':
    directory = 'path/to/directory'
    process_files(directory)