import document_util
import cv2

processed_image = document_util.get_cropped_document('../sample.jpg')
processed_image_2 = document_util.get_cropped_document('../sample2.jpg')
# cv2.imshow('test', processed_image_2)
# cv2.waitKey(0)
stitched_image = document_util.stitch_images(processed_image, processed_image_2, processed_image_2)
stitched_image.save('stitched_image.jpg', 'JPEG')
stitched_image.show()
