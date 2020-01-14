# BruteMeTheHorizon
 Password spraying for VMWare Horizon
## Usage
```
# python -m brutemethehorizon -h
usage: __main__.py [-h] -u URL [--username USERNAME] [--userfile USERFILE] [--password PASSWORD]
                   [--passfile PASSFILE] [--domain DOMAIN] [-l LOCK_TIME] [-c COUNT] [--proxy PROXY]
                   [--output-prefix OUTPUT_PREFIX] [--debug] [--output-dir OUTPUT_DIR]
VMWare Horizon Password Sprayer

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Horizon URL
  --username USERNAME   Username
  --userfile USERFILE   List of Usernames
  --password PASSWORD   Password
  --passfile PASSFILE   List of Passwords
  --domain DOMAIN       Specify NetBIOS domain name
  -l LOCK_TIME, --lock_time LOCK_TIME
                        Time in minutes between sprays. Default: 15 minutes
  -c COUNT, --count COUNT
                        Password per spray. Default: 1
  --proxy PROXY         HTTP(S) Proxy. Format: [http(s)://ip:port]
  --output-prefix OUTPUT_PREFIX
                        Output prefix ({prefix}_result.txt Default: horizon
  --debug               Debug output
  --output-dir OUTPUT_DIR
                        Output directory. Default: ./
```
## Requirements
* requests
