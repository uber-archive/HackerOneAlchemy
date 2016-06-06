# HackerOne Alchemy
A tool for making bug bounty life easier!

# Example Usage
```
(env)mjb-C1MQ533FG944:HackerOneAlchemy mandatory$ source env/bin/activate; python hackerone_alchemy.py --metrics --load-reports all_reports.reports

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
New reports: 21
Triaged reports: 88
Needs More Info reports: 145
Resolved reports: 227
Not Applicable reports: 221
Informative reports: 870
Duplicate reports: 365
Spam reports: 15
Signal to Noise ratio: 0.284810126582
Number of Wordpress reports: 289
Total reports: 1952
Total bounty amount awarded: $330,470.48
Closing reports as 'Spam': Priceless
```

# Setup
First, clone that sweet repo:

```
git clone gitolite@code.uber.internal:engsec/hackeronealchemy
```

Slide into that [DM`[DEL][DEL]`]() directory:

```
cd hackeronealchemy
```

Now set up your `virtualenv` and `source` it:

```
virtualenv env
source env/bin/activate
```

Boom, now let's install the requirements:

```
pip install -r requirements.txt
```

Now you'll need to edit the `config.yaml` with API credentials. You can get a set of API credentials from the following URL: [https://hackerone.com/uber/api](https://hackerone.com/uber/api):

```
vim config.yaml
```

Now that you've setup your `config.yaml` you are good to go! Test it's working with the following command:

```
./hackerone_alchemy.py --metrics
```

# Features
## Save reports for to disk for future quickloading
In order to save time, you can save reports to a JSON cache file via the `--save-reports` flag. The following is an example:

```
./hackerone_alchemy.py --save-reports all_reports.json
```

This is useful if you want to quickly re-analyze data using HackerOne Alchemy:

```
./hackerone_alchemy.py --load-reports all_reports.json --metrics
```

This feature is also useful because you can save reports in a specific date range and then do analysis on that subset of data:

```
./hackerone_alchemy.py --save-reports since_launch.json --since-date "March 22, 2016" # Save all reports since our bug bounty public launch to file
./hackerone_alchemy.py --load-reports since_launch.json --metrics # Get metrics for submissions since launch
```

## Get HackerOne Metrics
If you're writing a bug bounty status update post, or if you want to see the general health of the program you can use `--metrics` to get that data. For example, the following will get metrics on our bug bounty program since the beginning:

```
./hackerone_alchemy.py --metrics
```

In certain situations you may want metrics from a certain date. As mentioned above this is possible with the `--save-reports` and `--since-date` flag. For example, the following will grab bug bounty metrics since our launch date of March 22, 2016:

```
./hackerone_alchemy.py --save-reports since_launch.json --since-date "March 22, 2016" # Save all reports since our bug bounty public launch to file
./hackerone_alchemy.py --load-reports since_launch.json --metrics # Get metrics for submissions since launch
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
