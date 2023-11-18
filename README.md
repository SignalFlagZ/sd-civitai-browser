# sd-civitai-browser (CivBrowser)
An extension to help download models from CivitAi without leaving WebUI

# Modifications

https://github.com/SignalFlagZ/sd-civitai-browser/assets/23202768/56f34586-94ea-40a9-b826-30ff20bf7bb3

## Features
- Search Civitai models in ***multiple tabs***
- List models as ***card image***
- Safe display in ***sfw*** search
- Highlight models ***you have***
- Display/***save*** model information ***in HTML***
- ***Json data*** of model is also ***saved*** in the same folder as the model file
- If the sample image has meta data, display it with ***infotext compatibility***
- Click on the image to ***send to txt2img***
- Check downloaded model file with ***SHA256***
- ***Automatically*** set save folder, or specify it directly
- Card ***size and colors*** can be changed in Settings
- Support ***API Key***

## Versions
### v1.8
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
