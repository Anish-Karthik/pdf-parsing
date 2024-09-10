import os
import json
import pandas as pd

# Directory containing the JSON files
input_dir = 'sat/writing-comp-output'

# List to store the rows for the Excel sheet
rows = []

# Read and process each JSON file
for filename in sorted(os.listdir(input_dir)):
    if filename.endswith('.json'):
        filepath = os.path.join(input_dir, filename)
        
        with open(filepath, 'r') as file:
            data = json.load(file)
            
            for item in data["questions"]:
                # print(item)
                qno = item.get('qno', '')
                description = item.get('description', '').replace("\u2019", "'").replace("\u00e9", "é")
                if description == "":
                    description = "Choose the correct answer from the options below."
                options = item.get('options', [])
                correct_option = item.get('correct_option', '')
                
                # Extracting options
                option_a = options[0]['description'].strip() if len(options) > 0 else ''
                option_b = options[1]['description'].strip() if len(options) > 1 else ''
                option_c = options[2]['description'].strip() if len(options) > 2 else ''
                option_d = options[3]['description'].strip() if len(options) > 3 else ''
                
                # Append to rows list
                rows.append([qno, description, option_a, option_b, option_c, option_d, correct_option,'Writing Comprehension'])

# Create DataFrame from rows
df = pd.DataFrame(rows, columns=['S NO', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Answer','Topic'])

# Write to Excel file
output_file = 'output2.xlsx'
df.to_excel(output_file, index=False)

print(f"Excel file '{output_file}' created successfully.")
