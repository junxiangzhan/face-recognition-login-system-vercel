import cv2
import os

class CutPics:

    def __init__(self, userName: str, cascadePath: str = 'data\\haarcascade_frontalface_alt2.xml') -> None:

        """
        參數:
            picName(str): 照片名稱
            userName(str): 使用者名稱，作為資料庫資料夾中影像檔案資料夾名稱
            cascadePath(str): 影像偵測建置資源檔，此處建議使用'haarcascade_frontalface_alt2.xml'(存於data資料夾下)
        """
        self.userName = userName
        self.cascadePath = cascadePath

        # facedata -> 存放截圖後照片的資料夾
        if not os.path.exists("facedata"):
            os.mkdir("facedata")


    def cut(self, images) -> bool:

        """
        功能: 照片截圖，用於訓練人臉辨識

        參數:
            picName(str): 圖像檔案名稱
            index(int): 同一位使用者拍攝的第[index]張照片

        回傳: 布林值(bool)，代表是否截圖成功
        """
        cascade = cv2.CascadeClassifier(self.cascadePath)
        
        if not os.path.exists('__temp__'):
            os.mkdir('__temp__')
            
        for image in images:
            image.save('__temp__\\temp')
            img = cv2.imread('__temp__\\temp')

            faces = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=3, minSize=(20,20))
            # 偵測找到多少人臉 -> 若是>1則回傳截圖失敗(False)，必須=1
            if len(faces) > 1:
                print("照片多於一張人像，必須為個人照")
                return False

            for (x, y, w, h) in faces:
                imageCrop = img[y:y+h,x:x+w]    # type: ignore # 裁切
                imageResize = cv2.resize(imageCrop, (160,160))  # 重製大小
                cv2.imwrite('facedata\\{}\\{}'.format(self.userName, image.filename), imageResize)  # 儲存影像
            
            # faces = face_cascade.detectMultiScale(img, scaleFactor=1.1,
            #                                       minNeighbors=3, minSize=(20,20))
            
            # # 偵測找到多少人臉 -> 若是>1則回傳截圖失敗(False)，必須=1
            # if len(faces) > 1:
            #     print("照片多於一張人像，必須為個人照")
            #     return False

            # x, y, w, h = faces[0]
            # filename = "facedata\\" + self.userName + "_" + str(index) + ".jpg"
            # imageCrop = img[y:y+h,x:x+w]
            # imageResize = cv2.resize(imageCrop, (160, 160))

            # cv2.imwrite(filename, imageResize)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return True