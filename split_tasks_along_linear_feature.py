"""
Split tasks for drone flying along a linear feature such as a road, river, or trail.

Steps:
- Obtain or digitize the feature as a line. Get it into a CRS with sensible units (meters, ideally). Make sure it's a single polyline (merge if necessary) to ensure the points along it are evenly spaced.
- Buffer the feature by half the desired task width (so if a 400-meter task width desired, buffer by 200m). 
- Create points along the original line feature at the desired interval (for example, every 500 m). Bonus: get them to start at 1/2 the spacing so that the Voronois in the next step are even from the beginning.
- Create Voronoi polyons from the points. Make sure the Voronoi box is big enough to enclose the buffered feature.
- Convert the Voronoi polygons to lines.
- Buffer the buffered area again by some tiny amount like 1 m (to ensure that there are no gaps between the original buffered area and the lines we will use to polygonize).
- Clip the voronoi lines by the double-buffered area
- Convert the original buffered area into lines.
- Ensure both the clipped voronoi lines and linearized buffered area are exploded singleparts (we can't merge singlepart and multipart geometry, so the easiest thing is to explode and singlepart everything).
- Merge the clipped voronois and linearized buffered area.
- Polygonize the resulting merged layer, which should produce a nicely segmented strip of task polygons.
"""
