
import hashlib
import os
import re
import time
import urllib.parse

import pandas as pd
import requests
from lxml import etree

HEADERS = {
    'cookie': "buvid3=AA7396C6-088C-8C00-18AC-C88F31F4BD1017896infoc; b_nut=1725155520; _uuid=D6DDC5A8-B6BE-4B5C-3D2E-9D10A557B72E190453infoc; rpdid=|(umu)uukuk|0J'u~klulYl)); DedeUserID=27016679; DedeUserID__ckMd5=01946fdfcfa3acc3; CURRENT_QUALITY=80; hit-dyn-v2=1; buvid_fp_plain=undefined; LIVE_BUVID=AUTO5017251639765419; header_theme_version=CLOSE; enable_web_push=DISABLE; buvid4=D49483D9-0FE0-525A-E3EC-CB577E47D0E817896-024090101-zWxTcBdGFLx%2F7x9zjhdYyA%3D%3D; CURRENT_BLACKGAP=0; PVID=1; fingerprint=7283ea4de3eac46236f5131625ab5b5b; buvid_fp=7283ea4de3eac46236f5131625ab5b5b; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzODY1MjYsImlhdCI6MTczNTEyNzI2NiwicGx0IjotMX0.HmoO-Xa2Hz2yrmNLIq03yEY0Xt8SzUbwPP76EHpgCpc; bili_ticket_expires=1735386466; SESSDATA=e040930b%2C1750679326%2C6c925%2Ac2CjCefckmb2bmhC7DWb5O3Ja1mdufySEkcT2SDtWL4xIc6BD6Urb9j3TOwIVYLefgL1ASVmRsajNHTUp1VGhuNklORXdFWnYwM2tweHFEY1lhUHBfQ2dLMGREVkg5YlhsdEZMX01iOThlRlgtVklGR3Z1cWtEQk1TU3ViYnROTEVNb2p3S0hNOExRIIEC; bili_jct=428f12425eb270e7e03185782ed32a8c; CURRENT_FNVAL=4048; b_lsid=269E7693_19408AD8AEE; browser_resolution=1707-791; sid=5et1pu0u; bp_t_offset_27016679=1015648092059336704",
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}


