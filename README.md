# sd-civitai-browser (CivBrowser)
An extension to help download models from CivitAi without leaving WebUI

# Modifications

https://github.com/SignalFlagZ/sd-civitai-browser/assets/23202768/56f34586-94ea-40a9-b826-30ff20bf7bb3

***If you fork, please replace prefix `civsfz` in file names, function names, css class names, etc. with your own prefix to avoid conflicts.***
## Features
- Search Civitai models in ***multiple tabs***
- List models as ***card image***
- Safe display in ***sfw*** search
- Highlight models ***you have***
- Highlight models that ***can be updated*** 
- Searchable by specifying ***Base Models*** (experimental)
- Show ***Base Model*** on a model card
- Display/***save*** model information ***in HTML***
- ***Json data*** of model is also ***saved*** in the same folder as the model file
- If the sample image has meta data, display it with ***infotext compatibility***
- Click on the image to ***send to txt2img***
- Check downloaded model file with ***SHA256***
- ***Automatically*** set save folder, or specify it directly
- Card ***size and colors*** can be changed in Settings
- Support ***API Key***
- Show the ***Early Access*** period of models

## Versions
### v1.14
- Fix to use model-versions API to get meta data
- Add color frames to cards that can be updated
- Use jinja template engine
### v1.13
- Fix an issue where API responses changed and permissions could not be displayed correctly. #33
- Fix an issue where the version could not be selected correctly with multiple versions with the same name.
- Change info file format
- Change info file extension to json
- Change design of model information
### v1.12
- Check the match between image and infotext using image ID
- The meta key was missing from the API response, so retrieve it from the images API (Experimental)
  - Hide the infotext because it was displaying infotext different from the image (v1.12.1)
### v1.11
- Add search by model ID
- Change the default setting so that `/` is not treated as a folder separator.
- Get search choices from Civitai after launch and keep them up to date
### v1.10
- Cut file name length to 254 characters
- Show Early Access on card
  - The background color changes during and outside the period
- Show elapsed days on Early Access models
- Add model creation date/time, publication date/time, update date/time in HTML
- Add save folder setting \([How to set it up](https://github.com/SignalFlagZ/sd-webui-civbrowser/wiki#how-to-set-save-folders-by-type-v1100-and-above)\)
  - Specify path for each model type in JSON string
### v1.9
- Search for multiple model types at the same time
- Show model type on a card
- Changed model card design to display base model
  - Since there were many changes to Settings, it is recommended to delete prefix `civsfz` lines in config.json.
- Add filter for Base Models (experimental)
- ~~Show base model with background color of model name~~
- ~~Display base model in top frame color~~
  - Color can be changed in Settings
- Add an checkbox to the settings to specify whether to treat "/" as a folder separator (default:`True` for backward compatibility)
  - If you change it, some models may not be able to confirm the existence of the file.
- ~~Disable download button for Early Access models~~
  - Early access supporters may be able to download the model. Not tested.
- Rename files to avoid conflicts with other extensions
  - Why do python file conflicts occur? For example, api.py is used by many people and no problems occur.
- Add prefix `civsfz` to javascript function names to make them unique
- If you fork, please replace `civsfz` in file names, function names, css class names, etc. with your own prefix to avoid conflicts.
### v1.8
- Add sort types
- The model download timeout was set to 4 seconds because it was forcibly disconnected after about 5 seconds
- Support API Key
  - Some models require your API key when downloading
  - Models that fail to download may require an API key, but are indistinguishable from those that truly fail
  - API key is not saved for security reasons
  - Apply the API key using the command line option `--civsfz-api-key` or type directly into the text box
  - If there is no Content-Length in the request response, an API Key may be required. 
### v1.7
- Add open folder button
- Make tab bar sticky
- Add content types `Upscaler`,`MotionModule`,`Wildcards`,`Workflows`,`Other` (experimental)
  - Save the newly added contenttype files to the `OtherModels` folder. Where should we save the files?
  - Unable to reach stability matrix models folder
- Change default period to `Month`
- Make navigation buttons sticky
- Show save buttons and back-to-top button sticky
- Add back-to-top button
- Rename elements class/id
- Change to unique name 
- If the first image is of type `X`, treat the model as nsfw
  - Note that the save folder will change
- Move the file that failed to download to the trash
- Check the hash value of the downloaded file
- Model card size can be set in Settings
- Model card zooming size can be set in Settings
- Some colors of card can now be set in Settings
  - Settings will take effect on the next cards rendering
  - To return to default, search for `civsfz` from config.json and delete that line
- Stop using tkinter. It was causing a crash
### v1.7 beta3
- Fix a mistake when there are models with the same name
- Change model html styles
### v1.7 beta2
- The number of tabs can be changed in Settings
- The number of cards per page can now be changed
- Add Civitai Browser to Settings
- If there is no tkinter module, continue with limited functionality (experimental)
- Clicking on the image sends infotext to txt2img. If local, copy to clipboard
- Separately searchable in multiple tabs
### v1.7 beta
- Two tabs for separate searches (experimental)
  - Probably cannot download at the same time
### v1.6
- Support video type images (Temporarily because the video format is unknown)
- Display image meta data in Infotext-compatible format (can be expanded by pasting into a prompt)
- Click image to copy infotext
### v1.5
- Show download progress
- Add download cancel button
- Show Civitai response error
- File exists, overwrite and continue can be selected.
### v1.4
- Add page slider and jump button
- Rename tab `CivitAi` to `CivitAi Browser`
### v1.3
- Changed to index based model selection
- Add save folder textbox
- Add dropdown list of search period
- Highlighted if you already have the file
### v1.2.0
- NSFW models are saved in `.nsfw`
- Show permmisions in HTML -> [reference](https://github.com/civitai/civitai/blob/main/src/components/PermissionIndicator/PermissionIndicator.tsx#L15)
- Avoid collision when there are same model names
- Deprecate new folder checkbox and its function
- Change version selection from dropdown to radio button
### v1.1.0 and before
- Apply changes made by [thetrebor](https://github.com/thetrebor/sd-civitai-browser)
- Support LoRA
- Set folders from cmd_opts
- Save HTML with images
- Add Trained Tags in html
- Add meta data in html
- Copy first image as thumbnail
- Add thumbnail preview list
- Save model data as ".civitai.info"
- Support LoCon/LyCORIS
- Press the Download Model button again to cancel the download
- Add previous button
- Click on a thumbnail to select a model
- Add zoom effect to thumbnails
- Support ControlNet/Poses
- Support user and tag name search
- Implement page controls
- Support for `--lyco-dir`(To use the existing _LoCon folder, specify with `--lyco-dir`)
- Change the color of the frame of the card that has already been downloaded
- For base models other than SD1, save to a subfolder of the base model name
- Support `--lyco-dir-backcompat` modified in v1.5.1 of SD web UI
- Save to subfolder of base model name (e.g. `_SDXL_1_0` , `_Other`)
