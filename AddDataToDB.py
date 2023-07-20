import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(
    "C:/Users/LENOVO/Desktop/face-recognition-db-ebab4-firebase-adminsdk-2me33-da6fd6949f.json"
)
firebase_admin.initialize_app(
    cred,
    {"databaseURL": "https://face-recognition-db-ebab4-default-rtdb.firebaseio.com"},
)

ref = db.reference("Students")
data = {
    "123": {
        "name": "Zakir Naik",
        "Major": "Daawa",
        "Starting_year": 2020,
        "total_attendance": 6,
        "standing": "E",
        "year": 4,
        "last_attendance_time": "2023-07-10 00:54:34",
    },
    "345": {
        "name": "AL Khawarizmi",
        "Major": "Maths & Algorithms",
        "Starting_year": 2019,
        "total_attendance": 5,
        "standing": "E",
        "year": 3,
        "last_attendance_time": "2023-07-10 00:54:34",
    },
    "567": {
        "name": "elon musk",
        "Major": "cars",
        "Starting_year": 2020,
        "total_attendance": 3,
        "standing": "G",
        "year": 3,
        "last_attendance_time": "2023-07-10 00:54:34",
    },
}
# push data to the database using set method of reference object and pass dictionary as argument
for (
    key,
    value,
) in (
    data.items()
):  # derna .items() 7it 7na khdamin b dictionnaire 7it mni kankhdmo b key value pair w value tahia key value pairs idan fa rah had l value 3ibara 3an dictionnaire
    ref.child(key).set(
        value
    )  # we use "child" because we want to send data to a specific node which is "students"
