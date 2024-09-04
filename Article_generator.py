pip install selenium
pip install webdriver-manager
pip install wordcloud
pip install streamlit
pip install langchain-google-genai
pip install google-generativeai
pip install langchain
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import time
import re

GOOGLE_GEMINI_KEY = "AIzaSyAMzDZ-wpZNfylJbgaehOpor7Jb1keI3ZA"
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_GEMINI_KEY)

titles = []
links = []
dates = []
authors = []
descriptions = []
images = []
generated_articles = []

def scrape_articles(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'faceted-search-results')))

    extract_articles(driver)
    pagenation(driver)    

    driver.quit()

    data = {
        'Title': titles,
        'Link': links,
        'Date': dates,
        'Author': authors,
        'Description': descriptions,
        'Image': images
    }

    df = pd.DataFrame(data)
    return df

def extract_articles(driver):
    articles = driver.find_elements(By.CLASS_NAME, 'border-top.py-4')
    for article in articles:
        title_element = article.find_element(By.CSS_SELECTOR, 'h3.card__heading a')
        titles.append(title_element.text.strip())

        links.append(title_element.get_attribute('href'))

        dates_elements = article.find_elements(By.CSS_SELECTOR, 'time.card__date ')
        date = [d.text for d in dates_elements]
        dates.append(', '.join(date))

        authors_elements = article.find_elements(By.CSS_SELECTOR, 'span.card__byline a')
        author_names = [author.text for author in authors_elements]
        authors.append(', '.join(author_names))

        description_element = article.find_element(By.CSS_SELECTOR, 'div.card-body > p:last-of-type')
        descriptions.append(description_element.text.strip())

        image_element = article.find_element(By.CSS_SELECTOR, 'div.card__thumbnail img')
        images.append(image_element.get_attribute('src'))

def pagenation(driver):
    # Loop through the pages
    while True:
        try:
            # Find the "Next" button and click it
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next page"]')
            next_button.click()

            # Wait for the next page to load
            time.sleep(5)

            # Extract articles from the next page
            extract_articles(driver)
        except:
            break

def poll_for_new_articles(murl, driver, existing_df):
    # Split the URL into base and suffix parts
    parts = murl.split('&pg=')
    baseurl = parts[0]
    suffix = parts[1].split('&', 1)[1]  # Correctly retrieve the suffix

    while True:
        try:
            # Iterate over page numbers
            for page_number in range(1, 4):
                url = f"{baseurl}&pg={page_number}&{suffix}"
                driver.get(url)
                
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'faceted-search-results')))

                # Clear previous page's data (optional depending on your use case)
                titles = []
                links = []
                dates = []
                authors = []
                descriptions = []

                # Extract articles (assuming extract_articles fills these lists)
                extract_articles()

                # Create a temporary DataFrame for the new data
                new_data = pd.DataFrame({
                    'Title': titles,
                    'Link': links,
                    'Date': dates,
                    'Author': authors,
                    'Description': descriptions
                })

                # Append the new data to the existing DataFrame
                existing_df = pd.concat([existing_df, new_data], ignore_index=True)

        except Exception as e:
            print(f"Polling error: {e}")
            break

        # Wait before polling again
        print("Polling complete. Waiting for next poll.")
        time.sleep(3600)  # Wait for an hour before polling again

    return existing_df  # Return the updated DataFrame


def generate_article(title, description):
    prompt = (
        f"You are an AI article writer. Generate a detailed article on the following title and abstract. "
        f"Title: {title}\n"
        f"Abstract: {description}\n"
        f"Include Introduction, different sections, different applications, tables, and conclusion:\n\n"
    )

    response_text = llm.predict(text=prompt)
    return response_text

