import cv2
from os import mkdir, listdir
from os.path import join as resolve, exists as is_exists, isdir as is_dir
import glob
import numpy as np
import json

USER_PICS_DIR = 'user_data'
USERS_NAMES = resolve(USER_PICS_DIR, 'people.txt')
USERS_DB = resolve(USER_PICS_DIR, 'deepmind.yml')


class Database:

    def __init__(self, sourcePath: str) -> None:
        self.sourcePath = sourcePath    # 資源路徑檔
        self.cascade = cv2.CascadeClassifier(self.sourcePath)  # 建立識別檔案物件

    def saveImages(self, username: str, images) -> None:
        # 若資料夾不存在則建立
        if not is_exists(USER_PICS_DIR):
            mkdir(USER_PICS_DIR)

        # 確認是否建立過該人臉資料
        if not is_exists(resolve(USER_PICS_DIR, username)):
            mkdir(resolve(USER_PICS_DIR, username))     # 建立資料夾

        for image in images:
            img = np.frombuffer(image.stream.read(), np.uint8)   # 讀取影像
            faces = self.cascade.detectMultiScale(
                img, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
            print(faces)

            for (x, y, w, h) in faces:
                imageCrop = img[y:y+h, x:x+w]    # type: ignore # 裁切
                imageResize = cv2.resize(imageCrop, (160, 160))  # 重製大小
                faceName = resolve(USER_PICS_DIR, username, image.filename)
                cv2.imwrite(faceName, imageResize)  # 儲存影像

    def buildDB(self) -> None:
        """
        功能: 讀取人臉樣本並放入faces_db，建立標籤與人名串列
        回傳: None
        """
        nameList = []  # 員工姓名
        faces_db = []  # 儲存所有人臉
        labels = []   # 建立人臉標籤
        index = 0     # 員工編號索引

        try:
            # 讀取pics資料夾中的每個影像資料夾
            for dir_name in listdir(USER_PICS_DIR):
                if is_dir(resolve(USER_PICS_DIR, dir_name)):
                    faces = glob.glob(
                        resolve(USER_PICS_DIR, dir_name, "*.jpg"))  # 資料夾中所有影像檔案

                    for face in faces:
                        img = cv2.imread(face, cv2.IMREAD_GRAYSCALE)
                        faces_db.append(img)
                        labels.append(index)

                    nameList.append(dir_name)

                    index += 1

            with open(USERS_NAMES, "w+") as f:
                json.dump(nameList, f)

            # 建立LBPH人臉辨識物件
            model = cv2.face.LBPHFaceRecognizer_create()
            model.train(faces_db, np.array(labels))
            model.save(USERS_DB)

        except Exception as e:
            print(e)

    def login(self, username: str, image) -> bool:
        # 建立LBPH人臉辨識物件，並讀取已訓練數據
        model = cv2.face.LBPHFaceRecognizer_create()
        model.read(USERS_DB)

        # 獲取名稱標籤
        names = []
        with open(USERS_NAMES, 'r') as f:
            names = json.load(f)

        img = image.stream.read()
        faces = self.cascade.detectMultiScale(
            img, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)  # 框住人臉

        imageCrop = img[y:y+h, x:x+w]
        imageResize = cv2.resize(imageCrop, (160, 160))

        score = model.predict(imageResize)
        return score[1] < 50 and names[score[0]] == username
