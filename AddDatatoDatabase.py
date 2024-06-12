# import firebase_admin từ firebase_admin
import firebase_admin

# Import credentials và db từ firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Tải tệp JSON account key
cred = credentials.Certificate("serviceAccountKey.json")

# Khởi tạo ứng dụng Firebase với thông tin xác thực tài khoản dịch vụ và URL cơ sở dữ liệu
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a3edf-default-rtdb.firebaseio.com/"
})

# Lấy tham chiếu đến node 'Peoples' trong Firebase Realtime Database
ref = db.reference('Peoples')

# Định nghĩa một dictionary tên là 'data' chứa thông tin về các người dùng khác nhau
data = {
    "B0000":
        {
            "name": "Charles Chung",
            "major": "Technical Teacher",
            "starting_year": 2017,
            "total_attendance": 0,
            "standing": "A",
            "year": 0,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "321654":
        {
            "name": "Murtaza Hassan",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "111011":
        {
            "name": "Le Khac Thien",
            "major": "Robotics",
            "starting_year": 2024,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "852741":
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 7,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

# Lặp qua từng cặp key-value trong dictionary 'data'
for key, value in data.items():
    # Đặt giá trị của node con được xác định bởi 'key' trong tham chiếu 'Peoples' thành 'value'
    ref.child(key).set(value)
