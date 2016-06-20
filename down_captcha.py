import os
import re
import requests
import sys
import urlparse


def download_captcha(cap_fn):
    baseurl = 'https://flashbj.xzsec.com/'
    s = requests.session()
    r = s.get(os.path.join(baseurl, 'login.php?do=login&'), verify=False)
    m = re.search(r'<img src=".*?(text2png\.php.*?)"', r.text, re.M)
    capurl = os.path.join(baseurl, m.group(1))
    r = s.get(capurl, verify=False)
    session_id=s.cookies.get('PHPSESSID')
    params = urlparse.parse_qs(urlparse.urlsplit(capurl).query)
    with open(cap_fn, 'wb') as f:
        f.write(r.content)
    msg_fn = cap_fn + '.info'
    with open(msg_fn, 'w') as f:
        f.write('msg=%s\n' % params['msg'][0])
        f.write('sid=%s\n' % session_id)
    return params['msg'][0], session_id


def main(directory, num):
    for i in range(0, num):
        fn = os.path.join(directory, 'cap%03d.png' % i)
        msg, sid = download_captcha(fn)
        print 'captcha', fn, 'saved'
        print 'msg =', msg
        print 'sid =', sid
    print 'download complete'


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
