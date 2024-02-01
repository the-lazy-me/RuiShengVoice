import os

import mirai
import yaml

from pkg.plugin.host import EventContext, PluginHost
from pkg.plugin.models import *
from plugins.RuiShengVoice.pkg.voice_message import generate_audio

# 读取配置文件
with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
# 语音开关
enable = config['voice_switch']


# 注册插件
@register(name="RuiShengVoice", description="一个对接睿声API的文本转语音插件", version="0.1", author="the-lazy-me")
class MyPlugin(Plugin):

    # 插件加载时触发
    # plugin_host (pkg.plugin.host.PluginHost) 提供了与主程序交互的一些方法，详细请查看其源码
    def __init__(self, plugin_host: PluginHost):
        logging.info("Hello Plugin loaded.")
        pass

    # 当收到个人消息时触发
    @on(NormalMessageResponded)
    @on(GroupNormalMessageReceived)
    def text_to_voice(self, event: EventContext, **kwargs):
        # 输出调试信息
        # logging.debug("hello, {}".format(kwargs['sender_id']))
        global enable
        # 如果语音开关开启
        if enable:
            # logging.info("回复的文本消息是：{}".format(kwargs["response_text"]))
            res_text = kwargs["response_text"]
            # 生成语音
            result = generate_audio(res_text)

            # 使用Mirai库发送语音消息
            voice_message = mirai.Voice(base64=result)
            event.add_return("reply", [voice_message])
            event.prevent_default()

    # 当收到个人/群消息时触发
    @on(PersonCommandSent)
    @on(GroupCommandSent)
    def open_text_to_voice(self, event: EventContext, **kwargs):
        global enable
        command = kwargs["command"]
        params = kwargs["params"]
        if command == "voice" and kwargs["is_admin"]:
            if params[0] == "on":
                enable = True
                event.add_return("reply", ["语音开关已开启"])
                event.prevent_default()
            elif params[0] == "off":
                enable = False
                event.add_return("reply", ["语音开关已关闭"])
                logging.info(enable)
                event.prevent_default()


# 插件卸载时触发
def __del__(self):
    pass
