import cv2
import boto3
import io
from PIL import Image
import datetime

# Initialize AWS clients
rekognition = boto3.client('rekognition', region_name='ap-south-1')
dynamodb = boto3.client('dynamodb', region_name='ap-south-1')

def capture_image_with_face_detection():
    # The capture_image_with_face_detection function remains unchanged.
    # Add the code for face detection and image capture here.
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Python webcam Face Detection")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            # Save the detected face to an image file
            img_name = "Opencv_frame.png"
            cv2.imwrite(img_name, frame)
            print("Face captured")

        cv2.imshow("Face Detection", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape Hit")
            break

    cam.release()
    cv2.destroyAllWindows()

    return img_name
def recognize_faces(image_path):
    image = Image.open(image_path)
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    image_binary = stream.getvalue()

    response = rekognition.search_faces_by_image(
        CollectionId='studentsimg',
        Image={'Bytes': image_binary}
    )

    found = False

    for match in response['FaceMatches']:
        print(match['Face']['FaceId'], match['Face']['Confidence'])

        face = dynamodb.get_item(
            TableName='students_data',
            Key={'RekognitionId': {'S': match['Face']['FaceId']}}
        )

        if 'Item' in face:
            full_name = face['Item']['FullName']['S']
            rekognition_id = face['Item']['RekognitionId']['S']  # Assuming this attribute exists
            email = face['Item'].get('Email', {}).get('S', '')  # Fetch the 'Email' attribute from the DynamoDB table

            print("Found Person: ", full_name)
            found = True

            # Update or Create the item in DynamoDB with the date and present status
            update_dynamodb(full_name, rekognition_id, email)

    if not found:
        print("Person cannot be recognized")

def update_dynamodb(full_name, rekognition_id, email):
    current_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Prepare the item attributes for the 'Present' and 'Date' columns
    item = {
        'RekognitionId': {'S': rekognition_id},  # Use RekognitionId as the key
        'FullName': {'S': full_name},           # Use full_name for FullName column
        'Present': {'S': 'Yes'},
        'Date': {'S': current_date}
    }

    # Check if the email is not None
    if email is not None:
        item['Email'] = {'S': email}  # Include 'Email' attribute in the 'item' dictionary

    # Use the put_item function to create or update the item in the DynamoDB table
    response = dynamodb.put_item(
        TableName='students_data',
        Item=item
    )
    print(full_name + ", " + "Your attendance is taken successfully.\n Thank you!!\n")
    print("DynamoDB updated successfully!")

if __name__ == "__main__":
    # Capture the image with face detection
    captured_image_path = capture_image_with_face_detection()

    # Recognize faces in the captured image and update DynamoDB
    recognize_faces(captured_image_path)
