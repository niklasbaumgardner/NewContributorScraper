# NewContributorScraper
Scrapes Bugzilla bug list to check if users are first time contributors

### Setup
You will need to have python installed on your machine to run this script. Python installations can be found [here](https://www.python.org/downloads/).

You will need to install the Firefox webdriver. Please follow the [Selenium documentation](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) to download and install the webdriver.

I recommend setting up a virtual enviroment to run this. Steps for setting up a virtual environment can be found [here](https://docs.python.org/3/library/venv.html).

Once the virtual enviroment is set up and activated, please install the requirements by running `pip install -r requirements.txt`

You will also need to add `BUGZILLA_USERNAME` and `BUGZILLA_PASSWORD` with your credentials to your environment variables. This script needs to login to Bugzilla to function properly. 

Now you can run the script with `python newContributorScraper.py`. When running the script, you will be prompted with a DUO notification to login. The script currently waits 15 seconds to accept the DUO notification, feel free to adjust the time to your liking. 

Once the script is completed, the output is written to a file named `New_Contributors.txt` where the first patch contributors are denoted with '#'
