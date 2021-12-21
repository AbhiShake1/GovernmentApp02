import base64

import document_util

with open('../sample.jpg', 'rb') as f:
    b64string = base64.urlsafe_b64encode(f.read()).decode()
    print(b64string)
processed_image = document_util.get_cropped_document(b64string)
# cv2.imshow('test', processed_image_2)
# cv2.waitKey(0)
base64_pdf = document_util.stitch_images_to_pdf(processed_image, processed_image, processed_image)

with open('test.pdf', 'wb') as f:
    f.write(base64.b64decode(base64_pdf))
