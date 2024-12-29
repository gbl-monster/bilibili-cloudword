import jieba
import wordcloud
import pandas as pd
import os


def generate_cloud_word(file_path, pic_name):
    file_ext = os.path.splitext(file_path)[1]
    if file_ext == '.txt':
        f = open(file_path, encoding='utf-8')
        text = f.read()
        f.close()

    else:
        data = pd.read_csv(file_path)
        text = ' '.join(data['Comments'])
        print(text)

    text_list = jieba.lcut(text)
    text_str = ' '.join(text_list)
    stop_words = {'大哭', '这个', '所以', '求网', '开网', '心心', '星星', '厨子', '出网', '力元君', 'www', 'nb', 'doge', 'call',
                  'copy', 'tv', 'up', 'source'}

    wc = wordcloud.WordCloud(
        width=800,
        height=600,
        background_color='white',
        prefer_horizontal=1,
        stopwords=stop_words,
        font_path='msyh.ttc',
        min_word_length=2,
        collocations=False
    )
    wc.generate(text_str)
    wc.to_file(pic_name)


generate_cloud_word('barrage.txt', 'cloudWord_barrage.png')
generate_cloud_word('hot_comments.txt', 'cloudWord_hot_comment.png')
generate_cloud_word('我在学校开了门《大学生生活常识课》_comments.csv', 'cloudWord_comment.png')
