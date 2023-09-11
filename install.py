import launch
import platform

if not launch.is_installed("colorama"):
    launch.run_pip("install colorama", "requirements for sd-civitai-browser")

if platform.system() == 'Linux':
    if not launch.is_installed("tkinter"):
        launch.run_pip("install tkinter", "requirements for sd-civitai-browser")

if platform.system() == 'Darwin':
    if not launch.is_installed("tkinter"):
        # I don't know much
        # launch.run_pip("install tkinter", "requirements for sd-civitai-browser")
        pass
