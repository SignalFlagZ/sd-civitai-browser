import launch
import platform

if not launch.is_installed("colorama"):
    launch.run_pip("install colorama", "colorama: requirements for CivBrowser")
if not launch.is_installed("send2trash"):
    launch.run_pip("install Send2Trash", "Send2Trash: requirements for CivBrowser")
if not launch.is_installed("jinja2"):
    launch.run_pip("install jinja2", "jinja2: requirements for CivBrowser")
if not launch.is_installed("requests-cache"):
    launch.run_pip("install requests-cache", "requests-cache: requirements for CivBrowser")
system = platform.system()
if system == 'Windows':
    pass
elif  system == 'Linux':
    pass
elif system == 'Darwin':
    pass
else:
    pass