Fineco Bank trading utils script
-------------------

The following python script allows you to easily obtain analysts position about trading index titles in Fineco Bank.

You can create a cronjob and configure SMTP for sending email with results or you can read collected results in `risultati.json` .

Requirements
------------

- Python3
- BeautifulSoup 4
- SmtpLib python library

Configuration
-------------

You can setup a configuration with your login credentials in order to remember next times.
You should create a conf.json following conf.json.example:

```	
{
  "username": "your fineco username",
  "password": "your fineco password",
  "smtp": {
    "host": "",
    "port": 587,
    "email": "",
    "password": "",
    "recipient": ""
  },
  "valid_results": [
    "Strong BUY",
    "Strong SELL"
  ]
}
```

Usage
------

```	
$ python3 __init__.py 
```

You can decide to scrape all index titles or not adding one boolean argument (default is 0)

```	
$ python3 __init__.py 1
```

It could be useful, if you'll use this script with a cronjob.

Cronjob example using Linux Crontab
------

```
* * * * 1 python3 /script_path/fineco-analysis-utils-script/__init__.py 1 >/dev/null 2>&1
* * * * 0,2-6 python3 /script_path/fineco-analysis-utils-script/__init__.py >/dev/null 2>&1
```

In this example on monday the script before executing normal operations will scrape all index titles.

Credits
--------

- Me, of course :)

License
--------
_*Fineco Bank trading utils script*_ is licensed under : The Apache Software License, Version 2.0. You can find a copy of the license (http://www.apache.org/licenses/LICENSE-2.0.txt)

Enjoy ;)