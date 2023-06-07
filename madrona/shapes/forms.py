import os
import zipfile
import tempfile
import datetime
from django import forms
from django.forms.util import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.gis import gdal

#http://docs.djangoproject.com/en/dev/topics/http/file-uploads/
#http://www.neverfriday.com/sweetfriday/2008/09/-a-long-time-ago.html 

class UploadForm(forms.Form):

    file_obj = forms.FileField(label=_('Upload a Zipped Shapefile'))
    # TODO:
    # collect attribute info to stick in potential model
    #title = forms.CharField(max_length=50,label=_('Title'))
    #epsg = forms.IntegerField()

    def clean_file_obj(self):
        f = self.cleaned_data['file_obj']
        valid_shp, error = self.validate(f)
        if not valid_shp:
            raise ValidationError("A problem occured: %s" % error)

    def handle(self,filefield_data):
        """ Upload the file data, in chunks, to the SHP_UPLOAD_DIR specified in settings.py.
        """
        # ensure the upload directory exists
        if not os.path.exists(settings.SHP_UPLOAD_DIR):
            os.makedirs(settings.SHP_UPLOAD_DIR) 

        # contruct the full filepath and filename
        downloaded_file = os.path.normpath(os.path.join(settings.SHP_UPLOAD_DIR, filefield_data.name))

        print downloaded_file
        # if we've already got an upload with the same name, append the daymonthyear_minute
        if os.path.exists(downloaded_file):
            name, ext = os.path.splitext(downloaded_file)
            append = datetime.datetime.now().strftime('%d%m%Y_%m')
            downloaded_file = '%s_%s%s' % (name,append,ext) 

        print downloaded_file
        # write the zip archive to final location
        self.write_file(downloaded_file,filefield_data)

    def write_file(self,filename,filefield_data):
        destination = open(filename, 'wb+')
        for chunk in filefield_data.chunks():
            destination.write(chunk)
        destination.close()        

    def check_zip_contents(self, ext, zip_file):
        if not True in [info.filename.endswith(ext) for info in zip_file.infolist()]:
            return False
        return True

    def validate(self,filefield_data):
        """ Validate the uploaded, zipped shapefile by unpacking to a temporary sandbox.
        """
        # create a temporary file to write the zip archive to
        tmp = tempfile.NamedTemporaryFile(suffix='.zip', mode='w')

        # write zip to tmp sandbox
        self.write_file(tmp.name,filefield_data)

        if not zipfile.is_zipfile(tmp.name):
            return False, 'That file is not a valid Zip Archive'

        # create zip object
        zfile = zipfile.ZipFile(tmp.name)

        # ensure proper file contents by extensions inside
        if not self.check_zip_contents('shp', zfile):
            return False, 'Found Zip Archive but no file with a .shp extension found inside.'
        elif not self.check_zip_contents('prj', zfile):
            return False, 'You must supply a .prj file with the Shapefile to indicate the projection.'
        elif not self.check_zip_contents('dbf', zfile):
            return False, 'You must supply a .dbf file with the Shapefile to supply attribute data.'
        elif not self.check_zip_contents('shx', zfile):
            return False, 'You must supply a .shx file for the Shapefile to have a valid index.'

        # unpack contents into tmp directory
        tmp_dir = tempfile.gettempdir()
        for info in zfile.infolist():
            data = zfile.read(info.filename)
            shp_part = '%s%s%s' % (tmp_dir,os.path.sep,info.filename)
            fout = open(shp_part, "wb")
            fout.write(data)
            fout.close()

        # get the datasource name without extension
        ds_name = os.path.splitext(zfile.namelist()[0])[0]

        # ogr needs the full path to the unpacked 'file.shp'
        ds = gdal.DataSource('%s%s%s.shp' % (tmp_dir,os.path.sep,ds_name))

        # shapefiles have just one layer, so grab the first...
        layer = ds[0]

        # one way of testing a sane shapefile...
        # further tests should be able to be plugged in here...
        if layer.test_capability('RandomRead'):
            if str(ds.driver) == 'ESRI Shapefile':
                return True, None
            else:
                return False, "Sorry, we've experienced a problem on our server. Please try again later."
        else:
            return False, 'Cannot read the shapefile, data is corrupted inside the zip, please try to upload again'
