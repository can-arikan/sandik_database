import json
from django.http import HttpResponse, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from image_recognizer.image_utils.converter import convert
from image_recognizer.image_utils.divider import barcodeDivide
from image_recognizer.image_utils.scanner import warpImage
from django.views.decorators.csrf import csrf_exempt
from image_recognizer.models import TutanakImage, TutanakResimVeri, Veri
from django.db.models import Count
from pyzbar.pyzbar import decode
from django.db.models.manager import BaseManager

import cv2
import base64

def findInTutanaks(tutanaklar, id):
    for idx in range(len(tutanaklar)):
        if tutanaklar[idx].pk == id:
            return idx
    return -1

def isAllVerisEqual(veriler: BaseManager[Veri]):
    for idx in range(len(veriler) - 1):
        if not veriler[idx].equals(veriler[idx + 1]):
            return False
    return True

def read_qr_code(img, barcode):
    detect = cv2.QRCodeDetector()
    try:
        cv2.imwrite("./barcode.png", barcode)
        retval, value, _, _ = detect.detectAndDecodeMulti(img)
        if not retval:
            raise Exception("????")
        return value[0]
    except:
        try:
            retval, value, _, _ = detect.detectAndDecodeMulti(barcode)
            if not retval:
                raise Exception("????")
            return value[0]
        except:
            return

def read_qr(img, barcode):
    data1 = None
    data2 = None
    try:
        for i in decode(img):
            data1 = i.data.decode('utf-8')
    except: ""
    try:
        for i in decode(barcode):
            data2 = i.data.decode('utf-8')
    except: ""
    return data1, data2

@csrf_exempt
def fileUpload(request: WSGIRequest):
    if request.method != "POST":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        img = request.FILES["image"]
        img = convert(img)
        img = warpImage(img)
        if img is None:
            return JsonResponse({"Result": "Could not warped image"}, status=300)
        original_image = img
        barcode = barcodeDivide(img) 
        barcode_value0 = read_qr_code(img, barcode)

        barcode_value1, barcode_value2 = read_qr(img, barcode)

        barcode_value = ""
        if barcode_value1 == barcode_value2:
            barcode_value = barcode_value1
        elif barcode_value0 is not None:
            barcode_value = barcode_value0
        
        if barcode_value == '':
            barcode_value = None
        
        _, buffer = cv2.imencode('.png', original_image)

        original_image = base64.b64encode(buffer)

        TutanakImage.objects.create(tutanak=original_image, barcode=barcode_value)
        
        return JsonResponse({"Result": "File Successfully Transformed"}, status=200)

