# Nhập các thư viện cần thiết
import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

# Khởi tạo Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a3edf-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-a3edf.appspot.com"
})

bucket = storage.bucket()

# Khởi động camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Đặt chiều rộng khung hình
cap.set(4, 480)  # Đặt chiều cao khung hình

# Đọc ảnh nền
imgBackground = cv2.imread('Resources/background.png')

# Nhập các ảnh chế độ vào danh sách
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Tải tệp mã hóa
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    img = cv2.flip(img, 1)

    # Thu nhỏ hình ảnh để xử lý nhanh hơn
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Tìm vị trí khuôn mặt hiện tại và mã hóa khuôn mặt (mô hình hog)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Đặt hình ảnh camera lên nền
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[1]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            # So sánh mã hóa khuôn mặt với các mã hóa đã biết
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            
            matchIndex = np.argmin(faceDis)

            print(matches[matchIndex])

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Phóng to lại kích thước ban đầu
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1  # Tạo hộp bao quanh khuôn mặt
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)  # Vẽ hộp bao quanh khuôn mặt
                id = studentIds[matchIndex]
                print(f"ID: {id}")
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    # cv2.waitKey(1)
                    counter = 1

                if counter == 1:
                    # Lấy dữ liệu sinh viên từ cơ sở dữ liệu
                    studentInfo = db.reference(f'Peoples/{id}').get()
                    print(studentInfo)
                    # Lấy hình ảnh từ bộ lưu trữ
                    blob = bucket.get_blob(f'Images/{id}.png')

                    if blob is None:
                        print(f"Lỗi: Blob 'Images/{id}.png' không tồn tại trong bucket.")
                        counter = 0
                        continue

                    try:
                        blob_str = blob.download_as_string()
                        #  Chuyển đổi chuỗi byte đó thành một mảng numpy với kiểu dữ liệu np.uint8
                        array = np.frombuffer(blob_str, np.uint8)
                        # Giải mã mảng numpy thành một hình ảnh màu sử dụng OpenCV.
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    except Exception as e:
                        print(f"Một lỗi xảy ra khi xử lý hình ảnh: {e}")
                        counter = 0
                        continue

                    # Thay đổi kích thước imgStudent để phù hợp với không gian 216x216
                    imgStudent = cv2.resize(imgStudent, (216, 216))

                    # Cập nhật dữ liệu điểm danh
                    ref = db.reference(f'Peoples/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    studentInfo['year'] = datetime.now().year - studentInfo['starting_year']
                    ref.child('year').set(studentInfo['year'])

                    # Hiển thị thông tin sinh viên lên nền
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
            else:
                counter = 0
                id = -1
                imgStudent = []
                cv2.putText(imgBackground, "Unknown", (880, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

    # Hiển thị hình ảnh điểm danh
    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng camera và đóng cửa sổ
cap.release()
cv2.destroyAllWindows()
