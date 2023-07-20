import numpy as np
import cv2
import os
import csv
import pickle
import face_recognition
import cvzone
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, storage

cred = credentials.Certificate(
    "C:/Users/LENOVO/Desktop/face-recognition-db-ebab4-firebase-adminsdk-2me33-da6fd6949f.json"
)
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://face-recognition-db-ebab4-default-rtdb.firebaseio.com",
        "storageBucket": "face-recognition-db-ebab4.appspot.com",
    },
)


cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imageBackground = cv2.imread("Resources/background.png")

# import mode images to a list so that using them becomes easier
ModesFolderPath = "Resources/Modes"
ModesPathsList = os.listdir(ModesFolderPath)
imgModeList = []
for path in ModesPathsList:
    imgModeList.append(cv2.imread(os.path.join(ModesFolderPath, path)))


# using pickle the loading is done this way
# file=open("encodings.p","rb")
# knownEncodingsWithKnownIDs=pickle.load(file)
# file.close()

# load the encodings file
with open("encodings.csv", "r") as encodings_file:
    reader = csv.reader(encodings_file)
    knownEncodingsWithKnownIDs = list(reader)

print("encodings loaded successfully")

ImagesFilepath = "images"
ImagesPathsList = os.listdir(ImagesFilepath)
imagesList = []
known_IDs = []
for path in ImagesPathsList:
    imagesList.append(cv2.imread(os.path.join(ImagesFilepath, path)))
    # IDs
    known_IDs.append(os.path.splitext(path)[0])


# encoding student imported images
KnownEncodingsList = []


def findEncodings(imagList):
    encodeList = []
    for img in imagList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started ...")
KnownEncodingsList = findEncodings(imagesList)
# print(KnownEncodingsList)  # print(knownEncodingsWithKnownIDs[0])


mode_type = 0
i = 0
imgStudent = []

while True:
    ret, frame = cap.read()

    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    currentFaceLocation = face_recognition.face_locations(imgS)
    currentFaceEncoding = face_recognition.face_encodings(imgS, currentFaceLocation)

    imageBackground[162 : 162 + 480, 55 : 55 + 640] = frame
    imageBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
        mode_type
    ]  # meaning that the imgModeList is a dynamic type because it has the changing value of mode_type

    if currentFaceLocation:
        for encodeface, locface in zip(currentFaceEncoding, currentFaceLocation):
            matches = face_recognition.compare_faces(KnownEncodingsList, encodeface)
            faceDist = face_recognition.face_distance(KnownEncodingsList, encodeface)
            # print("matches", matches)
            # print("faceDist", faceDist)
            matchIndex = np.argmin(faceDist)
            # print(known_IDs[matchIndex])
            # print("matchindex", matchIndex)

            y1, x2, y2, x1 = locface
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            cv2.rectangle(
                imageBackground,
                (bbox[0], bbox[1]),
                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                (0, 255, 0),
                2,
            )

            if matches[matchIndex]:
                # print("Known Face Detected")
                id = known_IDs[matchIndex]

                # print(id)
                if i == 0:
                    # these two lines (line1 and line2) are just because the processing of the capture is too slow we add the "loading" thing just to seem like it is just loading not slow
                    # but in fact it is still slow
                    # the solution is to use Asyncronous functions but i did not use them
                    cvzone.putTextRect(imageBackground, "loading", (275, 400))  # line1
                    cv2.imshow("Face Recognition", imageBackground)  # line2
                    cv2.waitKey(1)
                    i = 1
                    mode_type = 1

        if i != 0:
            if i == 1:
                data = db.reference(f"Students/{id}").get()
                # print(data)

                # get the image from the firebase database storage
                bucket = storage.bucket()
                blob = bucket.get_blob(f"images/{id}.png")
                array = np.frombuffer(blob.download_as_string(), dtype=np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # uPDATE total attendance meaning as long as i am captured the total attendance increments with 1
                datetimeObject = datetime.strptime(
                    data["last_attendance_time"], "%Y-%m-%d %H:%M:%S"
                )
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                if secondsElapsed > 30:
                    ref = db.reference(f"Students/{id}")
                    data["total_attendance"] += 1
                    ref.child("total_attendance").set(data["total_attendance"])
                    ref.child("last_attendance_time").set(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                else:
                    mode_type = 3
                    i = 0
                    imageBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                        mode_type
                    ]
            if mode_type != 3:
                if 10 < i < 20:
                    mode_type = 2
                imageBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[mode_type]
                if i <= 10:
                    cv2.putText(
                        imageBackground,
                        str(data["total_attendance"]),
                        (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1,
                    )
                    cv2.putText(
                        imageBackground,
                        str(data["Major"]),
                        (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1,
                    )
                    cv2.putText(
                        imageBackground,
                        str(id),
                        (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (255, 255, 255),
                        1,
                    )
                    cv2.putText(
                        imageBackground,
                        str(data["standing"]),
                        (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (100, 100, 100),
                        1,
                    )
                    cv2.putText(
                        imageBackground,
                        str(data["year"]),
                        (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (100, 100, 100),
                        1,
                    )
                    cv2.putText(
                        imageBackground,
                        str(data["Starting_year"]),
                        (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (100, 100, 100),
                        1,
                    )
                    (w, h), _ = cv2.getTextSize(
                        data["name"], cv2.FONT_HERSHEY_COMPLEX, 1, 1
                    )
                    offset = (414 - w) // 2  # this is for centering the name
                    cv2.putText(
                        imageBackground,
                        str(data["name"]),
                        (808 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX,
                        1,
                        (100, 100, 100),
                        1,
                    )

                    imageBackground[175 : 175 + 216, 909 : 909 + 216] = imgStudent
                i += 1

                if i >= 20:
                    i = 0
                    mode_type = 0
                    data = []
                    imgStudent = []
                    imageBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                        mode_type
                    ]

    else:
        mode_type = 0
        i = 0
    # cv2.imshow("webcam", frame)
    cv2.imshow("Face Recognition", imageBackground)
    cv2.waitKey(1)  # 1millisecond
