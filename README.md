# ComfyUI-NS-PromptList
ComfyUI-PromptList is a simple prompt management node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that outputs prompts recorded in prompts.yaml.  
[日本語はこちら](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/README_jp.md)
## Features

- Loads prompts from prompts.yaml and outputs positive and negative prompts in String format.
- Writes new prompts to the yaml file.
- Modifies existing prompts registered in the yaml file.

## Installation
If you have [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) installed:
1. Click Manager -> Install via Git URL in the main menu.
2. Paste the URL into the text box that appears at the top of the window and press OK:  
   https://github.com/NakamuraShippo/ComfyUI-PromptList
3. After installation is complete, restart ComfyUI.

If you don't have [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) installed:
1. Navigate to the ComfyUI custom node directory. (Usually ComfyUI/custom_nodes/)
2. Clone this repository:  
`git clone https://github.com/NakamuraShippo/ComfyUI-PromptList`
3. Restart ComfyUI.

## Usage
![node](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/images/node1.png)  
Right-click on the workspace -> Add node -> prompt -> Prompt List to add the node.  
  
The node has the following inputs:  
selection: A list of prompts registered in prompts.yaml. Outputs the prompt for the selected item.  
  
If the following items are filled in, the prompt from the selection will not be output, and the entered prompt will be output instead:  
Prompt Name: New prompt name or name of the prompt to update  
Positive Prompt: Content of the positive prompt  
Negative Prompt: Content of the negative prompt  
  
The entered prompt name and prompts will be saved in ComfyUI\user\PromptList\prompts.yaml.  
If prompts.yaml is not found, an empty prompts.yaml will be automatically created.  
If you change a prompt using the same Prompt Name, it will overwrite the prompt in prompts.yaml.

#### prompts.yaml format
~~~
#prompts.yaml
  prompt_name_1:
    positive: Positive prompt content
    negative: Negative prompt content
  prompt_name_2:
    positive: Another positive prompt
    negative: Another negative prompt
~~~

### We have prepared a [spreadsheet for editing prompts.yaml](https://docs.google.com/spreadsheets/d/1TxATrMXC1X1iSBRD4yFQZoOOwwNVz6irTSpnyv2T1ec/edit?usp=sharing).

#### Preparation before using the spreadsheet
1. File -> Make a copy -> Edit to your preferred file name and click "Make a copy"
2. After a while, "Export" will appear to the right of Help. Click Export -> Export as YAML
3. Authentication required window -> OK
4. Select your Google account and log in (if a warning appears: Advanced -> Go to prompt.yaml export (unsafe) -> Allow)

#### How to fill in the spreadsheet
![spreadsheets](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/images/spreadsheets.png)  
"prompt name" cell = prompt name  
Cell to the right of "positive" = positive prompt  
Cell to the right of "negative" = negative prompt  
Enter each of these. (The white cells in columns A and C are the input cells)  
  
If you want to increase the number of items to register, please use autofill.  
![autofill](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/images/autofill.gif)

*Note*  
Do not edit cells filled with gray.  

#### Exporting YAML
1. After a while, "Export" will appear to the right of Help. Click Export/Import -> Export -> Export complete
2. prompts.yaml will be output to your Google Drive.

#### Importing YAML
1. Place prompts.yaml in the same folder as the spreadsheet
2. Click Export/Import -> Import -> Import complete

#### Recommended usage
If you make the following settings before exporting the yaml, you can save the trouble of moving files:
1. Install Google Drive
2. Set up a symbolic link to prompts.yaml in the folder of this custom node
3. When prompts.yaml in Google Drive is updated, the file on your desktop will also be synchronized in about 10 seconds.
4. Success!

##### About symbolic links (for those who don't know)
It's similar to a shortcut, but the crucial difference is that it can behave as if it has a real existence.
Open the command prompt and execute the following command, replacing the links with the appropriate locations for your environment:
~~~
Windows
mklink Full_path_of_ComfyUI\user\PromptList\prompts.yaml Path_to_the_prompts.yaml_file_in_GoogleDrive
Mac/Linux
ln -s Path_to_the_prompts.yaml_file_in_GoogleDrive Full_path_of_ComfyUI\user\PromptList\prompts.yaml

Example
mklink E:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-PromptList\prompts.yaml Y:\My Drive\ComfyUI-PromptList\prompts.yaml
~~~
For Windows, if you introduce an official app called PowerToys, you can easily set it up with a right-click.
Give it a try!
  
## Notes

The prompt list is saved in the prompts.yaml file.
If you edit, add new prompts, or make changes, please press Refresh in the ComfyUI main menu to reflect the changes.

## Workflow
![sample](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/images/PromptListWorkflow.png)

## Update History
2024/09/06 1.2.0 Node input field is now multiline. Edit spreadsheet is now available.  
2024/08/24 1.0.0 Initial public release as it's working for now  

## License
This project is released under the MIT License. For details, please refer to the [LICENSE.txt](https://github.com/NakamuraShippo/ComfyUI-PromptList/blob/main/License.txt) file.  
You are free to use, modify, and distribute this software for personal and commercial purposes as long as you include the original copyright notice and disclaimer.

## Other
Bug reports or feature requests are welcome through any contactable means.
Pull requests are also welcome.

## Contact
[NakamuraShippo](https://lit.link/admin/creator)
