VERSION = "v2.3.5"

platform = "A1111"
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
