from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.dirname(__file__))

import settings
setup_environ(settings)

#==================================#
from mlpa.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User

def main():
    user = User.objects.get(username='perry')

    for model in [Shipwreck, Pipeline, Mpa, Folder, Array]:
        a = model.objects.all()
        for i in a:
            i.delete()
    
    g3 = GEOSGeometry('SRID=4326;POINT(-120.45 34.32)')
    g3.transform(settings.GEOMETRY_DB_SRID)
    wreck1 = Shipwreck(user=user, name="Wreck 1", geometry_final=g3)
    wreck1.save()
    g3 = GEOSGeometry('SRID=4326;POINT(-120.85 34.82)')
    g3.transform(settings.GEOMETRY_DB_SRID)
    wreck2 = Shipwreck(user=user, name="Wreck 2", geometry_final=g3)
    wreck2.save()

    g2 = GEOSGeometry('SRID=4326;LINESTRING(-120.42 34.37, -121.42 33.37)')
    g2.transform(settings.GEOMETRY_DB_SRID)
    pipeline1 = Pipeline(user=user, name="Pipeline 1", geometry_final=g2)
    pipeline1.save()
    g2 = GEOSGeometry('SRID=4326;LINESTRING(-121.42 34.37, -122.42 33.37)')
    g2.transform(settings.GEOMETRY_DB_SRID)
    pipeline2 = Pipeline(user=user, name="Pipeline 2", geometry_final=g2)
    pipeline2.save()

    g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
    g1.transform(settings.GEOMETRY_DB_SRID)
    mpa1 = Mpa(user=user, name="Mpa1", geometry_orig=g1) 
    # geometry_final will be set with manipulator
    mpa1.save()

    g1 = GEOSGeometry('SRID=4326;POLYGON((-121.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -121.42 34.37))')
    g1.transform(settings.GEOMETRY_DB_SRID)
    mpa2 = Mpa(user=user, name="Mpa2", geometry_orig=g1) 
    # geometry_final will be set with manipulator
    mpa2.save()

    g1 = GEOSGeometry('SRID=4326;POLYGON((-122.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -122.42 34.37))')
    g1.transform(settings.GEOMETRY_DB_SRID)
    mpa3 = Mpa(user=user, name="Mpa3", geometry_orig=g1) 
    # geometry_final will be set with manipulator
    mpa3.save()

    folder1 = Folder(user=user, name="Folder1")
    folder1.save()
    folder2 = Folder(user=user, name="Folder2")
    folder2.save()
    folder3 = Folder(user=user, name="Folder3")
    folder3.save()

    array1 = Array(user=user, name="Array1")
    array1.save()
    array2 = Array(user=user, name="Array2")
    array2.save()

    mpa1.add_to_collection(array1)
    mpa2.add_to_collection(array2)
    array1.add_to_collection(folder1)
    wreck1.add_to_collection(folder1)
    pipeline1.add_to_collection(folder1)
    folder3.add_to_collection(folder2)



if __name__ == '__main__':
    main()
