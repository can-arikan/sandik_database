import cv2
import numpy as np
import os
from skimage.io import imread_collection
from .transform import perspective_transform

def kp_des(img, coll_train, detector, kp_des_query, kp_des_train):
    kp_query, des_query = detector.detectAndCompute(img,None)
    kp_des_query.append((kp_query, des_query))
     
    for img in coll_train:
        try:
            img_train = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except:
            img_train = img
        kp_train, des_train = detector.detectAndCompute(img_train,None)
        kp_des_train.append((kp_train, des_train))
    
    return(kp_des_query, kp_des_train)

def find_matches(des_query, des_train, kp1, kp2):
    key_matches = 0
    
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 10)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    if(len(kp1)>=2 and len(kp2)>=2):
        matches = flann.knnMatch(des_query, des_train, k=2)
    
    matchesMask = [[0,0] for i in range(len(matches))]
    
    for i,(m,n) in enumerate(matches):
        if m.distance < 0.7*n.distance:
            matchesMask[i]=[1,0]
            key_matches = key_matches + 1
            
    return(key_matches, matches)

def temp_query_match(
        coll_train, img, kp_des_train, 
        kp_des_query, train_name,
        dicto, MIN_MATCH_COUNT,
        erase_writings: bool = False
):
    warped_image = None
    for i,template in enumerate(coll_train):
        if (train_name[i] == 'INSERT IMAGE NAMES THAT DOES NOT HAVE MANY FEATURES OR TOO SMALL'):
            dicto['na'].append((train_name[i],[]))
            continue
        
        try:
            trainImg = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        except:
            trainImg = template
            
        QueryImgBGR = img

        if erase_writings: ""

        key_matches, matches = find_matches(kp_des_query[0][1], kp_des_train[i][1], kp_des_query[0][0], kp_des_train[i][0])
        if matches == 0:
            dicto['na'].append((train_name[i],[]))
            continue
            
        if key_matches > 40:
            goodMatch=[]
            for m,n in matches:
                if(m.distance<0.55*n.distance):
                    goodMatch.append(m)
            
            if(len(goodMatch)>MIN_MATCH_COUNT):
                tp=[]
                qp=[]
                for m in goodMatch:
                    tp.append(kp_des_train[i][0][m.trainIdx].pt)
                    qp.append(kp_des_query[0][0][m.queryIdx].pt)
                tp,qp=np.float32((tp,qp))
                H,status=cv2.findHomography(tp,qp,cv2.RANSAC,3.0)

                h,w=trainImg.shape
                trainBorder=np.float32([[[0,0],[0,h-1],[w-1,h-1],[w-1,0]]])
                if  H is not None:
                    queryBorder=cv2.perspectiveTransform(trainBorder,H)
                    warped_image = perspective_transform(QueryImgBGR, queryBorder.reshape(4, 2))
                    try:
                        warped_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
                    except: ""
    return warped_image

def load_images_from_folder(folder):
    name = []
    for filename in os.listdir(folder):
        name.append(filename)
    return name

def warper(train_names, coll_trains, img, detector, MIN_MATCH_COUNT, dicto, kp_des_query, kp_des_train, coll_train):
    train_name = load_images_from_folder(train_names)
    coll_train = imread_collection(coll_trains)
    if type(img) != type(np.array([])):
        open_cv_image = np.array(img)
        img = open_cv_image[:, :, ::-1].copy()
    kp_des_query, kp_des_train = kp_des(img, coll_train, 
                                        detector, kp_des_query,
                                        kp_des_train)
    return temp_query_match(coll_train, img, 
                             kp_des_train, kp_des_query, 
                             train_name,
                             dicto, MIN_MATCH_COUNT)

def warpImage(img):
    detector=cv2.SIFT_create()
    MIN_MATCH_COUNT=60
    dicto = {}
    dicto.setdefault('na',[])
    kp_des_query = []
    kp_des_train = []
    coll_train = []
    tmp = warper('./image_recognizer/image_utils/template/base', './image_recognizer/image_utils/template/base/*.png', img, detector, 
               MIN_MATCH_COUNT, dicto, 
               kp_des_query, kp_des_train, 
               coll_train)
    cv2.destroyAllWindows()
    return tmp