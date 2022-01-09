import cv2
import glob
import numpy as np

file_type_png = 'png'
file_type_jpg = 'jpg'
type_jpeg = "jpeg"
type_jpg = "jpg"
type_png = "png"


def labeling(img):
    blur = cv2.GaussianBlur(img, ksize=(3, 3), sigmaX=0)
    ret, thresh1 = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)

    edged = cv2.Canny(blur, 10, 250)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    total = 0

    contours_xy = np.array(contours)
    contours_xy.shape

    x_min, x_max = 0, 0
    value = list()
    for i in range(len(contours_xy)):
        for j in range(len(contours_xy[i])):
            value.append(contours_xy[i][j][0][0])
            x_min = min(value)
            x_max = max(value)

    y_min, y_max = 0, 0
    value = list()
    for i in range(len(contours_xy)):
        for j in range(len(contours_xy[i])):
            value.append(contours_xy[i][j][0][1])
            y_min = min(value)
            y_max = max(value)

    x = x_min
    y = y_min
    w = x_max - x_min
    h = y_max - y_min

    img_trim = img_o[y:y + h, x:x + w]

    x_offset = int(size / 2 - w / 2)
    y_offset = int(size / 2 - h / 2)
    x_end = int(x_offset + w)
    y_end = int(y_offset + h)
    # cv2.imshow('test', img_trim)
    # cv2.waitKey(0)

    if x < 3:
        return x, y - 3, w + 6, h + 6

    if y < 3:
        return x - 3, y, w + 6, h + 6

    return x - 3, y - 3, w + 6, h + 6
    # background[y_offset:y_end, x_offset:x_end] = img_trim
    # return background


for filename in glob.glob('./images/*.' + type_jpg):
    img_o = cv2.imread(filename)
    img_g = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    size = img_o.shape[1]
    size_2 = int(size / 3)

    roi = img_o
    roi_90 = cv2.rotate(roi, cv2.ROTATE_90_CLOCKWISE)
    roi_180 = cv2.rotate(roi, cv2.ROTATE_180)
    roi_270 = cv2.rotate(roi, cv2.ROTATE_90_COUNTERCLOCKWISE)

    roi[size_2:size, size_2 * 2:size] = roi_90[size_2:size, size_2 * 2:size]
    roi[size_2:size, 0:size_2 * 2] = roi_180[size_2:size, 0:size_2 * 2]
    roi[0:size_2 * 2, 0:size_2] = roi_270[0:size_2 * 2, 0:size_2]

    if filename.find(type_jpeg):
        cv2.imwrite(filename.replace('./images', './augmentationImages').replace(type_jpeg, type_jpg), roi)
    elif filename.find(type_png):
        cv2.imwrite(filename.replace('./images', './augmentationImages').replace(type_png, type_jpg), roi)
    else:
        cv2.imwrite(filename.replace('./images', './augmentationImages'), roi)

for filename2 in glob.glob('./augmentationImages/*.' + file_type_jpg):
    img_o = cv2.imread(filename2)
    img_g = cv2.imread(filename2, cv2.IMREAD_GRAYSCALE)

    size = img_o.shape[1]
    size_2 = int(size / 3)

    img_s315 = img_g[0:size_2, 0:size_2]
    img_s0 = img_g[0:size_2, size_2:size_2 * 2]
    img_s45 = img_g[0:size_2, size_2 * 2:size]
    img_s270 = img_g[size_2:size_2 * 2, 0:size_2]
    img_s90 = img_g[size_2:size_2 * 2, size_2 * 2:size]
    img_s225 = img_g[size_2 * 2:size, 0:size_2]
    img_s180 = img_g[size_2 * 2:size, size_2:size_2 * 2]
    img_s135 = img_g[size_2 * 2:size, size_2 * 2:size]

    image_dict = {
        'fertile_315': img_g[0:size_2, 0:size_2],
        'fertile_0': img_g[0:size_2, size_2:size_2 * 2],
        'fertile_45': img_g[0:size_2, size_2 * 2:size],
        'fertile_270': img_g[size_2:size_2 * 2, 0:size_2],
        'fertile_90': img_g[size_2:size_2 * 2, size_2 * 2:size],
        'fertile_225': img_g[size_2 * 2:size, 0:size_2],
        'fertile_180': img_g[size_2 * 2:size, size_2:size_2 * 2],
        'fertile_135': img_g[size_2 * 2:size, size_2 * 2:size]
    }

    path = './image'
    bar = filename2.find('_')
    name = filename2.replace(file_type_jpg, "xml")
    labeled = filename2.replace('augmentationImages', 'labeledImages').split('_')
    builder = labeled[0] + '_' + labeled[1]  # ./labeledImaged/f21_01.png

    # cv2.imwrite(builder.replace(file_type_png, file_type_jpg), img_o)

    with open(builder.replace(file_type_jpg, 'xml').replace('labeledImages', 'xml'), 'w') as xml:
        xml.write('<annotation>\n\t<folder>라벨링</folder>\n\t'
                  '<filename>' + builder.replace("./labeledImages/", "") + '</filename>\n\t'
                                                                           '<size>\n\t\t<width>' + str(
            size) + '</width>\n\t\t<height>' + str(size) + '</height>\n\t\t'
                                                           '<depth>3</depth>\n\t</size>\n')
        for key, value in image_dict.items():

            min_x, min_y, width, height = labeling(value)

            if key == 'fertile_0' or key == 'fertile_180':
                min_x = min_x + size_2

            elif key == 'fertile_45' or key == 'fertile_90' or key == 'fertile_135':
                min_x = min_x + size_2 * 2

            if key == 'fertile_270' or key == 'fertile_90':
                min_y = min_y + size_2
            elif key == 'fertile_225' or key == 'fertile_180' or key == 'fertile_135':
                min_y = min_y + size_2 * 2

            xml.write('\t<object>\n\t\t<name>' + key + '</name>\n\t\t<difficult>0</difficult>\n\t\t<bndbox>\n\t\t\t' +
                      '<xmin>' + str(min_x) + '</xmin>\n\t\t\t'
                                              '<ymin>' + str(min_y) + '</ymin>\n\t\t\t'
                                                                      '<xmax>' + str(min_x + width) + '</xmax>\n\t\t\t'
                                                                                                      '<ymax>' + str(
                min_y + height) + '</ymax>\n\t\t'
                                  '</bndbox>\n\t</object>\n')
        xml.write('</annotation>')
        print(name)
