# Character Killer

## Description
This is a project made to automate part of the process of creating custom characters in Mario Kart Wii.

It will take the character model and textures out of a source SZS file and insert them into all vehicle slots of the chosen character.

## Installation
This program needs a few things installed to run properly:
 - [Python](https://www.python.org/downloads/release/python-3121/)
 - [Wiimm's ISO Tools](https://wit.wiimm.de/)
 - [Wiimm's SZS Tools](https://szs.wiimm.de/)
 - [PyQt5](https://pypi.org/project/PyQt5/)

Once these are installed, simply download **character_killer.py** and place it wherever you like.

 ## Usage
 To use this program, type this into a terminal window in the same location as character_killer.py:

 `python character_killer.py`

 This will open the program. In the window that comes up, follow these steps:

 1. Select the character you'd like to replace.
 2. Click the button labelled **MKWii ISO**. You will need to provide either an ISO or WBFS file of Mario Kart Wii.
 3. Click the button labelled **Source Character**. You will need to provide an SZS file that already contains the custom character.
 4. Click the button labelled **Output Folder**. Choose a destination for the modified SZS files; it will create a folder titled `modified_szs` in this location.
 5. Click the button labelled **Patch Files!**. Once finished, the program will give the option to open the `modified_szs` folder.

<details>
<summary>Click to reveal: What does the program actually do with the files?</summary>

First, Wiimm's ISO Tools are used to extract the character files from the MKWii ISO. For example, if Mario is selected, it will extract `ma_bike-mr.szs`, `ma_kart-mr.szs`, etc. from `files/Race/Kart` and put them in a temporary folder `.tmp`.

Wiimm's SZS Tools are then used to extract the character files. It will extract the source SZS file to `.tmp/source_szs`, then extract the `driver_model.brres` file to `.tmp/source_brres`. The same thing is done to the 12 character SZS files, with the SZS files extracted to `.tmp/extracted_szs` and the BRRES files extracted to `.tmp/extracted_brres`.

The `model.mdl` file, `model_lod.mdl` file, and `Textures(NW4R)` folder of each extracted BRRES are then replaced with the models and textures of the source SZS file.

Finally, Wiimm's SZS Tools are used to rebuild the BRRES files, which are then put in the extracted SZS folders, which are then rebuilt and put into the `modified_szs` folder. The `.tmp` folder is deleted.

</details>

 ## Contributing
 Contributing is absolutely welcome. Feel free to fork this repository and make edits and changes as needed.

## License
This project is licensed under the [GNU General Public License v3.0](LICENSE).
