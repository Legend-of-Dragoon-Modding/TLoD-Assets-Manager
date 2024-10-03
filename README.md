# TLoD Assets Manager
TLoD Tool for manage game Assets (Textures, Models, Animations).
Version: **BETA 0.1**

*About the tool:*

Surely you are familiar to TLoD TMD Converter (tool for converting Models from TLoD) and TLoD Texture Converter (tool for converting Textures), now i merged the best of the two worlds in a single tool. TLoD Assets Manager. 

A tool designed to efficiently work with TLoD Models, Textures and in a future Sounds/Audio files.

At this very moment BETA Version 0.1, the idea about this tool is not only converting models/animations/textures, but also in a future help to modding community to easily grouping and sorting their installed Visual and Audio mods!. For BETA 0.2, Preview of Models/Animations and Textures in real time.

Since this tool realies heavily in [Severed Chains](https://github.com/Legend-of-Dragoon-Modding/Severed-Chains), i strongly recommend install it and run it (at least once) to get files properly deployed.

Also this tool came with a lot of news!.
- Changed support for 3D converted files into glTF 2.0, file format. Since Blender 4.0+ it's moving Collada DAE Files support into Legacy. This change also help us to store easily in the same file all the Animations from a converted model.
- Navigation for Conversion now it's more easy.
- Advanced features, deprecated, since Severed Chains convert almost all files into their "PSX Standard Version" file format.

Updates to be pull:
- Model/Animation and Texture Previewing.
- DEFF Converter.
- Sound/Music Converter.
- Visual/Sound Mods Managment.

---

## Severed Chains

You can check Severed Chains and it's Development in here:

Link: [Severed Chains](https://github.com/Legend-of-Dragoon-Modding/Severed-Chains)

Some parts of my code uses a "translated" version of Severed Chains code, Java -> Python.

This project made by: Monoxide.
Maintaned: Severed Chains Dev Team. (Lead Monoxide).
License: GPL Affero.

## PyQt6

As GUI i use PyQt6 a nice way to work on modern GUIs and hopefully get this tool working multiplatform without loosing my mind:

Link: [PyQt6](https://pypi.org/project/PyQt6/)

Project by: Riverbank Computing Limited.

Maintaned by: Phil Thimpson.

License: GPL v3.

### Other code snippets / Thanks

Monoxide, thanks a lot for making Severed Chains, also to helping me out understanding the Animations file formats and other stuff around the code.

TheFlyingZamboni, thanks a lot mate for giving the Texture code snippets and also for helping me understand how it works!.

StackOverflow Community in general. Since i look some solutions for stuff that i need to do in this code.

All rights reserved to their respective owners, you can check in the code the refereces for them!.

---

#### How to Install

If you are familiar with Python, you can pull the code and executing `main_gui.py`.

If you want to use a direct "compiled-Windows-EXE-version", download the lastest from here:
[Latest Build](https://github.com/Legend-of-Dragoon-Modding/TLoD-Assets-Manager/releases).

#### Setup

First start the tool will ask where it's located the `files` folder of Severed Chains, in here is where the TLoD Assets are deployed after Severed Chains first startup.

Later will ask a folder to deploy the converted files.

In the `CONFIG` Button you can change some options related to Window size and folders setup (if you want to change the deploy folder or the Severed Chains folder).

#### How to use it

In the main window will find several buttons to do specific tasks.
- Convert Battle Models. Pretty self-explanatory.
- Convert SubMap Models. Convert models used in the Pre-rendered Backgrounds, not only the characters but the 3D and Textures from the Pre-rendered Background.
- Convert WorldMap Models. Convert models used while world navigation. 
- Textures Only. In here you'll find the Textures which have no model related to it, for example the game GUI, some text, fonts, etc.
- Future Options: DEFF Conversion (convert Special Visual effects used during Magic casts, Dragoon attacks/magics, some other stuff), Sound Conversion, Mod Manager.