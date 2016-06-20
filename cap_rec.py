import numpy as np
import os
from PIL import Image


def bilevel(im):
    if im.mode != 'L':
        im = im.convert('L')
    data = np.asarray(im)
    bi_data = (data < data.mean()) * 255
    return bi_data


def split(data, part=4):
    nrow, ncol = data.shape
    sub_ncol = ncol / part
    results = []
    for left in range(0, ncol - sub_ncol + 1, sub_ncol):
        sub_data = data[:, left:left+sub_ncol]
        center = calc_center(sub_data)
        bias = int(center - (sub_ncol - 1.0) / 2.0)
        if bias != 0:
            sub_data = data[:, left + bias: left + sub_ncol + bias]
        results.append(sub_data)
    return results


def calc_center(arr):
    rind, cind = np.where(arr > 0)
    qpoints = arr[rind, cind]
    return np.dot(cind, qpoints)/qpoints.sum()


def split_connect(data, points_threshold=10):
    nrow, ncol = data.shape
    spans = []
    mask = np.uint8(data > 0)
    connect = (mask[:, :-1] & mask[:, 1:]).any(0)
    start = 0
    for i in range(0, ncol - 1):
        if not connect[i]:
            spans.append(range(start, i + 1))
            start = i + 1
    spans.append(range(start, ncol))
    results = []
    for i in range(0, len(spans)):
        if data[:, spans[i]].sum() > points_threshold:
            results.append(data[:, spans[i]])
    return results


def split_and_save(fn, directory='.'):
    im = Image.open(fn)
    bi_data = bilevel(im)
    split_data = split_connect(bi_data)
    basename = os.path.basename(fn)
    for i in range(0, len(split_data)):
        out_path = os.path.join(directory, '%s_%d.png' % (basename[:basename.rindex('.')], i))
        im = Image.fromarray(np.uint8(split_data[i]))
        im.save(out_path)


def split_captcha_samples(in_dir, out_dir):
    files = os.listdir(in_dir)
    for fn in files:
        if not fn.endswith('.png'):
            continue
        file_path = os.path.join(in_dir, fn)
        print 'start to split', file_path
        split_and_save(file_path, out_dir)
