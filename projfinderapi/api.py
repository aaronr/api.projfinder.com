from flask import abort, request, render_template, jsonify
import psycopg2
import sys
import os
import json

def api_landing():
    return render_template('api_landing.html')

def reproject():
    if request.method == 'GET':
        connstring="dbname='projfinder' port=5432 user='aaronr' host='localhost' password='aaronr'"
        try:
            conn=psycopg2.connect(connstring)
            cursor=conn.cursor()
            #output += 'Connection Success\n'
        except Exception, e:            
            abort(404)

        if request.args['x'] and request.args['y'] and request.args['epsg']:
            x = request.args['x']
            y = request.args['y']
            epsg = request.args['epsg']
            reprojection = {}
            reprojection['type'] = 'reprojection'
            # Need to reproject the coords
            sql = "select st_asgeojson(st_geometryfromtext('POINT(%s %s)',4326),15,4) as request, st_asgeojson(st_transform(st_geometryfromtext('POINT(%s %s)',4326),%s),15,4) as result limit 1;" % (x,y,x,y,epsg)
            cursor.execute(sql)
            results = cursor.fetchone()                
            reprojection['request'] = json.loads(results[0])
            reprojection['response'] = json.loads(results[1])
            return jsonify(reprojection)
        else:
            abort(404)

def projfinder():
    if request.method == 'GET':
        connstring="dbname='projfinder' port=5432 user='aaronr' host='localhost' password='aaronr'"
        try:
            conn=psycopg2.connect(connstring)
            cursor=conn.cursor()
            #output += 'Connection Success\n'
        except Exception, e:            
            abort(404)

        if request.args['ref_lon'] and request.args['ref_lat'] and request.args['unknown_x'] and request.args['unknown_y']:
            ref_lon = request.args['ref_lon']
            ref_lat = request.args['ref_lat']
            unknown_x = request.args['unknown_x']
            unknown_y = request.args['unknown_y']

            # The request object
            projrequest = {}
            sql = "select st_asgeojson(st_geometryfromtext('POINT(%s %s)',-1)) as unknown_geojson, st_asgeojson(st_geometryfromtext('POINT(%s %s)',4326),15,4) as ref_geojson" % (unknown_x, unknown_y, ref_lon, ref_lat)
            cursor.execute(sql)
            results = cursor.fetchone()
            projrequest['reference'] = json.loads(results[1])
            projrequest['unknown'] = json.loads(results[0])
            projrequest['type'] = 'projrequest'

            # The response will be an array of objects
            projresponse = []

            # This is the larger response object
            projfinder = {}
            projfinder['type'] = 'projfinder'
            projfinder['request'] = projrequest
            projfinder['response'] = projresponse

            limit = 10
            if request.args['limit'] and int(request.args['limit']) < 100:
                limit = request.args['limit']
            # Need to reproject the coords
            sql = "select st_asgeojson(st_geometryfromtext('POINT(%s %s)',sp.srid),15,4) as geojson, sp.srid as srid, split_part(sp.srtext,'\"',2) as name, st_distance(st_transform(st_geometryfromtext('POINT(%s %s)',4326),sp.srid), st_geometryfromtext('POINT(%s %s)',sp.srid)) as distance from spatial_ref_sys as sp, epsg_coordinatereferencesystem as cs, epsg_poly_bb as bb where st_contains(bb.geom, st_geometryfromtext('POINT(%s %s)',4326)) is true and cs.area_of_use_code=bb.area_code and exists(select 1 from spatial_ref_sys where srid=cs.coord_ref_sys_code) and srid=cs.coord_ref_sys_code group by sp.srid, sp.auth_name order by distance,char_length(split_part(sp.srtext,'\"',2)) limit %s" % (unknown_x, unknown_y, ref_lon, ref_lat, unknown_x, unknown_y, ref_lon, ref_lat, limit)
            cursor.execute(sql)
            results = cursor.fetchall()
            for i,row in enumerate(results):
                projresponse = {}
                projresponse['type'] = 'projresponse'
                projresponse['rank'] = i
                projresponse['point'] = json.loads(row[0])
                projresponse['srid'] = row[1]
                projresponse['name'] = row[2]
                projresponse['distance'] = row[3]
                projfinder['response'].append(projresponse)
            return jsonify(projfinder)
        else:
            abort(404)

