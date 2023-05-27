from django.contrib import admin
from django.urls import path

from image_recognizer.views import (
    fileUpload, getFile, getFilesFromBarcode, 
    getImageFromID, getAllDatas, dataUpload, getNextFile,
    possiblyProblematicIDs
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload_image", fileUpload),
    path("upload_data", dataUpload),
    path("get_file", getFile),
    path("get_image_ids", getFilesFromBarcode),
    path("get_image", getImageFromID),
    path("get_datas", getAllDatas),
    path("problematics", possiblyProblematicIDs),
    path("get_next_file", getNextFile)
]