@csrf_exempt
def getFile(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        images = TutanakImage.objects.annotate(veri_sayisi=Count('tutanak_veri__veri'))
        images = sorted(images, key=lambda x: x.veri_sayisi)
        
        if len(images) != 0:
            image = images[0]
            return JsonResponse({"Barcode": image.barcode, "image_id": image.pk})
        
        return JsonResponse({"Result": "No Image Exists"}, status=400)

@csrf_exempt
def getNextFile(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        images = TutanakImage.objects.annotate(veri_sayisi=Count('tutanak_veri__veri'))
        images = sorted(images, key=lambda x: x.veri_sayisi)
        last_id = int(request.GET['image_id'])
        
        if len(images) != 0:
            index = findInTutanaks(images, last_id)
            if index == -1:
                return JsonResponse({"Result": "Image Not Exists"}, status=400)
            index = pow((index + 1), 1, len(images))
            image = images[index]
            return JsonResponse({"Barcode": image.barcode, "image_id": image.pk})
        
        return JsonResponse({"Result": "No Image Exists"}, status=400)

@csrf_exempt
def getFilesFromBarcode(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        data = request.GET
        images = TutanakImage.objects.filter(barcode=data['barcode'])
        return JsonResponse({"Result": [i.pk for i in images]})
    
@csrf_exempt
def getImageFromID(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        data = request.GET
        if TutanakImage.objects.filter(pk=data['image_id']).exists():
            image = TutanakImage.objects.get(pk=data['image_id'])
            jpg_original = base64.b64decode(image.tutanak[2:-1])
            response = HttpResponse(content_type="image/png")
            response.content = jpg_original
            return response
        else:
            return JsonResponse({"Result": "Image Does Not Exist"}, status=400)

@csrf_exempt
def dataUpload(request: WSGIRequest):
    if request.method != "POST":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        data = json.loads(request.body)

        flag = None

        try:
            int(data['barcode'])
        except Exception:
            flag = "Is Not Integer"

        if flag == "Is Not Integer":
            return JsonResponse({"Result": "Barcode Must Be Integer"}, status=405)

        if data['barcode'] is None or data['barcode'] == "":
            return JsonResponse({"Result": "Barcode Can Not Be Empty Or Null String"}, status=405)

        if not TutanakImage.objects.filter(pk=data['ID']).exists():
            return JsonResponse({"Result": "Image Does Not Exist"}, status=404)

        tutanak_image = TutanakImage.objects.get(pk=data['ID'])
        
        if tutanak_image.barcode is not None:
            if data['barcode'] != tutanak_image.barcode:
                tutanak_image.need_to_be_checked = True
                tutanak_image.save()
                return JsonResponse({"Result": "Barcodes Does Not Match Contact Admin"}, status=300)
        
        tutanak_resim_veri, _ = TutanakResimVeri.objects.get_or_create(ysk_no=data['barcode'])
        tutanak_image.barcode = data['barcode']
        tutanak_image.tutanak_veri = tutanak_resim_veri
        tutanak_image.save()
        Veri.objects.create(
            tutanak_veri = tutanak_resim_veri,
            rt_oy = data['RT'],
            kk_oy = data['KK'],
            toplam_oy = data['Toplam'],
            gecersiz_oy = data['Gecersiz'],
            sandik_no = data['SandikNo'],
        )
        return JsonResponse({"Result": "Data Saved"})
    
@csrf_exempt
def getAllDatas(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        verileri = Veri.objects.all()

        results = [
            {
                "RT": i.rt_oy,
                "KK": i.kk_oy,
                "Toplam Oy": i.toplam_oy,
                "Gecersiz Oy": i.gecersiz_oy,
                "Sandik No": i.sandik_no,
                "YSK No": i.tutanak_veri.ysk_no,
                "Image ID": TutanakImage.objects.get(tutanak_veri=i.tutanak_veri).pk
            } for i in verileri
        ]

        ysk_numbers = TutanakResimVeri.objects.all()
        ysk_numbers = [i.ysk_no for i in ysk_numbers]

        data = {}

        for i in ysk_numbers:
            data[i] = []

        for idx in range(len(results)):
            result = results[idx]
            data[result["YSK No"]].append(result)

        return JsonResponse(data)

@csrf_exempt
def possiblyProblematicIDs(request: WSGIRequest):
    if request.method != "GET":
        return JsonResponse({"Result": "Page not found"}, status=404)
    else:
        tutanak_images = TutanakImage.objects.filter(need_to_be_checked=True)
        tutanak_images = [i.pk for i in tutanak_images]
        all_ysk_nos = TutanakResimVeri.objects.all()
        all_ysk_nos = [i.ysk_no for i in all_ysk_nos]
        not_all_equal_veris = []
        for ysk_no in all_ysk_nos:
            all_ysk_no_veris = Veri.objects.filter(tutanak_veri__ysk_no=ysk_no)
            if not isAllVerisEqual(all_ysk_no_veris):
                not_all_equal_veris.append(ysk_no)
        return JsonResponse({
            "Recomended To Check": {
                "All Veris Under This YSK Numbers": not_all_equal_veris,
                "All Images": tutanak_images,
            },
        })