import launch
import platform

if not launch.is_installed("colorama"):
    launch.run_pip("install colorama", "requirements for sd-civitai-browser")

system = platform.system()
if system == 'Windows':
    pass
elif  system == 'Linux':
    if not launch.is_installed("tkinter"):
        launch.run_pip("install tkinter", "requirements for sd-civitai-browser")
elif system == 'Darwin':
    if not launch.is_installed("tkinter"):
        # I don't know much
        launch.run_pip("install tkinter", "requirements for sd-civitai-browser")
        pass
else:
    if not launch.is_installed("tkinter"):
        launch.run_pip("install tkinter", "requirements for sd-civitai-browser")
