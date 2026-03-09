# ComfyUI-NS-PromptList
[日本語README](https://github.com/NakamuraShippo/ComfyUI-NS-PromptList/blob/main/README_jp.md)

This repository is no longer being updated and has been merged into [ComfyUI-NS-Util](https://github.com/NakamuraShippo/ComfyUI-NS-Util).  

<br>

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

<br>

ComfyUI-NS-PromptList is a simple prompt management node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that outputs prompts recorded in .yaml.

## Features

- Load prompts from prompts.yaml and output positive and negative prompts in String format
- Write new prompts to yaml
- Edit prompts registered in yaml

## Installation
If you have [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) installed:
1. Click Manager -> Install via Git URL from the main menu
2. Paste the URL in the text box that appears at the top of the window and press OK  
   https://github.com/NakamuraShippo/ComfyUI-NS-PromptList
3. Once the installation is complete, restart ComfyUI

If you don't have [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) installed:
1. Navigate to ComfyUI's custom nodes directory (usually ComfyUI/custom_nodes/)
2. Clone this repository:  
`git clone https://github.com/NakamuraShippo/ComfyUI-NS-PromptList`
3. Restart ComfyUI
4. In ComfyUI\venv\Scripts, Shift+Right-click → Open in terminal -> type "activate"
```
pip install pyyaml watchdog filelock
```

## Usage
Node location:
Add Node -> NS -> NS Prompt List

Node widgets:
- select_yaml: List of yaml files in ComfyUI-Create\custom_nodes\ComfyUI-NS-PromptList\yaml, loads the selected yaml
- select: Select from a list of title keys in the yaml selected by select_yaml to load the title and string
- title and text area: Content of the loaded title and string information

How to register prompts:
1. Enter an identifying title in the title field
2. Enter any string in the text area
3. Generate to write to yaml

How to edit prompts:
1. Enter the name of the prompt you want to edit in the title field
2. Enter any string in the text area
3. Generate
4. If the same title name exists in the specified yaml, the string will be overwritten

If you accidentally edit:
Press CTRL + Z to redo and restore the string, then generate again to overwrite

## Update History
2025/05/31 2.0.0 It has been completely redesigned and is now all on ComfyUI.
2024/09/06 1.2.0 Modified node input field to multiline. Published editing spreadsheet.
2024/08/24 1.0.0 Initial release as it's working properly

## License
This project is released under the MIT License. For details, see the [LICENSE.txt](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/License.txt) file.
You are free to use, modify, and distribute this software for personal and commercial purposes as long as you include the original copyright notice and disclaimer.

## Other
Bug reports and feature requests are welcome through any means of contact.
Pull requests are also welcome.

## Contact
[NakamuraShippo](https://lit.link/admin/creator)