class CookieError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BilibiliCommentFetcher:
    """Fetches and stores Bilibili comments using the Bilibili API."""

    search_url = 'https://search.bilibili.com/all'
    comment_api = 'https://api.bilibili.com/x/v2/reply/wbi/main'
    a = 'ea1db124af3c7062474693fa704f4ff8'

    def __init__(self, title: str = None, video_url: str = None) -> None:
        self.title = title
        self.video_url = video_url

    def get_video_url(self) -> str:

        response = requests.get(
            self.search_url, params={'keyword': self.title}, headers=HEADERS
        )

        tree = etree.HTML(response.text)
        xpath = '//div[@class="bili-video-card__wrap __scale-wrap"]//a[@class=""]/@href'
        href = 'https:' + tree.xpath(xpath)[0]
        return href

    def get_title(self) -> str:

        response = requests.get(self.video_url, headers=HEADERS)

        tree = etree.HTML(response.text)
        xpath = '//title[@data-vue-meta="true"]/text()'
        title = tree.xpath(xpath)[0].split('_', maxsplit=1)[0]
        return title

    def get_oid(self) -> str:

        response = requests.get(self.video_url, headers=HEADERS)

        pat = re.compile(r'&oid=(\d+)')
        try:
            oid = pat.search(response.text).group(1)
        except AttributeError:
            raise CookieError('Cookie is invalid or expired, please reconfigure it.')
        return oid

    def get_w_rid(self, oid: str, pagination_str: str = '{"offset":""}') -> str:

        if pagination_str == '{"offset":""}':

            pagination_str = urllib.parse.quote(pagination_str)
            l = [
                'mode=3',
                f'oid={oid}',
                f'pagination_str={pagination_str}',
                'plat=1',
                'seek_rpid=',
                'type=1',
                'web_location=1315875',
                f'wts={time.time():.0f}',
            ]
        else:
            pagination_str = urllib.parse.quote(pagination_str)
            l = [
                'mode=3',
                f'oid={oid}',
                f'pagination_str={pagination_str}',
                'plat=1',
                'type=1',
                'web_location=1315875',
                f'wts={time.time():.0f}',
            ]

        y = '&'.join(l)
        data = y + self.a

        md5 = hashlib.md5()
        md5.update(data.encode('utf-8'))
        w_rid = md5.hexdigest()
        return w_rid

    def get_next_offset_and_comments_in_page_1(
        self, oid: str, w_rid: str
    ) -> tuple[str, list[dict[str, list[str]]]]:

        params = {
            'oid': f'{oid}',
            'type': '1',
            'mode': '3',
            'pagination_str': '{"offset":""}',
            'plat': '1',
            'seek_rpid': '',
            'web_location': '1315875',
            'w_rid': f'{w_rid}',
            'wts': f'{time.time():.0f}',
        }
        response = requests.get(self.comment_api, params=params, headers=HEADERS)

        data = response.json()
        next_offset = data['data']['cursor']['pagination_reply']['next_offset']

        comments = [
            {
                (
                    data['data']['replies'][i]['member']['uname'],
                    data['data']['replies'][i]['member']['sex'],
                    data['data']['replies'][i]['content']['message'],
                    data['data']['replies'][i]['like'],
                ): [
                    data['data']['replies'][i]['replies'][j]['content']['message']
                    for j in range(len(data['data']['replies'][i]['replies']))
                ]
            }
            for i in range(len(data['data']['replies']))
        ]

        return next_offset, comments

    def fetch_comments(
        self, oid: str, w_rid: str, pagination_str: str
    ) -> list[dict[str, list[str]]]:

        params = {
            'oid': f'{oid}',
            'type': '1',
            'mode': '3',
            'pagination_str': pagination_str,
            'plat': '1',
            'web_location': '1315875',
            'w_rid': f'{w_rid}',
            'wts': f'{time.time():.0f}',
        }
        response = requests.get(self.comment_api, params=params, headers=HEADERS)

        data = response.json()
        comments = [
            {
                (
                    data['data']['replies'][i]['member']['uname'],
                    data['data']['replies'][i]['member']['sex'],
                    data['data']['replies'][i]['content']['message'],
                    data['data']['replies'][i]['like'],
                ): [
                    data['data']['replies'][i]['replies'][j]['content']['message']
                    for j in range(len(data['data']['replies'][i]['replies']))
                ]
            }
            for i in range(len(data['data']['replies']))
        ]
        return comments


def main():
    path = os.path.dirname(__file__)
    os.chdir(path)

    title_or_link = input('Please input the title or the link of the video: ')
    try:
        requests.get(title_or_link)
        fetcher = BilibiliCommentFetcher(video_url=title_or_link)
    except:
        fetcher = BilibiliCommentFetcher(title=title_or_link)
        fetcher.video_url = fetcher.get_video_url()

    fetcher.title = fetcher.get_title()
    print(f'Video found: {fetcher.title}.')
    flag = input('Type in "y" to continue, "n" to exit: ')
    if flag == 'n':
        exit()

    oid = fetcher.get_oid()

    w_rid = fetcher.get_w_rid(oid=oid)

    next_offset, comments_page_1 = fetcher.get_next_offset_and_comments_in_page_1(
        oid=oid, w_rid=w_rid
    )
    total_comments = comments_page_1
    print(f'Page 1: {len(total_comments)} comments fetched.')

    next_offset = next_offset.replace('"', r'\"')
    pagination_str = f'{{"offset":"{next_offset}"}}'

    page = 2
    comments_ = None
    while True:
        w_rid = fetcher.get_w_rid(oid=oid, pagination_str=pagination_str)
        comments = fetcher.fetch_comments(
            oid=oid, w_rid=w_rid, pagination_str=pagination_str
        )
        if len(comments) == 0:
            break
        elif comments == comments_:
            raise CookieError('Cookie is invalid or expired, please reconfigure it.')
        else:
            total_comments.extend(comments)
            print(f'Page {page}: {len(comments)} comments fetched.')
            page += 1

        comments_ = comments
        time.sleep(0.1)

    total_comments = pd.concat(map(pd.Series, total_comments), axis=0)
    total_comments.explode().rename_axis(
        ['User Name', 'Sex', 'Comments', 'Likes']
    ).rename('Replies').to_csv(f'{fetcher.title}_comments.csv')


if __name__ == '__main__':
    main()
