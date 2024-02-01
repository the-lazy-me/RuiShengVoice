import json
import requests
import logging
import io
import time
import re
import yaml
import os
import pilk
import base64
from pydub import AudioSegment

# 读取上级目录的配置文件
with open(os.path.join(os.path.dirname(__file__), '..', 'config.yml'), 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

api_key = config['api_key']
model = config['model']
voice_id = config['voice_id']
randomness = config['randomness']
stability_boost = config['stability_boost']
logging.info(
    "使用参数\napi_key：" + api_key + " \nmodel：" + str(model) + " \nvoice_id：" + str(voice_id) + "\nrandomness：" + str(
        randomness) + "\nstability_boost：" + str(stability_boost) + "\n进行语音合成")


# 生成音频，并转为silk
def generate_audio(text):
    # 发起生成语音任务
    result_id = send_generate_task(api_key, voice_id, text)

    # 定时查询语音生成任务
    query_generate_task(api_key, result_id)

    # 获取当前文件所在目录
    temp_folder = os.path.join(os.path.dirname(__file__), '..', 'audio_temp')
    # 要转换的mp3文件路径
    mp3_path = os.path.join(os.path.dirname(__file__), '..', 'audio_temp', f"{result_id}.mp3")
    # 转换为silk
    silk_path = convert_mp3_to_silk(mp3_path, temp_folder)
    # 转换为base64
    base64_silk = silk_to_base64(silk_path)
    # 清空audio_temp文件夹
    for root, dirs, files in os.walk(temp_folder):
        for file in files:
            os.remove(os.path.join(root, file))
    return base64_silk


# 分割句子
def sentence_slice(text):
    text = re.split('。|；|！|？', text)
    # 去除换行符号
    text = [i.replace("\n", "") for i in text]
    # 去除空格
    text = [i.strip() for i in text]
    # 去除空字符串
    text = [i for i in text if i != ""]
    return text


# 发起生成语音任务
def send_generate_task(api_key, voice_id, text):
    # API 请求地址
    url = 'https://v1.reecho.cn/api/tts/generate'

    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'  # 替换为你的实际 API key
    }

    # 分割句子
    sentences = sentence_slice(text)

    # 准备 contents 变量
    contents = []
    for sentence in sentences:
        contents.append({
            "text": sentence,
            "voiceId": voice_id
        })

    # 准备要发送的数据
    data = {
        "model": model,
        "randomness": randomness,
        "stability_boost": stability_boost,
        "contents": contents
    }

    # 打印要发送的数据
    logging.debug("请求数据:")
    logging.debug(json.dumps(data, ensure_ascii=False, indent=2))

    # 发起 POST 请求
    response = requests.post(url, headers=headers, json=data)

    # 处理响应
    if response.status_code == 200:
        result = response.json()
        # 打印响应数据
        logging.debug("响应数据:")
        logging.debug(json.dumps(result, ensure_ascii=False, indent=2))

        result_id = result['data']['id']
        return result_id
    else:
        # 打印错误信息
        logging.error(f"请求失败: {response.status_code}")
        return None


# 获取语音生成任务
def get_generate_task(api_key, id):
    url = f'https://v1.reecho.cn/api/tts/generate/{id}'

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # 发起 GET 请求
    response = requests.get(url, headers=headers)

    # 处理响应

    if response.status_code == 200:
        result = response.json()
        # 打印响应数据
        logging.debug("响应数据:")
        logging.debug(json.dumps(result, ensure_ascii=False, indent=2))

        result_contents = result['data']['metadata']['contents']
        return result_contents
    else:
        # 打印错误信息
        logging.error(f"请求失败: {response.status_code}")
        return None


# 定时进行语音生成任务查询
def query_generate_task(api_key, id):
    # 查询语音生成任务
    result = get_generate_task(api_key, id)

    # 如果查询到列表的每一项都要存在audio字段
    if result and all('audio' in content for content in result):
        # 将每一项的audio字段的值存入列表
        audio_urls = []
        for content in result:
            audio_urls.append(content['audio'])
        # 合并音频文件
        merge_audio(audio_urls, id)
        logging.debug("合并完成,文件名为" + id + ".mp3")
    else:
        # 如果没有查询到结果，等待 1 秒后再次查询
        time.sleep(1)
        query_generate_task(api_key, id)


# 下载并合并音频文件
def merge_audio(audio_urls, id):
    # 创建空列表，用于存放音频文件
    audio_files = []
    for url in audio_urls:
        response = requests.get(url)
        audio_files.append(AudioSegment.from_mp3(io.BytesIO(response.content)))

    # 创建空的 AudioSegment 对象
    audio = AudioSegment.silent()

    # 拼接音频文件
    for audio_file in audio_files:
        audio += audio_file

    # 判断当前目录下是否存在 audio_temp 文件夹，如果不存在则创建
    if not os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'audio_temp')):
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'audio_temp'))

    # 导出音频文件,命名为id.mp3,保存在当前目录的audio_temp文件夹下
    out_path = os.path.join(os.path.dirname(__file__), '..', 'audio_temp', f"{id}.mp3")
    logging.debug(out_path)
    audio.export(out_path, format="mp3")


# 转化为pcm
def mp3_to_pcm(mp3_path: str, temp_folder: str) -> tuple[str, int]:
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        sample_rate = audio.frame_rate
        pcm_data = audio.raw_data
        pcm_path = os.path.join(temp_folder, os.path.splitext(os.path.basename(mp3_path))[0] + '.pcm')
        with open(pcm_path, 'wb') as pcm_file:
            pcm_file.write(pcm_data)
        return pcm_path, sample_rate
    except Exception as e:
        logging.error(f"Error converting MP3 to PCM: {e}")
        raise


# 转换为silk
def convert_mp3_to_silk(mp3_path: str, temp_folder: str) -> str:
    try:
        pcm_path, sample_rate = mp3_to_pcm(mp3_path, temp_folder)
        silk_path = os.path.join(temp_folder, os.path.splitext(os.path.basename(pcm_path))[0] + '.silk')
        pilk.encode(pcm_path, silk_path, pcm_rate=sample_rate, tencent=True)
        return silk_path
    except Exception as e:
        logging.error(f"Error converting MP3 to SILK: {e}")
        raise


# 将silk进行base64编码，返回base64编码后的字符串
def silk_to_base64(silk_path: str) -> str:
    try:
        with open(silk_path, "rb") as audio_file:
            audio_data = audio_file.read()
        base64_silk = base64.b64encode(audio_data).decode("utf-8")
        return base64_silk
    except FileNotFoundError:
        logging.error("Error: Silk file not found.")
    except Exception as e:
        logging.error(f"Error: {e}")


# 示例用法
if __name__ == "__main__":
    # 示例文本
    your_text = """
    你好，世界！
    """

    # 成并合并音频文件
    result = generate_audio(your_text)
    print(result)
