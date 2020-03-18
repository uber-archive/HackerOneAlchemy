# HackerOne Alchemy

(This project is deprecated and not maintained.)

A tool for making bug bounty life easier! This tool generates statistics around reports and also makes it easier to identify reports that need more attention.

# Example Usage
```
(env)~ source env/bin/activate; python hackerone_alchemy.py --metrics

 ██░ ██  ▄▄▄       ▄████▄   ██ ▄█▀▓█████  ██▀███   ▒█████   ███▄    █ ▓█████ 
▓██░ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒ ██ ▀█   █ ▓█   ▀ 
▒██▀▀██░▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒▒██░  ██▒▓██  ▀█ ██▒▒███   
░▓█ ░██ ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░▓██▒  ▐▌██▒▒▓█  ▄ 
░▓█▒░██▓ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒░ ████▓▒░▒██░   ▓██░░▒████▒
 ▒ ░░▒░▒ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ░░ ▒░ ░
 ▒ ░▒░ ░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ░ ░  ░
 ░  ░░ ░  ░   ▒   ░        ░ ░░ ░    ░     ░░   ░ ░ ░ ░ ▒     ░   ░ ░    ░   
 ░  ░  ░      ░  ░░ ░      ░  ░      ░  ░   ░         ░ ░           ░    ░  ░
                  ░                                                          
 ▄▄▄       ██▓     ▄████▄   ██░ ██ ▓█████  ███▄ ▄███▓▓██   ██▓               
▒████▄    ▓██▒    ▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▓██▒▀█▀ ██▒ ▒██  ██▒               
▒██  ▀█▄  ▒██░    ▒▓█    ▄ ▒██▀▀██░▒███   ▓██    ▓██░  ▒██ ██░               
░██▄▄▄▄██ ▒██░    ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒██    ▒██   ░ ▐██▓░               
 ▓█   ▓██▒░██████▒▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒██▒   ░██▒  ░ ██▒▓░               
 ▒▒   ▓▒█░░ ▒░▓  ░░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ▒░   ░  ░   ██▒▒▒                
  ▒   ▒▒ ░░ ░ ▒  ░  ░  ▒    ▒ ░▒░ ░ ░ ░  ░░  ░      ░ ▓██ ░▒░                
  ░   ▒     ░ ░   ░         ░  ░░ ░   ░   ░      ░    ▒ ▒ ░░                 
      ░  ░    ░  ░░ ░       ░  ░  ░   ░  ░       ░    ░ ░                    
                  ░                                   ░ ░                    
                    "so 1337"
                                                "check out dat ascii art"
    "actually, it's not ascii, it's unicode"
                                                        "k"


TOTAL REPORT STATS
==================
Total reports: 397
Total Resolved: 15
Total Spam: 0
Total Triaged: 28
Total Informative: 153
Total Duplicate: 78
Total Not-Applicable: 45
Total New: 41
Total Needs-More-Info: 37
Mean resolution time: 10 days, 11:08:38.315467
Mean first response time: 1 day, 13:38:19.589763
Signal to Noise ratio: 0.217171717172
Number of flagged reports: 0
Total bounty amount awarded: $87,375.00
Closing reports as 'Spam': Priceless
```

# Setup
First, clone that sweet repo:

```
git clone "https://github.com/uber/HackerOneAlchemy.git"
```

Slide into that directory:

```
cd HackerOneAlchemy
```

Now set up your `virtualenv` and `source` it:

```
virtualenv env
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

You'll need to edit the `config.yaml` with API credentials. You can get a set of API credentials from your HackerOne portal, something like https://hackerone.com/{PROGRAM_NAME}/api. You'll also want to set `hackerone_program` to your program's handle.

Now that you've setup your `config.yaml` you are good to go! Test it's working with the following command:

```
./hackerone_alchemy.py --metrics
```

Note: For the Phabricator integrations, you will need an ~/.arcrc file already setup for authentication.

# Features

## Get HackerOne Metrics
If you're writing a bug bounty status update post, or if you want to see the general health of the program you can use `--metrics` to get that data. For example, the following will get metrics on our bug bounty program since the beginning:

```
./hackerone_alchemy.py --metrics
```

In certain situations you may want metrics from a certain date. This is possible with the `--since-date` flag. For example, the following will grab bug bounty metrics since our launch date of March 22, 2016:

```
./hackerone_alchemy.py --metrics --since-date "March 22, 2016" # Get metrics for submissions since launch
```

## Get HackerOne Bonus List
One of the fun features we have is [a bonus system](https://newsroom.uber.com/bug-bounty-program/). HackerOne Alchemy has a feature which allows you to figure out who is eligible for bonuses.

To get this information use HackerOne Alchemy with the flags `--bonuses` and `--since-date`. The following is an example where the bonus season started on `May 1st, 2016`:

```
./hackerone_alchemy.py --bonuses --since-date "May 1, 2016"
```

This will print out a list of users and the reports which have made them eligible. Keep in mind the reports have to be in a `Resolved` state (and there must be >=5 of them) before the bot will print them as eligible.

## Get Oncall Work
If you're the current bug bounty oncall, you can use `--oncall` to get a list of reports that you should take a look at. This does a few checks such as checking if a report is `Triaged` in HackerOne but `Resolved` in Phabricator and vise versa:

```
./hackerone_alchemy.py --oncall
```

This project is released under the [MIT License](LICENSE.md).
