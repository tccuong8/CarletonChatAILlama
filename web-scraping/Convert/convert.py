import pandas as pd
from bs4 import BeautifulSoup

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('article_text.csv')

# Function to extract text from HTML
def html_to_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Extract text from the HTML
    text = soup.get_text(separator='\n', strip=True)
    return text

# Apply the function to the 'Article_Text' column
data['Article_Text'] = data['Article_Text'].apply(html_to_text)

# Save the updated DataFrame back to a CSV file
data.to_csv('formatted_file.csv', index=False)
