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

            output_filename = f"precip_{year}.json"
            output_file_path = os.path.join(directory, output_filename)
            with open(output_file_path, 'w') as file:
                json.dump(modified_data, file, indent=4)

            print(f"Processed file: {filename}")

def process_file(file):
    if file.endswith('.json'):
        year = int(file.split('_')[1].split('.')[0])
        file_path = os.path.join(os.getcwd(), file)
        with open(file_path, 'r') as file:
            data = json.load(file)

        modified_data = []
        for item in data:
            item['Year'] = year
            modified_data.append(item)

        output_filename = f"precip_{year}.json"
        output_file_path = os.path.join(os.getcwd(), output_filename)
        with open(output_file_path, 'w') as file:
            json.dump(modified_data, file, indent=4)

        print(f"Processed file: {file}")

if __name__ == '__main__':
    #directory = os.getcwd()
    #directory = os.path.join(directory, 'backups/backups/rainfall_2013.json')
    file = "backups/rainfall_2013.json"
    process_file(file)