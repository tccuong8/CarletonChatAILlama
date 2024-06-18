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


for i in range(len(data['Article_Text'])):
    current_line = data['Article_Text'][i]
    current_line = (list(current_line))
    one_line = ""
    for character in current_line:
        if character != "\n": one_line += character 
        else: one_line += " "
    data['Article_Text'][i] = (one_line)

# Save the updated DataFrame back to a CSV file
data.to_csv('formatted_file_fix.csv', index=False)
