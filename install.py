import launch
import platform

if not launch.is_installed("colorama"):
    launch.run_pip("install colorama", "requirements for sd-civitai-browser")
if not launch.is_installed("send2trash"):
    launch.run_pip("install Send2Trash", "requirements for sd-civitai-browser")
system = platform.system()
if system == 'Windows':
    pass
elif  system == 'Linux':
    pass
elif system == 'Darwin':
    pass
else:
    pass