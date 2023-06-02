### 半自動拍攝多張人臉實例 ###

import cv2
import os

def taking_photo():   
    # 若不存在則建立資料夾
    if not os.path.exists("photos"):    
        os.mkdir("photos")

    name = input("Enter your nickname: ")
    # 分類器資源檔目錄
    picPath = r'C:\\Python311\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml' 
    # 建立辨識物件
    face_cascade = cv2.CascadeClassifier(picPath)  
    cap = cv2.VideoCapture(0)   # 開啟攝影機
    num = 1     # 影像編號

    # 若攝影機開啟則執行
    while cap.isOpened():   
        # 讀取影像
        ret, img = cap.read()   
        # 使用辨識物件
        faces = face_cascade.detectMultiScale(img, scaleFactor=1.4, minNeighbors=3, minSize=(20,20))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)  # 藍色框住人臉
        cv2.imshow("Photo", img)    # 顯示影像

        if ret == True:     # 若影像讀取成功
            key = cv2.waitKey(200)  # 0.2秒檢查一次

            if key == ord('x') or key == ord('X'):  # 若是按下X或x
                imageCrop = img[y:y+h,x:x+w]    # type: ignore  # 裁剪
                imageResize = cv2.resize(imageCrop,(160,160))   # 重製大小
                faceName = "photos\\" + name + "_" + str(num) + ".jpg"  
                cv2.imwrite(faceName, imageResize)  # 儲存影像

                print(f"拍攝第 {num} 次人臉成功")  
                if num == 5: break  # 拍5張人臉後終止
                num += 1

    cap.release()   # 關閉攝影機
    cv2.destroyAllWindows()

taking_photo()