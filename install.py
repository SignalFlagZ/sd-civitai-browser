import launch

if not launch.is_installed("colorama"):
    launch.run_pip("install colorama", "requirements for sd-civitai-browser")
    