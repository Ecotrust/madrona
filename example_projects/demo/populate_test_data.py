from django.core.management import setup_environ
import os
import sys
sys.path.append(os.path.dirname(__file__))

import settings
setup_environ(settings)

#==================================#
from mlpa.models import *
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import User, Group
from lingcod.common.utils import enable_sharing

def main():
    user = User.objects.get(username='cburt')

    for model in [Shipwreck, Pipeline, Mpa, Folder, Array]:
        a = model.objects.all()
        for i in a:
            i.delete()
    
    g3 = GEOSGeometry('SRID=4326;POINT(-120.45 34.32)')
    g3.transform(settings.GEOMETRY_DB_SRID)
    wreck1 = Shipwreck(user=user, name="Wreck 1", geometry_orig=g3)
    wreck1.save()
    g3 = GEOSGeometry('SRID=4326;POINT(-120.85 34.82)')
    g3.transform(settings.GEOMETRY_DB_SRID)
    wreck2 = Shipwreck(user=user, name="Wreck 2", geometry_orig=g3)
    wreck2.save()

    g2 = GEOSGeometry('SRID=4326;LINESTRING(-120.42 34.37, -121.42 33.37)')
    g2.transform(settings.GEOMETRY_DB_SRID)
    pipeline1 = Pipeline(user=user, name="Pipeline 1", geometry_orig=g2)
    pipeline1.save()
    g2 = GEOSGeometry('SRID=4326;LINESTRING(-121.42 34.37, -122.42 33.37)')
    g2.transform(settings.GEOMETRY_DB_SRID)
    pipeline2 = Pipeline(user=user, name="Pipeline 2", geometry_orig=g2)
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

    g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
    print dir(g1)
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

    ####
    try:
        user2 = User.objects.get(username="user2")
    except:
        user2 = User.objects.create_user('user2', 'test@marinemap.org', password='pass')

    try:
        group1 = Group.objects.get(name="Group1")
    except:
        group1 = Group.objects.create(name="Group1")
    group1.save()
    user.groups.add(group1)
    user2.groups.add(group1)
    enable_sharing(group1)

    group2 = Group.objects.get(name=settings.SHARING_TO_PUBLIC_GROUPS[0])
    user.groups.add(group2)
    enable_sharing
    folder1.share_with(group2)

    ####
    g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.24 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
    g1.transform(settings.GEOMETRY_DB_SRID)
    mpa4 = Mpa(user=user2, name="Mpa4", geometry_orig=g1) 
    mpa4.save()

    folder4 = Folder(user=user2, name="Folder4")
    folder4.save()

    array4 = Array(user=user2, name="Array4")
    array4.save()

    mpa4.add_to_collection(array4)
    array4.add_to_collection(folder4)
    folder4.share_with(group1)
    


if __name__ == '__main__':
    main()
