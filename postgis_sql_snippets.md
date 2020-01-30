
 WITH unique_geoms (fid, geom, uuid, id, region_cod, region_nam, district_c, district_n, ward_code, ward_name, vil_mtaa_c, vil_mtaa_n, hamlet, ea_geocode, status, authority, category_1, areaid, division, objectid, shape_leng, shape_area, layer, match) as 
  (SELECT row_number() OVER (PARTITION BY ST_AsBinary(geom)) as fid, geom, uuid, id, region_cod, region_nam, district_c, district_n, ward_code, ward_name, vil_mtaa_c, vil_mtaa_n, hamlet, ea_geocode, status, authority, category_1, areaid, division, objectid, shape_leng, shape_area, layer, match 
    FROM "Tanzania_EA")
 SELECT fid, geom, uuid, id, region_cod, region_nam, district_c, district_n, ward_code, ward_name, vil_mtaa_c, vil_mtaa_n, hamlet, ea_geocode, status, authority, category_1, areaid, division, objectid, shape_leng, shape_area, layer, match 
 FROM unique_geoms 
 WHERE fid=1;
