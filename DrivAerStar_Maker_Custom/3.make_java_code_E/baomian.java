// Simcenter STAR-CCM+ macro: baomian.java
package macro;

import java.io.File;
import java.util.*;

import star.base.neo.*;
import star.common.*;
import star.meshing.*;
import star.surfacewrapper.*;
import star.vis.*;

public class baomian extends StarMacro {

  public void execute() {
    String formattedNumber = "<<<id>>>";
    String folderPath = "<<<dir>>>/";
    File folder = new File(folderPath);
    if (!folder.exists()) {
      folder.mkdirs();
    }

    File bodyDbs = new File(folderPath + "body.dbs");
    if (!bodyDbs.exists()) {
      execute0();
    } else {
      System.out.println(formattedNumber + " body.dbs exists");
    }
  }

  private void execute0() {
    String dirin = "<<<dir>>>/";
    String dirout = "<<<dir>>>/";
    String back = "<<<back>>>";

    Simulation simulation_0 = getActiveSimulation();

    Units units_0 = simulation_0.getUnitsManager().getPreferredUnits(Dimensions.Builder().length(1).build());
    Units units_1 = ((Units) simulation_0.getUnitsManager().getObject("mm"));

    PartImportManager partImportManager_0 = simulation_0.get(PartImportManager.class);
    partImportManager_0.importStlParts(
        new StringVector(new String[] {
            resolvePath(dirin + "part_01_Body.stl"),
            resolvePath(dirin + "part_02_UB_Smooth.stl"),
            resolvePath(dirin + "part_03_" + back + ".stl"),
            resolvePath(dirin + "part_07_Mirror.stl")
        }),
        "OneSurfacePerPatch", "OnePartPerFile", units_1, true, 1.0E-5, false, false);

    simulation_0.getSceneManager().createGeometryScene("Geometry Scene", "Outline", "Surface", 1, null);
    Scene scene_0 = simulation_0.getSceneManager().getScene("Geometry Scene 1");
    scene_0.initializeAndWait();
    scene_0.resetCamera();

    MeshPart body = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_01_Body"));
    MeshPart underbody = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_02_UB_Smooth"));
    MeshPart backPart = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_03_" + back));
    MeshPart mirror = ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_07_Mirror"));

    SurfaceWrapperAutoMeshOperation wrapper =
        (SurfaceWrapperAutoMeshOperation) simulation_0.get(MeshOperationManager.class)
            .createSurfaceWrapperAutoMeshOperation(
                new NeoObjectVector(new Object[] {body, underbody, backPart, mirror}), "Surface Wrapper");

    wrapper.getDefaultValues().get(BaseSize.class).setValueAndUnits(0.05, units_0);

    Units units_2 = ((Units) simulation_0.getUnitsManager().getObject(""));
    wrapper.getDefaultValues().get(PartsTargetSurfaceSize.class)
        .getRelativeSizeScalar().setValueAndUnits(10.0, units_2);
    wrapper.getDefaultValues().get(PartsMinimumSurfaceSize.class)
        .getRelativeSizeScalar().setValueAndUnits(5.0, units_2);
    wrapper.getDefaultValues().get(GlobalVolumeOfInterest.class)
        .getVolumeOfInterestOption().setSelected(GlobalVolumeOfInterestOption.Type.EXTERNAL);

    SurfaceCustomMeshControl mirrorControl = wrapper.getCustomMeshControls().createSurfaceControl();
    mirrorControl.getGeometryObjects().setQuery(null);
    mirrorControl.getGeometryObjects().setObjects(mirror);
    mirrorControl.getCustomConditions().get(PartsTargetSurfaceSizeOption.class)
        .setSelected(PartsTargetSurfaceSizeOption.Type.CUSTOM);
    mirrorControl.getCustomValues().get(PartsTargetSurfaceSize.class)
        .getRelativeSizeScalar().setValueAndUnits(3.0, units_2);

    wrapper.execute();

    RootDescriptionSource rootDescriptionSource_0 =
        simulation_0.get(SimulationMeshPartDescriptionSourceManager.class).getRootDescriptionSource();
    MeshOperationPart wrappedBody =
        ((MeshOperationPart) simulation_0.get(SimulationPartManager.class).getPart("Surface Wrapper"));

    rootDescriptionSource_0.exportDbsPartDescriptions(
        new NeoObjectVector(new Object[] {wrappedBody}), resolvePath(dirout + "body.dbs"), 1, "");

    simulation_0.get(SimulationPartManager.class)
        .removeObjects(body, underbody, backPart, mirror, wrappedBody);
    scene_0.closeInteractive();
    simulation_0.get(MeshOperationManager.class).removeObjects(wrapper);
    simulation_0.getSceneManager().removeObjects(scene_0);
  }
}
