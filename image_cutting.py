#encoding=utf-8
import tifffile
import cv2 as cv
import os
import argparse
import glob

def get_fixed_windows(image_size, wind_size, overlap_size):
    '''
    This function can generate overlapped windows given various image size
    params:
        image_size (w, h): the image width and height
        wind_size (w, h): the window width and height
        overlap (overlap_w, overlap_h): the overlap size contains x-axis and y-axis

    return:
        rects [(xmin, ymin, xmax, ymax)]: the windows in a list of rectangles
    '''
    rects = set()

    assert overlap_size[0] < wind_size[0]
    assert overlap_size[1] < wind_size[1]

    im_w = wind_size[0] if image_size[0] < wind_size[0] else image_size[0]
    im_h = wind_size[1] if image_size[1] < wind_size[1] else image_size[1]

    stride_w = wind_size[0] - overlap_size[0]
    stride_h = wind_size[1] - overlap_size[1]

    for j in range(wind_size[1]-1, im_h + stride_h, stride_h):
        for i in range(wind_size[0]-1, im_w + stride_w, stride_w):
            right, down = i+1, j+1
            right = right if right < im_w else im_w
            down  =  down if down < im_h  else im_h

            left = right - wind_size[0]
            up   = down  - wind_size[1]

            rect_ = [left, up, right, down]
            print(rect_)
            rects.add((left, up, right, down))

    return list(rects)


def cutting(save_dir, path, num, is_source_domain=True):
    img = tifffile.imread(path)
    if is_source_domain:
        img = cv.pyrDown(img, dstsize=(img.shape[0] // 2, img.shape[1] // 2))
    image_size = (img.shape[0], img.shape[1])
    wind_size = (256, 256)
    overlap_size = (128, 128)
    # img = Image.fromarray(img)
    rets = get_fixed_windows(image_size, wind_size, overlap_size)
    i = len(rets) * num
    for rect in rets:
        # print(rect)
        img_crop = img[rect[0]:rect[2], rect[1]:rect[3]]
        # img_crop = img.crop(rect)
        if is_source_domain:
            save_path = os.path.join(save_dir+'A', "%d.png" % i)
        else:
            save_path = os.path.join(save_dir+'B', "%d.png" % i)
        tifffile.imwrite(save_path, img_crop)
        # img_crop.save(save_path, format='PNG', subsampling=0, quality=100)
        if i % (len(rets) // 10) == 0:
            print("%d / %d: last image saved at %s, " % (i, len(rets)*(num+1), save_path))
        i = i + 1

def process_datasets(Vahingen_dir, Potsdom_dir, output_dir, phase):
    save_phase = 'test' if phase == 'val' else 'train'
    savedir = os.path.join(output_dir, save_phase)
    os.makedirs(savedir, exist_ok=True)
    os.makedirs(savedir + 'A', exist_ok=True)
    os.makedirs(savedir + 'B', exist_ok=True)
    print("Directory structure prepared at %s" % output_dir)

    target_domain_path_expr = os.path.join(Vahingen_dir, phase) + "/*.tif"
    target_domain_paths = glob.glob(target_domain_path_expr)
    target_domain_paths = sorted(target_domain_paths)
    for num, target_domain_path in enumerate(target_domain_paths):
        cutting(savedir, target_domain_path, num, is_source_domain=False)

    source_domain_expr = os.path.join(Potsdom_dir, phase) + "/*_IRRG.tif"
    source_domain_paths = glob.glob(source_domain_expr)
    source_domain_paths = sorted(source_domain_paths)
    for num, source_domain_path in enumerate(source_domain_paths):
        cutting(savedir, source_domain_path, num, is_source_domain=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--Vahingen_dir', type=str, required=False,
                        default='F:\?????????\ISPRS2D_Potsdam_Vahingen\Vahingen',
                        help='Path to the ISPRS2D Vahingen directory.')
    parser.add_argument('--Potsdom_dir', type=str, required=False,
                        default='F:\?????????\ISPRS2D_Potsdam_Vahingen\Potsdam',
                        help='Path to the ISPRS2D Potsdom directory.')
    parser.add_argument('--output_dir', type=str, required=False,
                        default='./datasets/Potsdam_Vahingen/',
                        help='Directory the output images will be written to.')
    opt = parser.parse_args()
    print('Preparing Potsdom_Vahingen Dataset for val phase')
    process_datasets(opt.Vahingen_dir, opt.Potsdom_dir, opt.output_dir, "val")
    print('Preparing Potsdom_Vahingen Dataset for train phase')
    process_datasets(opt.Vahingen_dir, opt.Potsdom_dir, opt.output_dir, "train")

    print('Done')

'''
# output
(0, 0, 800, 600)
(500, 0, 1300, 600)
(980, 0, 1780, 600)
'''