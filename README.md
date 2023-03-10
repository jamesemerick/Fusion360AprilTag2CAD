# Fusion360AprilTag2CAD

An Autodesk [Fusion 360](https://www.autodesk.com/products/fusion-360/overview) add-in
for converting PNG AprilTag images to a Fusion 360 solid model.

The resultant model can then be exporting to an STL file to be 3D printed. 

Pre-generated AprilTag images can be downloaded from the
[apriltag-imgs](https://github.com/AprilRobotics/apriltag-imgs) GitHub repository. 

[Fusion 360 API
Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)

## Installation

1. Download this repo.
1. Open Fusion 360, click the `Scripts and Add-Ins` command from the `UTILITIES` tab in
   the toolbar. When the dialog opens, click the `Add-Ins` tab, then the green `+` next
   to `My Add-Ins`.
![fusion360_addins_menu](https://user-images.githubusercontent.com/17363991/224447667-f286f95b-a117-4f42-b29c-98f134803f03.png)
1. Choose the directory that this repository was downloaded to. 
1. Click `Run`
1. An `AprilTag2CAD` command icon should now exist next to the  `Scripts and Add-Ins`
   command.  
![fusion360_apriltag_icon](https://user-images.githubusercontent.com/17363991/224447706-b4410381-eae7-4180-9e6f-d6eec5956974.png)


## Usage

1. Click the `AprilTag2CAD` command from the `UTILITIES` tab.
1. Select the PNG file you want to convert. 
1. Optionally choose to save the new Fusion Document and export it to an STL file.



https://user-images.githubusercontent.com/17363991/224447717-ab17ceda-34ce-46ba-9b03-b90dcfd0b68a.mov



*NOTE: This add-in uses only Python standard library so no additional modules need to be
installed in the Fusion 360 Python environment.* 

*NOTE: This add-in could also be run as a Fusion 360 script by taking the
[apriltag_to_cad](./commands/createAprilTagModel/apriltag_to_cad.py) and
[png_util](./commands/createAprilTagModel/apriltag_to_cad.py) modules and running them
from a Fusion 360 script.

## Future Features
- [ ] Allow users to specify the dimensions (height, width, depth) of the AprilTag
  model.
- [ ] Option to create a AprilTags from a folder containing multiple PNG files. 
- [ ] Option to export to STL (instead of exporting by default).
- [ ] Support additional file type exports. 

## Contributing
Contributions via Pull Requests and filing Issues are welcome. 
