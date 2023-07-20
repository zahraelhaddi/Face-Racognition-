import cv2
import face_recognition
import os
import pickle
import csv

# add students images to Firebase
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


# import students images
ImagesFilepath = "images"
ImagesPathsList = os.listdir(ImagesFilepath)
imagesList = []
known_IDs = []
for path in ImagesPathsList:
    imagesList.append(cv2.imread(os.path.join(ImagesFilepath, path)))
    # IDs
    known_IDs.append(os.path.splitext(path)[0])

    # Get a reference to the Firebase Storage bucket (mine)
    bucket = storage.bucket()
    # fileName
    fileName = f"{ImagesFilepath}/{path}"

    # Create a blob object and upload the image file
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


list = []
for path in ImagesPathsList:
    hadaa = "C:/Users/LENOVO/Desktop/attendance_system_project/images/"
    hada = os.path.join(hadaa, path)
    list.append(hada)


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
# print(KnownEncodingsList)

print("encoding complete, encodingsList successfully filled")
# print(known_IDs)
# print(imagesList)
# print(ImagesPathsList)
# print(KnownEncodingsList)

# chaque encoding correspond à un ID
knownEncodingsWithKnownIDs = [KnownEncodingsList, known_IDs]


file = "encodings.csv"
with open(file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(knownEncodingsWithKnownIDs)

print("file saved")
# file = open("EncodeFile.p", 'wb')
print("Data written to CSV file successfully.")
# pickle.dump([KnownEncodingsList], file)
# file.close()
