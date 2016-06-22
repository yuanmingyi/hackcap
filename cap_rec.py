import numpy as np
import os
from PIL import Image


def bilevel(im):
    if im.mode != 'L':
        im = im.convert('L')
    data = np.asarray(im)
    bi_data = (data < data.mean()) * 255
    return bi_data


def reshape(im, shape):
    return im.resize(shape, Image.ANTIALIAS)


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


def split_connect(data, points_threshold=10, expected_width=8):
    nrow, ncol = data.shape
    spans = []
    mask = np.uint8(data > 0)
    connect = (mask[:, :-1] & mask[:, 1:]).any(0)
    start = 0
    for i in range(0, ncol - 1):
        if not connect[i]:
            parts = int(round(float(i + 1 - start) / expected_width))
            if parts < 1:
                parts = 1
            width = (i + 1 - start) / parts
            while start + 2 * width <= i + 1:
                spans.append(range(start, start + width))
                start += width
            spans.append(range(start, i + 1))
            start = i + 1
    spans.append(range(start, ncol))
    results = []
    for i in range(0, len(spans)):
        if data[:, spans[i]].sum() > points_threshold:
            results.append(data[:, spans[i]])
    return results


def split_and_save(fn, resize, directory='.', points_threshold=10, expected_width=8):
    im = Image.open(fn)
    bi_data = bilevel(im)
    split_data = split_connect(bi_data, points_threshold, expected_width)
    basename = os.path.basename(fn)
    file_names = []
    for i in range(0, len(split_data)):
        out_path = os.path.join(directory, '%s_%d.png' % (basename[:basename.rindex('.')], i))
        im = Image.fromarray(np.uint8(split_data[i]))
        im = im.resize(resize, Image.ANTIALIAS)
        im.save(out_path)
        file_names.append(os.path.basename(out_path))
    return file_names


def split_captcha_samples(in_dir, out_dir, list_name):
    files = os.listdir(in_dir)
    sample_list = []
    for fn in files:
        if not fn.endswith('.png'):
            continue
        file_path = os.path.join(in_dir, fn)
        print 'start to split', file_path
        sample_list.extend(split_and_save(file_path, (8, 16), out_dir))
    sample_list_file = os.path.join(out_dir, list_name)
    with open(sample_list_file, 'w') as f:
        f.writelines([fn + ',\n' for fn in sample_list])


def get_feature(data):
    return data.reshape(1, -1)


def load_data(data_dir, label_file):
    label_path = os.path.join(data_dir, label_file)
    data = None
    labels = []
    with open(label_path, 'r') as f:
        for line in f.readlines():
            tokens = line.split(',')
            if len(tokens) != 2:
                print 'invalid line:', line
                continue
            filename = tokens[0].strip()
            label = tokens[1].strip()
            file_path = os.path.join(data_dir, filename)
            try:
                im = Image.open(file_path)
            except:
                print 'cannot open image:', file_path
                continue
            img_data = np.asarray(im)
            feature = get_feature(img_data)
            if data is None:
                data = feature
            else:
                data = np.vstack(data, feature)
            labels.append(label)
    return labels, data


def train_model(data, labels):
    pass
