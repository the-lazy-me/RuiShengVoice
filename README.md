# RuiShengVoice

[QChatGPT](https://github.com/RockChinQ/QChatGPT)的插件，通过调用睿声的API，将输出内容转化为音频

> 我没学过python，代码大量依赖于AI生成，难免有不合理不正确之处，不过，代码和人有一个能跑就行😋

## 介绍

本插件调用了睿声的API，Reecho.AI 睿声 - 超拟真人工智能瞬时语音克隆平台（他们这么说），**注意：**API不是免费的，需要最低支付大概15元才可调用

效果：只能说还过得去，但有时候不稳定，尤其面对中英文混合时，不过胜在可以自己上传音频构建自己的音频模型，而且时间和金钱成本低

## 使用

### 下载

克隆此项目，放到plugins的文件夹下

```bash
git clone https://github.com/the-lazy-me/RuiShengVoice.git
```

或下载源码压缩包，解压后放到plugins的文件夹下

打开RuiShengVoice文件夹，命令行执行

```bash
pip install -r requirements.txt
```

速度太慢可以执行

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### 前置工作

参考此教程，安装ffmpeg

教程：https://zhuanlan.zhihu.com/p/118362010

### 配置

打开RuiShengVoice文件夹下的`config.yml`，内容如下图所示

```yaml
# 以下参数，可在https://dev.reecho.ai/introduction/overview找到
# 你在睿声获取的API，链接https://dev.reecho.ai/introduction/authentication
api_key: sk-XXXXXXXXXXXXXXXXXXXXXXXXX
# 参考睿声给出的模型，接着2024年2月2日，他们只给出下面这个model，链接https://dev.reecho.ai/generate/async
model: reecho-neural-voice-001
# 睿声给出的角色id，链接https://dash.reecho.ai/voices，这里以罗翔老师的为例
voice_id: 06887661-89a4-4196-bcb4-30b227e36277
# 多样性 (0-100)，参考https://dev.reecho.ai/generate/async
randomness: 97
# 稳定性过滤 (0-100，默认请填写0)，参考https://dev.reecho.ai/generate/async
stability_boost: 100
# 是否默认开启语音功能，默认为False
voice_switch: False
```

- 先注册一个睿声的账号，在https://www.reecho.ai/
- api_key的获取，在https://dash.reecho.ai/apiKey，要先充值的，目前最低大概15元
- model的填写，目前不用改，具体看https://dev.reecho.ai/generate/async，点页面的post，里面可以看到介绍
- voice_id的填写，注册账号后，你可以在声音社区将喜欢的添加到角色列表，然后在[角色管理](https://dash.reecho.ai/voices)点击你选择的人物的详细，上面有个角色详细，项目那一串数字就是，例如`06887661-89a4-4196-bcb4-30b227e36277`（罗翔老师的音频模型）
- randomness，和stability_boost同model

> 来自[官方](https://dash.reecho.ai/generate)的生成风格：
>
> - 通用：对大部分用例较为通用的生成风格，限制相对较小，但部分声音角色的表现可能会不够稳定
>   - 多样性`randomness`: 97
>   - 稳定性过滤`stability_boost`: 0
> - 均衡：平衡了稳定性与多样性的生成风格，相较于通用的稳定性更强，但部分声音角色表现力以及音色相似度可能有所下降
>   - 多样性`randomness`: 97
>   - 稳定性过滤`stability_boost`: 100
> - 稳定：更为稳定的生成风格，各项参数限制相对较大，可能会导致部分声音角色的表现力以及音色相似度较差
>   - 多样性`randomness`: 97
>   - 稳定性过滤`stability_boost`: 50
> - 创意：多样性最高，且限制最小的生成风格，通常可以发挥模型的全部表现力，但稳定性可能较差
>   - 多样性`randomness`: 00
>   - 稳定性过滤`stability_boost`: 0

- voice_switch，看你喜好，选择是否默认开启，当然你也可以在对话中调整开关，如下

## 对话

- `!voice on`开启语音
- `!voice onff`关闭语音

语音输出相比文字会有一定滞后，这一点只能等睿声提供更快速的语音输出

