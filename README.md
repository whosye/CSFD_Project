# CSFD Project

This project scrapes the list of top-rated films from [CSFD.cz](https://www.csfd.cz) and stores the data in a Django database. For each film, it extracts the names of actors from the detail page. The data is saved into two Django models (`Movie` and `Actor`) with a many-to-many relationship.

## Features

- Automated scraping of top films from CSFD
- Extraction of actor names from each movie detail page
- Data stored in Django models: `Movie` and `Actor`
- Asynchronous scraping using `ThreadPoolExecutor` for faster performance -- for show you can try run in sequential mode 
- Unit tests using `unittest.mock` and local fake HTML files run -> python manage.py test

## Getting Started

1. Clone the repository: git clone git@github.com:whosye/CSFD_Project.git
2. cd CSFD_Project
3. Create and activate a virtual environment: python3 -m venv venv && source venv/bin/activate (depends on OS)
4. Install dependencies: pip install -r requirements.txt
5. cd csfdProject
6. If no DB - Apply database migrations: python manage.py makemigrations && python manage.py migrate
7. If no DB - Run the scraper and populate the database: python manage.py csfd --pages 3 --seq True
8. Run server: python manage.py runserver





