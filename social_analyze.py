import os
import sqlite3

def extract_social_media_data(partition_path, output_file='social_media_analysis.txt'):

    social_media_domains = [
        'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'tiktok.com', 'pinterest.com', 'reddit.com', 'snapchat.com',
        'tumblr.com', 'vk.com', 'whatsapp.com', 'youtube.com', 'discord.com',
        'flickr.com', 'wechat.com', 'viber.com', 'zoom.us', 'skype.com',
        'myspace.com', 'periscope.tv', 'xing.com', 'soundcloud.com', 'spotify.com',
        'yahoo.com', 'meetup.com', 'foursquare.com', 'quora.com', 'mix.com',
        'plurk.com', 'behance.net', 'dribbble.com', 'medium.com', 'slack.com',
        'telegram.org', 'line.me', 'weibo.com', 'snapchat.com', 'reddit.com',
        'clubhouse.com', 'kakao.com', 'ok.ru', 'twitch.tv', 'dailymotion.com',
        'badoo.com', 'match.com', 'grindr.com', 'taringa.net', 'ask.fm', 'vimeo.com',
        'foursquare.com', 'periscope.tv', 'stumbleupon.com', 'livejournal.com', 'icq.com',
        'yandex.ru', 'turing.com', 'baidu.com', 'qq.com', 'bilibili.com', 'douyin.com',
        'koubei.com', 'renren.com', 'douban.com', 'qqmail.com', 'zhihu.com', 'whatsapp.com'
    ]

    browser_files = {
        'chrome': {
            'history': ['History'],
            'cookies': ['Cookies']
        },
        'firefox': {
            'history': ['places.sqlite'],
            'cookies': ['cookies.sqlite']
        },
        'edge': {
            'history': ['History'],
            'cookies': ['Cookies']
        },
        'opera': {
            'history': ['History'],
            'cookies': ['Cookies']
        },
        'safari': {
            'history': ['History.db'],
            'cookies': ['Cookies.binarycookies']
        }
    }

    results = []

    for root, dirs, files in os.walk(partition_path):
        for file in files:
            for browser, file_types in browser_files.items():
                if file in file_types['history']:
                    analyze_history_file(os.path.join(root, file), social_media_domains, results, browser)
                if file in file_types['cookies']:
                    analyze_cookies_file(os.path.join(root, file), social_media_domains, results, browser)

    with open(output_file, 'w') as f:
        for result in results:
            f.write(str(result) + '\n')
    
    simply_results = [{"browser": result["browser"], "host": result["host"]} for result in results]
    return count_hosts_by_browser(simply_results)

def analyze_history_file(history_file, social_media_domains, results, browser):
    try:
        conn = sqlite3.connect(history_file)
        cursor = conn.cursor()
        print(f"[INFO] Analyzing ({browser}): {history_file}")

        if browser in ['chrome', 'edge', 'opera']:
            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
        elif browser == 'firefox':
            cursor.execute("SELECT url, title, visit_count FROM moz_places")
        elif browser == 'safari':
            cursor.execute("SELECT history_item, visit_count FROM history_visits")
        else:
            return

        for row in cursor.fetchall():
            for domain in social_media_domains:
                if domain in row[0]:
                    results.append({
                        "browser": browser,
                        "file": history_file,
                        "url": row[0],
                        "title": row[1] if len(row) > 1 else None,
                        "visit_count": row[2] if len(row) > 2 else None,
                        "last_visit_time": row[3] if len(row) > 3 else None
                    })
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error: ({browser}): {history_file}, {e}")


def analyze_cookies_file(cookies_file, social_media_domains, results, browser):
    try:
        if browser == 'safari' and cookies_file.endswith('.binarycookies'):
            print(f"[INFO] Cookies Safari ({browser}) : {cookies_file}")
            return

        conn = sqlite3.connect(cookies_file)
        cursor = conn.cursor()
        print(f"[INFO] Analyzing cookies ({browser}): {cookies_file}")

        if browser in ['chrome', 'edge', 'opera', 'firefox']:
            cursor.execute("SELECT host_key, name, value FROM cookies")
        else:
            return

        for row in cursor.fetchall():
            for domain in social_media_domains:
                if domain in row[0]:
                    results.append({
                        "browser": browser,
                        "file": cookies_file,
                        "host": row[0],
                        "cookie_name": row[1],
                        "cookie_value": row[2]
                    })
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error ({browser}): {cookies_file}, {e}")


def count_hosts_by_browser(results):
    host_counts = {}

    for result in results:
        browser = result["browser"]
        host = result["host"]

        if browser not in host_counts:
            host_counts[browser] = {}

        if host not in host_counts[browser]:
            host_counts[browser][host] = 0

        host_counts[browser][host] += 1
    
    return host_counts
