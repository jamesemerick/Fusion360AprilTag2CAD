from typing import Tuple

import adsk.core
import adsk.fusion

from ...lib import fusion360utils
from . import png_util

EDGE_LENGTH = 2  # Unit: cm


def run():
    app = adsk.core.Application.get()
    ui = app.userInterface
    doc = app.activeDocument

    # Get input April Tag PNG
    png_file = fusion360utils.get_file("Select a AprilTag PNG file.", "*.png")

    # Extract the pixel array
    width, height, pixel_values = png_util.read_png(png_file)

    # Create a new document, get the root component and the sketches of the new design.
    doc: adsk.core.Document = app.documents.add(
        adsk.core.DocumentTypes.FusionDesignDocumentType
    )
    doc.activate()
    design: adsk.fusion.Design = doc.products.item(0)
    root_comp = design.rootComponent
    sketches = root_comp.sketches

    white, black = _get_material_colors()

    # Loop through each pixel and create a cube at the corresponding location
    voxel_size = EDGE_LENGTH / width
    for x in range(height):
        for y in range(width):
            # Create a sketch
            new_sketch = sketches.add(root_comp.xYConstructionPlane)
            sketch_lines = new_sketch.sketchCurves.sketchLines

            # Create sketch rectangle
            start_point = adsk.core.Point3D.create(x * voxel_size, y * voxel_size, 0)
            end_point = adsk.core.Point3D.create(
                x * voxel_size + voxel_size, y * voxel_size + voxel_size, 0
            )
            sketch_lines.addTwoPointRectangle(start_point, end_point)

            # Get the profile
            prof = new_sketch.profiles.item(0)

            # Create an extrusion input
            extrudes = root_comp.features.extrudeFeatures
            extrude_input = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            )

            # Define that the extent is a distance extent of the calculated voxel size
            distance = adsk.core.ValueInput.createByReal(voxel_size)
            # Set the distance extent
            extrude_input.setDistanceExtent(False, distance)
            # Set the extrude type to be solid
            extrude_input.isSolid = True

            # Create the extrusion
            ext = extrudes.add(extrude_input)

            # Get the body with the extrude
            brepBody = ext.bodies.item(0)

            # Set the light bulb besides the body node in the browser to off
            brepBody.isLightBulbOn = False
            brepBody.isVisible = True

            color = pixel_values[x][y]
            if color == 255:
                brepBody.appearance = white
            else:
                brepBody.appearance = black

            adsk.doEvents()

    # Save the new design.
    doc_name = f"{png_file.stem}-{EDGE_LENGTH*10}x{EDGE_LENGTH*10}mm"
    active_hub = app.data.activeHub
    active_folder = app.data.activeFolder
    result = ui.messageBox(
        f"Save to {active_hub.name}:{active_folder.name} as {doc_name}?",
        "Save AprilTag",
        adsk.core.MessageBoxButtonTypes.YesNoButtonType,
        adsk.core.MessageBoxIconTypes.QuestionIconType,
    )
    if result == adsk.core.DialogResults.DialogYes:
        doc.saveAs(
            doc_name,
            active_folder,
            "",
            "",
        )
    else:
        ui.messageBox("Skipping save...")

    # Export STL
    result = ui.messageBox(
        "Download the STL file?",
        "Download STL",
        adsk.core.MessageBoxButtonTypes.YesNoButtonType,
    )
    if result == adsk.core.DialogResults.DialogYes:
        download_path = fusion360utils.get_download_dir(app) / f"{doc_name}.stl"
        stl_export_options = design.exportManager.createSTLExportOptions(
            root_comp, str(download_path)
        )
        stl_export_options.sendToPrintUtility = False
        design.exportManager.execute(stl_export_options)

    ui.messageBox("AprilTag conversion complete!")


def _get_material_colors() -> Tuple[adsk.core.Appearance, adsk.core.Appearance]:
    """Get the materials to be used when created pixel solids."""
    app = adsk.core.Application.get()
    fusionMaterials = app.materialLibraries.itemByName("Fusion 360 Appearance Library")
    white_paint = fusionMaterials.appearances.itemByName(
        "Paint - Enamel Glossy (White)"
    )
    black_paint = fusionMaterials.appearances.itemByName(
        "Paint - Enamel Glossy (Black)"
    )
    return white_paint, black_paint
