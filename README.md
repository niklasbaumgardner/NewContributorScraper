# NewContributorScraper
Scrapes Bugzilla bug list to check if users are first time contributors

### Setup
You will need to have python installed on your machine to run this script. Python installations can be found [here](https://www.python.org/downloads/).

You will need to download the [latest geckodriver release](https://github.com/mozilla/geckodriver/releases) and list the geckodriver executable in your `PATH`. If there are issues running the driver, please follow the [Selenium documentation](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/) and ensure that you have the correct path listed.

I recommend setting up a virtual enviroment to run this. Steps for setting up a virtual environment can be found [here](https://docs.python.org/3/library/venv.html).

Once the virtual enviroment is set up and activated, please install the requirements by running `pip install -r requirements.txt`

You will also need to add `BUGZILLA_USERNAME` and `BUGZILLA_PASSWORD` with your credentials to your environment variables. This script needs to login to Bugzilla to function properly. 

### Running the script
Now you can run the script with `python newContributorScraper.py` and these supported commandline arguments:
- `url` (required): the resolved bugs url that we want to parse
- `--timer` (optional): the number of seconds that we want the script to wait for during the Duo authentication step
- `--help` (optional): displays descriptions for positional and optional arguments

When running the script, you will be prompted with a DUO notification to login. By default, the script waits 20 seconds to accept the DUO notification. Feel free to adjust the time to your liking with the `--timer` flag.

Here is an example:
```
python newContributorScraper.py "https://bugzilla.mozilla.org/buglist.cgi?title=Resolved%20bugs%20(excluding%20employees)&quicksearch=1640117%2C1953387%2C1957495%2C1835264%2C1960409%2C1824630%2C1960912%2C1920146%2C1954490%2C1960383%2C1958161%2C1939345%2C1323331%2C1953454%2C1961002%2C1895516%2C1955567&list_id=17551856" --timer=30
```

We pass in this [resolved bugs link](https://bugzilla.mozilla.org/buglist.cgi?title=Resolved%20bugs%20(excluding%20employees)&quicksearch=1640117%2C1953387%2C1957495%2C1835264%2C1960409%2C1824630%2C1960912%2C1920146%2C1954490%2C1960383%2C1958161%2C1939345%2C1323331%2C1953454%2C1961002%2C1895516%2C1955567&list_id=17551856) (note the use of double quotes `""`) and specify a Duo authentification wait time of 30 seconds.

### Output
Once the script is completed, the output is written to a file named `New_Contributors.txt` where the first patch contributors are denoted with '#'
