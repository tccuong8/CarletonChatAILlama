import pandas as pd
from bs4 import BeautifulSoup

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('article_text.csv')

# Function to extract text from HTML
def html_to_text(html):
    if isinstance(html, str):
        soup = BeautifulSoup(html, 'html.parser')
        # Extract text from the HTML
        text = soup.get_text(separator='\n', strip=True)
        return text

# Apply the function to the 'Article_Text' column
data['Article_Text'] = data['Article_Text'].apply(html_to_text)

valid_symbols = []
invalid_symbols = []
file = open("filter.txt","w")

for i in range(len(data['Article_Text'])):
    current_line = data['Article_Text'][i]
    current_line = (list(current_line))
    one_line = ""
    for character in current_line:
        if character in invalid_symbols: continue # remove symbols that might be preventing the Assistant from accepting the file
        if character not in valid_symbols: 
            try: 
                file.write(str(character))
                valid_symbols.append(character)
            except: 
                invalid_symbols.append(character)
        if character != "\n": one_line += character # remove in-csv-cell newlines
        else: one_line += " "
    data['Article_Text'][i] = (one_line)
file.close()

# Save the updated DataFrame back to a CSV file
data.to_csv('formatted_file_fix_standard.csv', index=False)

