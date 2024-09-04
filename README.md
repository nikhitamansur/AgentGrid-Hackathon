# AgentGrid-Hackathon
This project is a web application built using Streamlit that scrapes research articles from a specified website and uses AI to generate detailed articles based on the scraped data. It integrates various Python libraries like Selenium for web scraping, Pandas for data handling, and LangChain with Google's Gemini model for AI-powered article generation.

Table of Contents
Features
Installation
Usage
Code Explanation
Contributing
License
Features
Web Scraping: Automatically scrape the latest research articles from a specified source.
AI-Powered Content Generation: Generate detailed research articles using AI based on the scraped data.
Interactive Interface: User-friendly interface built with Streamlit, allowing users to browse, generate, and search articles.
CSV Export: Export scraped articles into a CSV file for further analysis.

1. Python Libraries Installation
The first lines of the code install necessary Python libraries like Selenium for web scraping, Streamlit for the web interface, Pandas for data handling, and LangChain for AI-based article generation.
2. Streamlit Web Application Setup
Streamlit is used to create a simple and interactive web application. The app's interface includes navigation, options to select a time period, and functionality to scrape, display, and generate articles.
3. Web Scraping with Selenium
The code uses Selenium to automate the process of extracting articles from a research website. It opens a browser in headless mode (no visible window) and scrapes article details like titles, links, dates, authors, descriptions, and images.
Pagination Handling: The code can also handle multiple pages by clicking the "Next" button and scraping articles from each page until no more pages are left.
4. AI-Powered Article Generation
The LangChain library is integrated with Google's Gemini model to generate detailed articles based on the scraped data. The AI model takes a title and description as input and produces a full article, including sections, applications, and conclusions.
5. Article Display and Management
The app displays the scraped articles on the home page, allowing users to browse through them.
Users can generate AI-written articles by clicking a button next to each article. The generated articles are stored in the session state and can be searched and reviewed later.
Articles are displayed in a well-formatted HTML structure, with appropriate styling for readability.
6. CSV Export
The scraped articles can be converted into a CSV file using Pandas, allowing easy export and further analysis.
7. Streamlit Interface
Sidebar Navigation: Allows users to switch between the "Home" page (for scraping and generating articles) and the "About" page (providing information about the app).
Search Functionality: Users can search for generated articles by title.
