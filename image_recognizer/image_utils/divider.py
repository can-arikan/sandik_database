import cv2

from image_recognizer.image_utils.scanner import warper


def barcodeDivide(img):
    detector=cv2.SIFT_create()
    MIN_MATCH_COUNT=20
    dicto = {}
    dicto.setdefault('na',[])
    kp_des_query = []
    kp_des_train = []
    coll_train = []
    tmp = warper('./image_recognizer/image_utils/template/barcode', 
                 './image_recognizer/image_utils/template/barcode/*.png', img, detector, 
               MIN_MATCH_COUNT, dicto, 
               kp_des_query, kp_des_train, 
               coll_train)
    cv2.destroyAllWindows()
    return tmp

def rtDivide(img):
    detector=cv2.SIFT_create()
    MIN_MATCH_COUNT=10
    dicto = {}
    dicto.setdefault('na',[])
    kp_des_query = []
    kp_des_train = []
    coll_train = []
    tmp = warper('./image_recognizer/image_utils/template/rt',
                 './image_recognizer/image_utils/template/rt/*.png', img, detector, 
               MIN_MATCH_COUNT, dicto, 
               kp_des_query, kp_des_train, 
               coll_train)
    cv2.destroyAllWindows()
    return tmp

def kkDivide(img):
    detector=cv2.SIFT_create(contrastThreshold=0.025)
    MIN_MATCH_COUNT=10
    dicto = {}
    dicto.setdefault('na',[])
    kp_des_query = []
    kp_des_train = []
    coll_train = []
    tmp = warper('./image_recognizer/image_utils/template/kk',
                 './image_recognizer/image_utils/template/kk/*.png', img, detector, 
               MIN_MATCH_COUNT, dicto, 
               kp_des_query, kp_des_train, 
               coll_train)
    cv2.destroyAllWindows()
    return tmp

def divider(img):
    img1 = img
    img2 = img
    img3 = img
    return barcodeDivide(img1), kkDivide(img2), rtDivide(img3)