import subprocess
from typing import Tuple


class XRandr:
    @staticmethod
    def get_resolution() -> Tuple[int, int]:
        cmd = ['xrandr']
        cmd2 = ['grep', '*']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
        p.stdout.close()

        resolution_string, junk = p2.communicate()
        resolution = resolution_string.split()[0].decode('utf-8')
        w_str, h_str = resolution.split('x')
        return int(w_str), int(h_str)
