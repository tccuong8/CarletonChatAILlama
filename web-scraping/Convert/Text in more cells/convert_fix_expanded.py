import pandas as pd
from bs4 import BeautifulSoup

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('article_text_expanded.csv')
# print((data['Article_Text_0']))
# quit()

# Function to extract text from HTML
def html_to_text(html):
    if isinstance(html, str):
        soup = BeautifulSoup(html, 'html.parser')
        # Extract text from the HTML
        text = soup.get_text(separator='\n', strip=True)
        return text

# Apply the function to the 'Article_Text' column
data['Article_Text_0'] = data['Article_Text_0'].apply(html_to_text)


for i in range(len(data['Article_Text_0'])):
    current_line = data['Article_Text_0'][i]
    try:
        current_line = (list(current_line))
        one_line = ""
        for character in current_line:
            if character != "\n": one_line += character 
            else: one_line += " "
        split_lines = one_line.split(". ")
        for j in range(len(split_lines)):
            try: data[f'Article_Text_{j}'][i] = (split_lines[j])
            except: pass
    except: continue

# Save the updated DataFrame back to a CSV file
data.to_csv('formatted_file_fix_expanded.csv', index=False)
