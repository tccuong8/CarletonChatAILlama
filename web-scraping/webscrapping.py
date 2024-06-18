import requests
from bs4 import BeautifulSoup
import csv


# URL of the homepage of Knowledge Base
url = "https://stolafcarleton.teamdynamix.com/TDClient/2092/Carleton/KB/"  

# Send an HTTP GET request to the website
response = requests.get(url)

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, "html.parser")

# Extract data from the page
categories = []

for category_div in soup.find_all("div", class_="media media-doubled border category-box category-box-collapsed"):
    category_name = category_div.find("h3", class_="category-title").find("a").text
    category_link = "https://stolafcarleton.teamdynamix.com" + category_div.find("h3", class_="category-title").find("a")["href"]
    
    categories.append({
        "Category_Name": category_name,
        "Link": category_link
    })

# Save main category data to a CSV file
with open("main_categories.csv", "w", newline="") as csvfile:
    fieldnames = ["Category_Name", "Link"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for category in categories:
        writer.writerow(category)

###################################################################################################################

#Code to load the sub-categories that are not part of the main categories

sub_categories = []
# Extract data from the page
for category in categories:
    category_response = requests.get(category["Link"])
    # Parse the HTML content of the page
    category_soup = BeautifulSoup(category_response.text, "html.parser")


    for category_div in category_soup.find_all("div", class_="media media-doubled border category-box category-box-collapsed"):
        sub_category_name = category_div.find("h3", class_="category-title").find("a").text
        sub_category_link = "https://stolafcarleton.teamdynamix.com" + category_div.find("h3", class_="category-title").find("a")["href"]
        
        sub_categories.append({
            "Sub_Category_Name": sub_category_name,
            "Link": sub_category_link,
            "Main_Category": category["Category_Name"]  # Add the main category name
        })

#Extract data from sub-categories pages a layer deeper
for sub_category in sub_categories:
    sub_category_response = requests.get(sub_category["Link"])
    # Parse the HTML content of the page
    sub_category_soup = BeautifulSoup(sub_category_response.text, "html.parser")


    for sub_category_div in sub_category_soup.find_all("div", class_="media media-doubled border category-box category-box-collapsed"):
        sub_category_name = sub_category_div.find("h3", class_="category-title").find("a").text
        sub_category_link = "https://stolafcarleton.teamdynamix.com" + sub_category_div.find("h3", class_="category-title").find("a")["href"]
        
        sub_categories.append({
            "Sub_Category_Name": sub_category_name,
            "Link": sub_category_link,
            "Main_Category": sub_category["Sub_Category_Name"]  # Add the main category name
        })

# Save sub-category data to a CSV file
with open("sub_categories.csv", "w", newline="") as csvfile:
    fieldnames = ["Sub_Category_Name", "Link", "Main_Category"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for sub_category in sub_categories:
        writer.writerow(sub_category)

# #########################################################################################################################################################

#Code to load the article names and links 

articles = []

for category in categories:
    article_response = requests.get(category["Link"])
    # Parse the HTML content of the page
    article_soup = BeautifulSoup(article_response.text, "html.parser")


    for article_div in article_soup.find_all("div", class_="gutter-bottom-lg"):
        article_name = article_div.find("h3", class_="gutter-bottom-xs").find("a").text.strip()
        article_link = "https://stolafcarleton.teamdynamix.com" + article_div.find("h3", class_="gutter-bottom-xs").find("a")["href"]
        
        articles.append({
            "Article_Name": article_name,
            "Link": article_link,
            "Category_Under": category["Category_Name"]
        })

for sub_category in sub_categories:
    article_response = requests.get(sub_category["Link"])
    # Parse the HTML content of the page
    article_soup = BeautifulSoup(article_response.text, "html.parser")


    for article_div in article_soup.find_all("div", class_="gutter-bottom-lg"):
        article_name = article_div.find("h3", class_="gutter-bottom-xs").find("a").text.strip()
        article_link = "https://stolafcarleton.teamdynamix.com" + article_div.find("h3", class_="gutter-bottom-xs").find("a")["href"]
        
        articles.append({
            "Article_Name": article_name,
            "Link": article_link,
            "Category_Under": sub_category["Sub_Category_Name"]
        })


# Save article data to a CSV file
with open("articles.csv", "w", newline="") as csvfile:
    fieldnames = ["Article_Name", "Link", "Category_Under"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for article in articles:
        writer.writerow(article)
############################################################################################################################################################

#Code to load the article text to a csv. 
'''Code needs to be updated to make sure it is grabbing the right content as some article pages may differ'''


article_text = []

for article in articles:
    # Send an HTTP GET request to the article page
    response1 = requests.get(article["Link"])

    # Parse the HTML content of the page
    soup1 = BeautifulSoup(response1.text, "html.parser")

    # Extract the article text and links
    article_div = soup1.find("div", {"id": "ctl00_ctl00_cpContent_cpContent_divBody"})

    # Extract the article content, including HTML tags
    article_content = str(article_div)
    h1_element = soup1.find("h1")
    article_name1 = h1_element.get_text().strip()

    article_text.append({
        "Article_Name": article_name1,
        "Article_Link": article["Link"],
        "Article_Text": article_content
        })

    # Save the article content to a CSV file
    with open("article_text.csv", "w", newline="") as csvfile:
        fieldnames = ["Article_Name", "Article_Link", "Article_Text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for article1 in article_text:
            writer.writerow(article1)


###########################################################################################################################################################

#Code to get the popular tags and their links to the popular articles



url2 = "https://stolafcarleton.teamdynamix.com/TDClient/2092/Carleton/Shared/BrowseTags?ItemID=0&ComponentID=26"  

# Send an HTTP GET request to the website
response2 = requests.get(url2)

# Parse the HTML content of the page
soup2 = BeautifulSoup(response2.text, "html.parser")

# Extract data from the page
tags = []

for tag_div in soup2.find_all("div", class_="col-md-3 col-sm-4 gutter-top"):
    tag_name = tag_div.find("a", class_="font-md").get_text()
    tag_link = "https://stolafcarleton.teamdynamix.com" + tag_div.find("a", class_="font-md").get("href")
    
    tags.append({
        "Tag_Name": tag_name,
        "Link": tag_link
    })

# Save main category data to a CSV file
with open("popular_tags.csv", "w", newline="") as csvfile:
    fieldnames = ["Tag_Name", "Link"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for tag in tags:
        writer.writerow(tag)


# if __name__=="__main__": 
#     main() 