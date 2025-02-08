# real_estate_lead_gen

## Description
This is a program I built for a local real estate business. They focus on mobile home real estate, identifying people who own their mobile home, but have fallen behind in lot fees and are involved in court cases with the mobile home park they reside in. The business reaches out to these individuals and offers to pay what they owe to the park, purchase their mobile home on top of that, remodel the home and then sell it.

The program searches county court cases, generating URLs based on a list of mobile home parks in the county. It then pulls case numbers and generates the URLs for the specific cases. From there it pulls desired data from each case, compiles it into a dataframe, and sends it to a google sheet for the client.

# Table of Contents
- [Technologies Used](#technologies-used)
- [Installation](#setup-and-installation)
- [Features](#features)
- [Contact](#contact)

## Technologies Used
- Python
- BeautifulSoup
- Pandas
- gspread

## Setup and Installation
Ensure you have Python 3.8+ installed.
Install all dependencies:

pip install -r requirements.txt

## Clone the Repository
First, clone the repository to your local machine using the following command:
```bash```
git clone https://github.com/aolson659/real_estate_lead_gen.git
cd real_estate_lead_gen


The program does require google cloud API setup, you will need a json configuration file for it to run. However if you want to test out the data parsing, there is a URL present in parse_data that will provide an example of how the functions work.

### Features
The purpose of this project was to provide an easy way for a local business to generate new leads. It finds ideal customers for the business and provides all the data necessary for the business to make an offer. It has proven to be hugely beneficial ot the business, saving them time and allowing for them to increase their revenue. Since having access to the program, they have reported more than a XXX% increase in their revenue stream. The program was integrated onto their XXX server and can be easily run, providing new leads whenever they need them.


### Contact
For collaboration, troubleshooting, and potential job offers, you can reach me at aolsondm@gmail.com