def format_html_content(content, title, image_url):
    formatted_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
                color: #000; /* Set body text color to black */
            }}
            .article h1 {{
                color: #003366; /* Dark blue color for the main title */
                font-size: 2.5em;
                margin-bottom: 20px;
                text-align: center;
            }}
            .article h2, .article h3 {{
                color: #003; 
            }}
            .article {{
                max-width: 800px;
                margin: 0 auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                color: #000;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .section h2 {{
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
                color: #003; 
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            table, th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                color: #000; /* Set table text color to black */
            }}
            th {{
                background-color: #f4f4f4;
                color: #000; /* Set table header text color to black */
            }}
            img {{
                width: 100%;
                height: auto;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="article">
            <h1>{title}</h1>
            <img src="{image_url}" alt="Article Image">
            {content}
        </div>
    </body>
    </html>
    """
    return formatted_content


def convert_df_to_csv(df):
    csv = df.to_csv(index=False)
    return csv

# Streamlit setup
st.set_page_config(page_title="AI Research Article Generator", layout="wide")
st.title("AI Research Article Generator")

# Sidebar for navigation
st.sidebar.header("Navigation")
options = st.sidebar.radio("Go to", ["Home", "About"])

if options == "Home":
    st.sidebar.header("Options")
    time_period = st.sidebar.selectbox(
        "Select Time Period",
        ["Previous Week", "Previous Month", "Previous Year"]
    )

    url = {
        "Previous Week": 'https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/?facet%5Bdate%5D%5Bfixed%5D=week&facet%5Btax%5D%5Bmsr-content-type%5D=post&pg=1&sort_by=most-recent',
        "Previous Month": 'https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/?facet%5Bdate%5D%5Bfixed%5D=month&facet%5Btax%5D%5Bmsr-content-type%5D=post&pg=1&sort_by=most-recent',
        "Previous Year": 'https://www.microsoft.com/en-us/research/research-area/artificial-intelligence/?facet%5Bdate%5D%5Bfixed%5D=year&facet%5Btax%5D%5Bmsr-content-type%5D=post&pg=1&sort_by=most-recent'
    }[time_period]

    with st.spinner("Scraping Data.."):
        st.session_state.articles = scrape_articles(url)

    # Display articles and generate article content
    if 'generated_articles' not in st.session_state:
        st.session_state.generated_articles = []

    search_generated = st.text_input("Search generated articles", "")
    
    if search_generated:
        search_filtered = [ga for ga in st.session_state.generated_articles if search_generated.lower() in ga['title'].lower()]
    else:
        search_filtered = st.session_state.generated_articles

    if not st.session_state.articles.empty:
        for idx, article in st.session_state.articles.iterrows():
            st.subheader(f"{idx + 1}: {article['Title']}")
            st.write(f"**Author:** {article['Author']}")
            st.write(f"**Date:** {article['Date']}")
            st.write(f"**Link:** {article['Link']}")
            st.write(f"**Description:** {article['Description']}")
            st.image(article['Image'], width=300)

            if st.button(f"Generate Article for '{article['Title']}'", key=f"generate_{idx}"):
                with st.spinner(f"Generating article for '{article['Title']}'..."):
                    generated_article = generate_article(
                    title=article['Title'],
                    description=article['Description'],
                    )         
        
                    formatted_article = format_html_content(generated_article, article['Title'], article['Image'])
                    st.markdown(formatted_article, unsafe_allow_html=True)
        
                    # Store the generated article
                    st.session_state.generated_articles.append({
                    'title': article['Title'],
                    'content': generated_article
                    })

                    
                    # Store the generated article
                    st.session_state.generated_articles.append({
                        'title': article['Title'],
                        'content': generated_article
                    })

    # Display generated articles
    if search_generated:
        st.subheader("Search Results")
        for idx, gen_article in enumerate(search_filtered):
            st.write(f"**Title:** {gen_article['title']}")
            st.write(f"**Generated Content:**")
            st.markdown(format_html_content(gen_article['content']), unsafe_allow_html=True)
            st.write("---")
            
elif options == "About":
    st.header("About This App")
    st.write("This app uses AI to generate detailed articles based on recent research.")


