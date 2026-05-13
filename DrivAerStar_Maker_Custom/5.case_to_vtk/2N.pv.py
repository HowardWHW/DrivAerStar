# trace generated using paraview version 5.12.1
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 12

#### import the simple module from the paraview
from paraview.simple import *
import sys
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'EnSight Reader'
kwWakeRefine0503case = EnSightReader(registrationName='KwWakeRefine0503.case', CaseFileName=sys.argv[1])

UpdatePipeline(time=0.0, proxy=kwWakeRefine0503case)

# create a new 'Extract Block'
extractBlock1 = ExtractBlock(registrationName='ExtractBlock1', Input=kwWakeRefine0503case)

# Properties modified on extractBlock1
extractBlock1.Selectors = ['/Root/Wheels_FrontSurface', '/Root/Wheels_RearSurface', '/Root/bodypart_01_Body_Open_EngineBayFlowSurface', '/Root/bodypart_02_UB_EngineBayFlowSurface', '/Root/bodypart_03_NotchbackSurface', '/Root/bodypart_04_ExhaustSystem_EngineBayFlowSurface', '/Root/bodypart_07_MirrorSurface', '/Root/bodypart_08_EngineBayTrim_EngineBayFlowSurface', '/Root/bodypart_09_EngineAndGearbox_EngineBayFlowSurface', '/Root/bodypart_10_FrontGrills_EngineBayFlowSurface', '/Root/Porosity_EngineBayFlow']

UpdatePipeline(time=0.0, proxy=extractBlock1)

# create a new 'Programmable Filter'
programmableFilter1 = ProgrammableFilter(registrationName='ProgrammableFilter1', Input=extractBlock1)

# Properties modified on programmableFilter1
programmableFilter1.Script = """input_mb = self.GetInputDataObject(0, 0)
output_mb = self.GetOutput()

output_mb.ShallowCopy(input_mb)

for i in range(output_mb.GetNumberOfBlocks()):
    block = output_mb.GetBlock(i)
    if not block or not block.IsA("vtkDataSet"):
        continue
    
    cell_data = block.GetCellData()
    wss_vec = cell_data.GetArray("WallShearStress")

    if not wss_vec:
        num_cells = block.GetNumberOfCells()

        wss_array = vtk.vtkFloatArray()
        wss_array.SetName("WallShearStress")
        wss_array.SetNumberOfComponents(3)
        wss_array.SetNumberOfTuples(num_cells)
        wss_array.Fill(0.0)
        cell_data.AddArray(wss_array)

        for suffix in [\'i\', \'j\', \'k\', \'Magnitude\']:
            component_array = vtk.vtkFloatArray()
            component_array.SetName(f"WallShearStress{suffix}")
            component_array.SetNumberOfValues(num_cells)
            component_array.Fill(0.0)
            cell_data.AddArray(component_array)
    else:
        need_i = not cell_data.GetArray("WallShearStressi")
        need_j = not cell_data.GetArray("WallShearStressj")
        need_k = not cell_data.GetArray("WallShearStressk")
        need_mag = not cell_data.GetArray("WallShearStressMagnitude")

        if need_i or need_j or need_k or need_mag:
            num_cells = block.GetNumberOfCells()
            wss_i = vtk.vtkFloatArray() if need_i else None
            wss_j = vtk.vtkFloatArray() if need_j else None
            wss_k = vtk.vtkFloatArray() if need_k else None
            wss_mag = vtk.vtkFloatArray() if need_mag else None

            if wss_i:
                wss_i.SetName("WallShearStressi")
                wss_i.SetNumberOfValues(num_cells)
            if wss_j:
                wss_j.SetName("WallShearStressj")
                wss_j.SetNumberOfValues(num_cells)
            if wss_k:
                wss_k.SetName("WallShearStressk")
                wss_k.SetNumberOfValues(num_cells)
            if wss_mag:
                wss_mag.SetName("WallShearStressMagnitude")
                wss_mag.SetNumberOfValues(num_cells)

            for idx in range(num_cells):
                x, y, z = wss_vec.GetTuple3(idx)
                if wss_i:
                    wss_i.SetValue(idx, x)
                if wss_j:
                    wss_j.SetValue(idx, y)
                if wss_k:
                    wss_k.SetValue(idx, z)
                if wss_mag:
                    wss_mag.SetValue(idx, (x * x + y * y + z * z) ** 0.5)

            if wss_i:
                cell_data.AddArray(wss_i)
            if wss_j:
                cell_data.AddArray(wss_j)
            if wss_k:
                cell_data.AddArray(wss_k)
            if wss_mag:
                cell_data.AddArray(wss_mag)
"""
programmableFilter1.RequestInformationScript = ''
programmableFilter1.RequestUpdateExtentScript = ''
programmableFilter1.PythonPath = ''

UpdatePipeline(time=0.0, proxy=programmableFilter1)

# create a new 'Cell Size'
cellSize1 = CellSize(registrationName='CellSize1', Input=programmableFilter1)

UpdatePipeline(time=0.0, proxy=cellSize1)

# create a new 'Merge Blocks'
mergeBlocks1 = MergeBlocks(registrationName='MergeBlocks1', Input=cellSize1)

UpdatePipeline(time=0.0, proxy=mergeBlocks1)

# create a new 'Extract Surface'
extractSurface1 = ExtractSurface(registrationName='ExtractSurface1', Input=mergeBlocks1)

UpdatePipeline(time=0.0, proxy=extractSurface1)

# set active source
SetActiveSource(programmableFilter1)

# set active source
SetActiveSource(cellSize1)

# set active source
SetActiveSource(mergeBlocks1)

# set active source
SetActiveSource(extractSurface1)

# create a new 'Surface Normals'
surfaceNormals1 = SurfaceNormals(registrationName='SurfaceNormals1', Input=extractSurface1)

# Properties modified on surfaceNormals1
surfaceNormals1.ComputeCellNormals = 1

UpdatePipeline(time=0.0, proxy=surfaceNormals1)

# save data
SaveData(sys.argv[2], proxy=surfaceNormals1, ChooseArraysToWrite=1,
    CellDataArrays=['Area', 'Normals', 'Pressure', 'WallShearStressi', 'WallShearStressj', 'WallShearStressk'])