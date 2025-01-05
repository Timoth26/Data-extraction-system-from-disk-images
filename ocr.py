import cv2
import easyocr
import tempfile

def ocr(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as temp_file:
        temp_file_path = temp_file.name
        cv2.imwrite(temp_file_path, thresh)

        reader = easyocr.Reader(['en', 'pl'])
        results = reader.readtext(temp_file_path)

    extracted_text = " ".join([result[1] for result in results])
    print(extracted_text)
    return extracted_text
