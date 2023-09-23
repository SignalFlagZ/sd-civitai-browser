# sd-civitai-browser
An extension to help download models from CivitAi without leaving WebUI

# Modifications

https://github.com/SignalFlagZ/sd-civitai-browser/assets/23202768/56f34586-94ea-40a9-b826-30ff20bf7bb3

## Versions
### v1.7
- Model card size can be set in Settings
- Model card zooming size can be set in Settings
- Some colors of card can now be set in Settings
  - When you press the Get List button, the settings will be loaded and will be reflected when you display a new cards
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
