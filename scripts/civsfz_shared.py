VERSION = "v2.3.6"

platform = "A1111"
forge_version = None
try:
    from modules_forge import forge_version
except ImportError:
    from modules.cmd_args import parser
    if parser.description:
        platform = "SD.Next"
    pass
else:
    platform = "Forge"
    forge_version = forge_version
# print(f'Working on {platform}')

try:
    # SD web UI >= v1.6.0-RC
    from modules.shared_cmd_options import cmd_opts as cmd_opts
except ImportError:
    # SD web UI < v1.6.0-RC
    # SD.Next
    from modules.shared import cmd_opts as cmd_opts
from modules.shared import opts as opts

if platform == "Forge":
    from modules.hashes import calculate_sha256_real as calculate_sha256
else:
    from modules.hashes import calculate_sha256 as calculate_sha256
