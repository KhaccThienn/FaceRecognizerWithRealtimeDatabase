# Nhập các thư viện cần thiết
import cv2
import face_recognition
# ghi file nhi phan
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Tải tệp JSON khóa tài khoản dịch vụ để xác thực Firebase
cred = credentials.Certificate("serviceAccountKey.json")

# Khởi tạo ứng dụng Firebase với thông tin xác thực tài khoản dịch vụ, URL cơ sở dữ liệu và bucket lưu trữ
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a3edf-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-a3edf.appspot.com"
})

# Import hình ảnh sinh viên
folderPath = 'Images'
# Lấy danh sách các tệp trong thư mục
pathList = os.listdir(folderPath)
print(pathList)

# Khởi tạo danh sách lưu trữ hình ảnh và ID sinh viên
imgList = []
studentIds = []

# Duyệt qua từng tệp trong thư mục
for path in pathList:
    # Đọc và thêm hình ảnh vào danh sách imgList
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # Lấy tên tệp (không bao gồm phần mở rộng) và thêm vào danh sách studentIds
    studentIds.append(os.path.splitext(path)[0])

    # Đặt tên tệp đầy đủ
    fileName = f'{folderPath}/{path}'
    # Lấy bucket từ Firebase storage
    bucket = storage.bucket()
    # Tạo một blob từ bucket với tên tệp
    blob = bucket.blob(fileName)
    # Tải tệp lên Firebase storage
    blob.upload_from_filename(fileName)

# In danh sách ID sinh viên
print(studentIds)


# Hàm để tìm mã hóa các khuôn mặt trong danh sách hình ảnh
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # Chuyển đổi hình ảnh từ BGR sang RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Tìm mã hóa khuôn mặt và thêm vào danh sách encodeList
        # Dính Overfitting
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


# Bắt đầu quá trình mã hóa
print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
# Kết hợp danh sách mã hóa với ID sinh viên
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

if os.path.isfile("EncodeFile.p"):
    os.remove("EncodeFile.p")

# Lưu danh sách mã hóa và ID sinh viên vào tệp "EncodeFile.p" bằng cách sử dụng pickle
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

# In thông báo hoàn thành lưu tệp
print("File Saved")
