'''
manual operation
'''

import os, sys
import requests
from app import db, app
from app.models import Stats, Post


def update_post_total():
    stats_post = Stats.query.filter_by(name='post_count').first()
    if not stats_post:
        post_count = Stats(name='post_count')
        db.session.add(post_count)
        db.session.commit()
    else:
        stats_post.total = Post.query.count()
        db.session.commit()
        print('The number of total posts is updated to:', stats_post.total)

def create_triggers():
    custom_triggers = ['count_up', 'count_down']#up must be first,down  be down
    if db.engine.dialect.name == 'mysql':
        triggers = db.engine.execute('show triggers;').fetchall()
        for n in triggers:
            if n[0] in custom_triggers:
                raise Exception("triggers already exists {0}".format(n[0]))
        db.engine.execute(('''CREATE TRIGGER {0} AFTER INSERT ON 'post' FOR EACH ROW UPDATE 'stats'
            SET 'stats'.'total' = 'stats'.'total' + 1 
            WHERE 'stats'.'name' = 'post_count';
            CREATE TRIGGER {1} AFTER DELETE ON 'post' FOR EACH ROW UPDATE 'stats'
            SET 'stats'.'total' = 'stats'.'total' - 1 
            WHERE 'stats'.'name' = 'post_count';'''.format(custom_triggers[0],
                custom_triggers[1]).replace('\n', '')))
        print('triggers are created.They are', ','.join(custom_triggers))

def submit_links(links=None, from_db=False):
    '''
    get links from file by default.
    baidu_linksubmit.txt's format is as follows:
    https://www.example.com/1
    https://www.example.com/2
    https://www.example.com/article/1

    params:
        links default to None,can be str,list or set.
        str:
            links='https://www.example.com/1\nhttp://www...',seperated by'\n'
        list,set:
            links=['https://www.example.com/1','https://www.example.com/2']
            links=('https://www.example.com/1','https://www.example.com/2')
    from_db=True is designed for submit articles'url according to data
    from db.This method is not recommended!
    '''
    baidu_url = app.config['BAIDU_LINKSUBMIT']
    headers = {'User-Agent': 'curl/7.12.1', 'Host': 'data.zz.baidu.com'}
    if baidu_url.startswith('http'):
        if not os.path.exists('app/baidu_linksubmit.txt'):
            print('lack of app/baidu_linksubmit.txt')
            return 
        if not links:
            with open('app/baidu_linksubmit.txt', 'r+') as f:
                links = set()
                for n, l in enumerate(f):
                    if l.startswith('http'):
                        links.add(l)
                    if n > 9999:
                        break                     #limit number to 10000
                if links:
                    links = ''.join(links)
                    r = requests.post(
                        url=baidu_url,
                        data=links,
                        headers=headers)
                    if r.ok:
                        try:
                            feedback = eval(r.text)
                        except:
                            print('feedback is uncorrect,not dict-like format.ckeck the baidu_url')
                            return
                        if isinstance(feedback, dict):
                            fails = feedback['success'] - (1+n)
                            if fails > 0:
                                print(fails,' links failed',feedback)
                            else:
                                f.truncate()
                        print(feedback['success'], 'pieces of links are submitted to baidu.')
                        return True
                    else:
                        print('fail to connect,maybe url is uncorrect.code:',r.stats_code)

        if links:
            if isinstance(links, str) and 7<len(links)<88000 \
                    and links.startswith('http'):
                links = links
                n = len(links.split('\n'))
            elif isinstance(links, (list, set)) and links:
                links = set(links)
                n = len(links)
                links = '\n'.join(links)
            else:
                print('param links is set badly.')
                return
            r = requests.post(
                url=baidu_url,
                data=links,
                headers=headers)
            if r.ok:
                try:
                    feedback = eval(r.text)
                except:
                    print('feedback is uncorrect,not dict-like format.ckeck the baidu_url')
                    return
                if isinstance(feedback, dict):
                    fails = feedback['success'] - n
                    if fails > 0:
                        print(fails,' links failed',feedback)
                print(feedback['success'], 'pieces of links are submitted to baidu.')
                return True
            else:
                print('fail to connect,maybe url is uncorrect.code:',r.stats_code)

        if from_db:
            posts = Post.query.filter_by(baidu_linksubmit=0).limit(1000).all()
            links = set()
            pattern = ''
            while not pattern.startswith('http'):
                pattern = input('''input domain name.
                    for example:
                        if you want to submit 'http://www.zhuchuzjut/test/1'
                        you should input 'http://www.zhuchuzjut/test/'
                        ''')
            for n, l in enumerate(posts):
                links.add(pattern + str(l.id))
                l.baidu_linksubmit = 1
            if links:
                links = '\n'.join(links)
                r = requests.post(
                        url=baidu_url,
                        data=links,
                        headers=headers)
                if r.ok:
                    try:
                        feedback = eval(r.text)
                    except:
                        print('feedback is uncorrect,not dict-like format.ckeck the baidu_url')
                        return 
                    if isinstance(feedback, dict):
                        fails = feedback['success'] - (1+n)
                        if fails > 0:
                            print(fails,' links failed',feedback)
                        else:
                            db.session.commit()
                            print(feedback)
                    print(feedback['success'], 'pieces of links are submitted to baidu.')
                else:
                    print('fail to connect,maybe url is uncorrect.code:',r.stats_code)

if __name__ == '__main__':
    update_post_total()
    create_triggers()
    submit_links()
    print('over')