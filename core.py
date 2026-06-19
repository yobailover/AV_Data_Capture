import json
import os.path
import re
import shutil
import platform

from PIL import Image
from ADC_function import *

# =========website========
from WebCrawler import avsox
from WebCrawler import fanza
from WebCrawler import fc2fans_club
from WebCrawler import jav321
from WebCrawler import javbus
from WebCrawler import javdb
from WebCrawler import mgstage
from WebCrawler import xcity
from WebCrawler import javlib
from WebCrawler import dlsite
from WebCrawler import missav


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    print('[-]Move to Failed output folder')
    shutil.move(filepath, str(os.getcwd()) + '/' + failed_folder + '/')
    return 


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            return 


def get_data_from_json(file_number, filepath, conf: config.Config):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data
    """

    func_mapping = {
        "avsox": avsox.main,
        "fc2": fc2fans_club.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        "javlib": javlib.main,
        "dlsite": dlsite.main,
        "missav": missav.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if "avsox" in sources and (re.match(r"^\d{5,}", file_number) or
        "HEYZO" in file_number or "heyzo" in file_number or "Heyzo" in file_number
    ):
        if conf.debug() == True:
            print('[+]select avsox')
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif "fanza" in sources and (re.match(r"\d+\D+", file_number) or
        "siro" in file_number or "SIRO" in file_number or "Siro" in file_number
    ):
        if conf.debug() == True:
            print('[+]select fanza')
        sources.insert(0, sources.pop(sources.index("fanza")))
    elif "fc2" in sources and ("fc2" in file_number or "FC2" in file_number
    ):
        if conf.debug() == True:
            print('[+]select fc2')
        sources.insert(0, sources.pop(sources.index("fc2")))
    elif "dlsite" in sources and (
        "RJ" in file_number or "rj" in file_number or "VJ" in file_number or "vj" in file_number
    ):
        if conf.debug() == True:
            print('[+]select dlsite')
        sources.insert(0, sources.pop(sources.index("dlsite")))

    json_data = {}
    for source in sources:
        try:
            if conf.debug() == True:
                print('[+]select',source)
            json_data = json.loads(func_mapping[source](file_number))
            # if any service return a valid return, break
            if get_data_state(json_data):
                break
        except:
            break

    # Return if data not found in all sources
    if not json_data:
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # ================================================网站规则添加结束================================================

    title = json_data['title']
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data['release']
    number = json_data['number']
    studio = json_data['studio']
    source = json_data['source']
    runtime = json_data['runtime']
    outline = json_data['outline']
    label = json_data['label']
    series = json_data['series']
    year = json_data['year']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small = ''
    imagecut = json_data['imagecut']
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    # ===  替换Studio片假名
    studio = studio.replace('アイエナジー','Energy')
    studio = studio.replace('アイデアポケット','Idea Pocket')
    studio = studio.replace('アキノリ','AKNR')
    studio = studio.replace('アタッカーズ','Attackers')
    studio = re.sub('アパッチ.*','Apache',studio)
    studio = studio.replace('アマチュアインディーズ','SOD')
    studio = studio.replace('アリスJAPAN','Alice Japan')
    studio = studio.replace('オーロラプロジェクト・アネックス','Aurora Project Annex')
    studio = studio.replace('クリスタル映像','Crystal 映像')
    studio = studio.replace('グローリークエスト','Glory Quest')
    studio = studio.replace('ダスッ！','DAS！')
    studio = studio.replace('ディープス','DEEP’s')
    studio = studio.replace('ドグマ','Dogma')
    studio = studio.replace('プレステージ','PRESTIGE')
    studio = studio.replace('ムーディーズ','MOODYZ')
    studio = studio.replace('メディアステーション','宇宙企画')
    studio = studio.replace('ワンズファクトリー','WANZ FACTORY')
    studio = studio.replace('エスワン ナンバーワンスタイル','S1')
    studio = studio.replace('エスワンナンバーワンスタイル','S1')
    studio = studio.replace('SODクリエイト','SOD')
    studio = studio.replace('サディスティックヴィレッジ','SOD')
    studio = studio.replace('V＆Rプロダクツ','V＆R PRODUCE')
    studio = studio.replace('V＆RPRODUCE','V＆R PRODUCE')
    studio = studio.replace('レアルワークス','Real Works')
    studio = studio.replace('マックスエー','MAX-A')
    studio = studio.replace('ピーターズMAX','PETERS MAX')
    studio = studio.replace('プレミアム','PREMIUM')
    studio = studio.replace('ナチュラルハイ','NATURAL HIGH')
    studio = studio.replace('マキシング','MAXING')
    studio = studio.replace('エムズビデオグループ','M’s Video Group')
    studio = studio.replace('ミニマム','Minimum')
    studio = studio.replace('ワープエンタテインメント','WAAP Entertainment')
    studio = re.sub('.*/妄想族','妄想族',studio)
    studio = studio.replace('/',' ')
    # ===  替换Studio片假名 END
    
    location_rule = eval(conf.location_rule())

    # Process only Windows.
    if platform.system() == "Windows":
        if 'actor' in conf.location_rule() and len(actor) > 100:
            print(conf.location_rule())
            location_rule = eval(conf.location_rule().replace("actor","'多人作品'"))
        if 'title' in conf.location_rule() and len(title) > 100:
            location_rule = eval(conf.location_rule().replace("title",'number'))

    # Truncate runtime to pure integer (minutes), strip any unit suffix
    try:
        clean_runtime = int(runtime)
    except (ValueError, TypeError):
        clean_runtime = 0
    json_data['runtime'] = str(clean_runtime)

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    naming_result = eval(conf.naming_rule())
    # If the title already starts with the number (e.g. missav returns "CAWD-969 Title"),
    # strip the duplicate prefix to avoid "CAWD-969 CAWD-969 ..."
    if title.startswith(number):
        naming_result = title
    json_data['naming_rule'] = naming_result
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    return json_data


def get_info(json_data):  # 返回json里的数据
    title = json_data['title']
    studio = json_data['studio']
    year = json_data['year']
    outline = json_data['outline']
    runtime = json_data['runtime']
    director = json_data['director']
    actor_photo = json_data['actor_photo']
    release = json_data['release']
    number = json_data['number']
    cover = json_data['cover']
    website = json_data['website']
    series = json_data['series']
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label


def small_cover_check(path, number, cover_small, naming_rule_result, conf: config.Config, filepath, failed_folder):
    base = naming_rule_result
    poster_name = base + '.png'
    download_file_with_filename(cover_small, poster_name, path, conf, filepath, failed_folder)
    print('[+]Image Downloaded! ' + path + '/' + poster_name)


def create_folder(success_folder, location_rule, json_data, conf: config.Config):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)
    if len(location_rule) > 240 or len(success_folder + '/' + location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor","'manypeople'",3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ']-' + title, "/number")
            path = escape_path(path, conf.escape_literals())

            os.makedirs(path)
    return path


# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: config.Config, filepath, failed_folder):
    proxy, timeout, retry_count, proxytype = config.Config().proxy()

    for i in range(retry_count):
        try:
            if not proxy == '':
                if not os.path.exists(path):
                    os.makedirs(path)
                proxies = get_proxy(proxy, proxytype)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
                r = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'}
                r = requests.get(url, timeout=timeout, headers=headers)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, failed_folder)
    return


# 封面是否下载成功，否则移动到failed
def image_download(cover, base, path, conf: config.Config, filepath, failed_folder):
    fanart_name = base + '.jpg'
    if download_file_with_filename(cover, fanart_name, path, conf, filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path + '/' + fanart_name) == 0:
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(cover, fanart_name, path, conf, filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + fanart_name) == 0:
        return
    print('[+]Image Downloaded!', path + '/' + fanart_name)


def print_files(path, base_nfo, naming_rule_evaluated, cn_sub, json_data, filepath, failed_folder, tag, actor_list, liuchu, base_thumb, base_fanart, base_poster):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)

    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + "/" + base_nfo + ".nfo", "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print(" <title>" + base_nfo + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>" + outline + "</outline>", file=code)
            print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + base_poster + "</poster>", file=code)
            print("  <thumb>" + base_thumb + "</thumb>", file=code)
            print("  <fanart>" + base_fanart + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + key + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                aaaa = ''
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if cn_sub == '1':
                print("  <tag>中文字幕</tag>", file=code)
            if liuchu == '流出':
                print("  <tag>流出</tag>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                aaaaa = ''
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
            except:
                aaaaaaaa = ''
            if cn_sub == '1':
                print("  <genre>中文字幕</genre>", file=code)
            print("  <num>" + number + "</num>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Wrote!            " + path + "/" + base_nfo + ".nfo")
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
        moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
        moveFailedFolder(filepath, failed_folder)
        return


def cutImage(imagecut, base_fanart, base_poster, path):
    if imagecut == 1: # 剪裁大封面
        try:
            img = Image.open(path + '/' + base_fanart)
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w - h / 1.5, 0, w, h))
            img2.save(path + '/' + base_poster)
            print('[+]Image Cutted!     ' + path + '/' + base_poster)
        except:
            print('[-]Cover cut failed!')
    elif imagecut == 0: # 复制封面
        shutil.copyfile(path + '/' + base_fanart, path + '/' + base_poster)
        print('[+]Image Copyed!     ' + path + '/' + base_poster)


def paste_file_to_folder(filepath, path, base, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    try:
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, path + '/' + base + houzhui)
        else:
            os.rename(filepath, path + '/' + base + houzhui)
        if os.path.exists(os.getcwd() + '/' + base + '.srt'):  # 字幕移动
            os.rename(os.getcwd() + '/' + base + '.srt', path + '/' + base + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + base + '.ssa'):
            os.rename(os.getcwd() + '/' + base + '.ssa', path + '/' + base + '.ssa')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + base + '.sub'):
            os.rename(os.getcwd() + '/' + base + '.sub', path + '/' + base + '.sub')
            print('[+]Sub moved!')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return 
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return 


def paste_file_to_folder_mode2(filepath, path, multi_part, base, conf, part=''):  # 文件路径，番号，后缀，要移动至的位置
    if multi_part == 1:
        base += part  # 这时number会被附加上CD1后缀
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    try:
        if conf.soft_link():
            os.symlink(filepath, path + '/' + base + houzhui)
        else:
            os.rename(filepath, path + '/' + base + houzhui)
        if os.path.exists(os.getcwd() + '/' + base + '.srt'):  # 字幕移动
            os.rename(os.getcwd() + '/' + base + '.srt', path + '/' + base + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + base + '.ass'):
            os.rename(os.getcwd() + '/' + base + '.ass', path + '/' + base + '.ass')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + base + '.sub'):
            os.rename(os.getcwd() + '/' + base + '.sub', path + '/' + base + '.sub')
            print('[+]Sub moved!')
        print('[!]Success')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return 
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return

def get_part(filepath, failed_folder):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return


def debug_print(data: json):
    try:
        print("[+] ---Debug info---")
        for i, v in data.items():
            if i == "outline":
                print("[+]  -", i, "    :", len(v), "characters")
                continue
            if i == "actor_photo" or i == "year":
                continue
            print("[+]  -", "%-11s" % i, ":", v)
        print("[+] ---Debug info---")
    except:
        pass


def core_main(file_path, number_th, conf: config.Config):
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    c_word = ''
    cn_sub = ''
    liuchu = ''

    filepath = file_path  # 影片的路径
    number = number_th
    json_data = get_data_from_json(number, filepath, conf)  # 定义番号

    # Return if blank dict returned (data not found)
    if not json_data:
        return

    if json_data["number"] != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data["number"]
    imagecut = json_data['imagecut']
    tag = json_data['tag']
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf.failed_folder())
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀
    if '流出' in filepath:
        liuchu = '流出'

    # 创建输出失败目录
    CreatFailedFolder(conf.failed_folder())

    # 调试模式检测
    if conf.debug():
        debug_print(json_data)

    # 创建文件夹
    path = create_folder(conf.success_folder(), json_data['location_rule'], json_data, conf)

    # Compute base filename from naming_rule (already evaluated on line 217)
    naming_rule_evaluated = json_data['naming_rule']
    if multi_part == 1:
        naming_rule_evaluated += part  # append CD1 etc.

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    if conf.main_mode() == 1:
        base_fanart = naming_rule_evaluated + '.jpg'
        base_poster = naming_rule_evaluated + '.png'
        base_thumb = naming_rule_evaluated + '.png'  # same file, different extension alias
        base_nfo = naming_rule_evaluated

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, number, json_data['cover_small'], json_data['naming_rule'], conf, filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download(json_data['cover'], naming_rule_evaluated, path, conf, filepath, conf.failed_folder())

        # 裁剪图
        cutImage(imagecut, base_fanart, base_poster, path)

        # 打印文件
        print_files(path, base_nfo, naming_rule_evaluated, cn_sub, json_data, filepath, conf.failed_folder(), tag, json_data['actor_list'], liuchu, base_thumb, base_fanart, base_poster)

        # 移动文件
        paste_file_to_folder(filepath, path, naming_rule_evaluated, conf)
    elif conf.main_mode() == 2:
        # 移动文件
        paste_file_to_folder_mode2(filepath, path, multi_part, naming_rule_evaluated, conf)
