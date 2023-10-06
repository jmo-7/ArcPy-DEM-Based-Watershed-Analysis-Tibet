# Initial setup
import arcpy
from arcpy import env
from arcpy.sa import *

# Import DEM to the project Geodatabase (GDB):
Input_DEM_List = [r"# Path of the filled DEM", r"# Path of the original (i.e., Baseline) DEM"]
Destination = r"# Path of the project GDB"
for DEM in Input_DEM_List:
    arcpy.conversion.RasterToGeodatabase(DEM, Destination, "")
    print(f"\n{DEM} has been successfully imported!")


# Set the workspace environment:
env.workspace = r"# Path of the project GDB"

# Perform map algebra to obtain the difference between the baseline and filled DEMs:
outRas = Raster("# File name of the filled DEM") - Raster("# File name of the original (i.e., Baseline) DEM")
outRas.save("# File name for saving the output DEM's difference's raster")

# Create flow direction raster using the "Flow Direction (Spatial Analyst)" tool:
in_surface_raster = "# File name of the filled DEM"
force_flow = "NORMAL"
out_drop_raster = None
flow_direction_type = "D8"
outFlowDirection = FlowDirection(in_surface_raster, force_flow, out_drop_raster, flow_direction_type)
outFlowDirection.save("# File name for saving the output flow direction's raster")

# Create basin raster using the "Basin (Spatial Analyst)" tool:
outBasin = Basin("# File name of the flow direction's raster")
outBasin.save("# File name for saving the output basin's raster")

# Convert the basin raster into polygon feature class using the "Raster To Polygon (Conversion)" tool:
in_basin_raster = "# File name of the basin's raster"
out_basin_polygon = "# File name of the output basin polygon's feature class"
simplify = "SIMPLIFY"
arcpy.conversion.RasterToPolygon(in_basin_raster, out_basin_polygon, simplify)

# Create the flow accumulation raster using the "Flow Accumulation (Spatial Analyst)" tool:
in_flow_direction_ras = "# File name of the flow direction's raster"
out_flow_accumulation_ras = FlowAccumulation(in_flow_direction_ras)
out_flow_accumulation_ras.save("# File name for saving the output flow accumulation's raster")

# Create 4 stream rasters with 4 different threshold values using the "Con (Spatial Analyst)" tool:
in_conditional_ras = "# File name of the flow accumulation's raster"
true_constant = 1
false_constant = 0
where_clause_list = ["VALUE > 1000", "VALUE > 700", "VALUE > 500", "VALUE > 300"]
threshold_values_list = ["1000", "700", "500", "300"]
for clause, threshold in zip(where_clause_list, threshold_values_list):
    print(f"\nWhere clause used in this iteration is: {clause}")
    out_con = Con(in_conditional_ras, true_constant, false_constant, clause)
    out_con.save(f"stream_ras_{threshold}")
    print(f"\nstream_ras_{threshold} has been successfully produced!")

# Create 4 stream link rasters for the 4 threshold values using the "Stream Link (Spatial Analyst)" tool:
stream_ras_list = arcpy.ListRasters("stream*")
for stream_ras in stream_ras_list:
    print(f"\nStream raster in this iteration is: {stream_ras}")
    out_stream_link_ras = StreamLink(stream_ras, in_flow_direction_ras)
    out_stream_link_ras.save(f"{stream_ras}_link")
    print(f"\n{stream_ras}_link has been successfully produced!")

# Create 4 stream network feature classes for the 4 stream link rasters using the "Stream to Feature (Spatial Analyst)" tool:
stream_link_ras_list = ["stream_ras_1000_link", "stream_ras_700_link", "stream_ras_500_link", "stream_ras_300_link"]
output_name_list = ["stream_network_1000", "stream_network_700", "stream_network_500", "stream_network_300"]
for stream_link_ras, name in zip(stream_link_ras_list, output_name_list):
    print(f"\nStream link raster in this iteration is: {stream_link_ras}")
    StreamToFeature(stream_link_ras, in_flow_direction_ras, name)
    print(f"\n{name} has been successfully produced!")

# Create a stream order raster for the stream link raster with 1000 threshold value using the "Stream Order (Spatial Analyst)" tool:
in_stream_ras = "stream_ras_1000"
order_method = "STRAHLER"
out_stream_order_ras = StreamOrder(in_stream_ras, in_flow_direction_ras, order_method)
out_stream_order_ras.save("stream_order_ras_1000")
print(f"\nstream_order_ras_1000 has been successfully produced!")

# Convert the stream order raster into a stream order feature class using the "Stream to Feature (Spatial Analyst)" tool:
in_stream_order_ras = "stream_order_ras_1000"
out_stream_order_fc = "stream_order_fc_1000"
StreamToFeature(in_stream_order_ras, in_flow_direction_ras, out_stream_order_fc)
print(f"\n{out_stream_order_fc} has been successfully produced!")

print("\nProcess is completed!")