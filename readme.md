# MarketCompetitionAnalyzer
## Installation

```
$ git clone http://10.42.1.93/Hiram/MarketCompetitionAnalyzer.git
$ cd MarketCompetitionAnalyzer
$ pipenv install --dev
$ pipenv shell
"
Remember to write needing env variables 
in a file named '.flaskenv' in the root directory
For example:
FLASK_APP=app
FLASK_ENV=development
MAIL_DEFAULT_SENDER=your email sender
MAIL_SERVER=your email server
MAIL_USERNAME=your email account
MAIL_PASSWORD=your email pwd
DATABASE_URI=your db link #only mysql support
"
$ flask init
$ flask run
* Running on http://127.0.0.1:5000/
```