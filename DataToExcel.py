import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, storage
import pandas as pd
import openpyxl

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

data = db.reference(f"Students").get()
# for key, value in data.items():
# print(value["Major"])

df = pd.DataFrame(data.values())

df["last_attendance_time"] = pd.to_datetime(df["last_attendance_time"])
grouped_data = df.groupby("last_attendance_time")
df_grouped_Data = pd.DataFrame(grouped_data)
# print(df_grouped_Data)

with pd.ExcelWriter("attendance_data.xlsx") as writer:
    for group_name, group_df in grouped_data:
        group_df.to_excel(writer, sheet_name=str(group_name.date()), index=False)
