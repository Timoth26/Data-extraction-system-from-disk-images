import cv2
import easyocr

def ocr(image_path):

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    processed_image_path = "processed_image.jpg"
    cv2.imwrite(processed_image_path, thresh)

    reader = easyocr.Reader(['en', 'pl'])
    results = reader.readtext(processed_image_path)
    extracted_text = " ".join([result[1] for result in results])
    print(extracted_text)
    return extracted_text
