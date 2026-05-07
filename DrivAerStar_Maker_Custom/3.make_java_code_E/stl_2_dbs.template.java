// Simcenter STAR-CCM+ macro: stl_2_dbs.java
package macro;

import java.io.File;
import java.util.*;

import star.base.neo.*;
import star.common.*;
import star.meshing.*;
import star.vis.*;

public class stl_2_dbs extends StarMacro {

  public void execute() {
    String formattedNumber = "<<<id>>>";
    String dirin = "<<<dir>>>/";
    String dirout = "<<<dir>>>/";

    File frontInput = new File(dirin + "part_05_Wheels_Front_Closed.stl");
    File rearInput = new File(dirin + "part_06_Wheels_Rear_Closed.stl");
    File frontOutput = new File(dirout + "Wheels_Front.dbs");
    File rearOutput = new File(dirout + "Wheels_Rear.dbs");

    if (frontInput.exists() && rearInput.exists() && (!frontOutput.exists() || !rearOutput.exists())) {
      execute0(formattedNumber);
    }
  }

  private void execute0(String dirid) {
    String dirin = "<<<dir>>>/";
    String dirout = "<<<dir>>>/";

    Simulation simulation_0 = getActiveSimulation();

    PartImportManager partImportManager_0 = simulation_0.get(PartImportManager.class);

    Units units_1 = ((Units) simulation_0.getUnitsManager().getObject("mm"));

    partImportManager_0.importStlParts(
        new StringVector(new String[] {
            resolvePath(dirin + "part_05_Wheels_Front_Closed.stl"),
            resolvePath(dirin + "part_06_Wheels_Rear_Closed.stl")
        }),
        "OneSurfacePerPatch", "OnePartPerFile", units_1, true, 1.0E-5, false, false);

    simulation_0.getSceneManager().createGeometryScene("Geometry Scene", "Outline", "Surface", 1, null);

    Scene scene_0 = simulation_0.getSceneManager().getScene("Geometry Scene 1");
    scene_0.initializeAndWait();
    scene_0.resetCamera();

    RootDescriptionSource rootDescriptionSource_0 =
        simulation_0.get(SimulationMeshPartDescriptionSourceManager.class).getRootDescriptionSource();

    MeshPart meshPart_0 =
        ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_05_Wheels_Front_Closed"));
    rootDescriptionSource_0.exportDbsPartDescriptions(
        new NeoObjectVector(new Object[] {meshPart_0}), resolvePath(dirout + "Wheels_Front.dbs"), 1, "");

    MeshPart meshPart_1 =
        ((MeshPart) simulation_0.get(SimulationPartManager.class).getPart("part_06_Wheels_Rear_Closed"));
    rootDescriptionSource_0.exportDbsPartDescriptions(
        new NeoObjectVector(new Object[] {meshPart_1}), resolvePath(dirout + "Wheels_Rear.dbs"), 1, "");

    simulation_0.get(SimulationPartManager.class).removeObjects(meshPart_0, meshPart_1);
    scene_0.closeInteractive();
    simulation_0.getSceneManager().removeObjects(scene_0);
  }
}
