# ChatBot

## OpenAI ChatGPT API + Search Engine Web Crawler (Baidu)

Make chatgpt more accurate and timely!

> &emsp;众所周知，在OpenAI平台上的``ChatGPT``模型目前有两大痛点：1. 它所学习的数据资料都是截止到2021年为止的，因此无法给出2022年之后的发生的事情。2. 有些时候会出现一些常识性的错误，也就是它会一本正经的胡说八道，比如问它一些历史、数学问题，它可能就会回答出**像那么回事儿的错误答案**。
> &emsp;究其原因，主要是ChatGPT是“生成式回复”。它事先学习了大量的人类的知识以及人类对它的引导和奖励的策略。它本质上依托于一个参数量巨大的神经网络模型，其训练过程是基于它的语料库进行的，而**这些训练数据本身良莠不齐，并不全都是优质文本，因此有可能出现事实性错误问题。** ``ChatGPT``给出的答案只是基于其理解生成的最佳结果，然而对于某些训练的知识盲区问题，它可能根据字面意思进行推理，从而出现了“一本正经胡说八道”的现象。
> &emsp;所以为了解决上面的两个问题，我们可以利用**搜索引擎**向``ChatGPT``提供准确、及时的辅助信息。<font color="magenta">**总而言之，整体方案就是把在搜索引擎上爬取的问题相关资料丢给CharGPT，让它帮我们整合并输出我们想要的答案。**</font>
> &emsp;接下来，博主会从``OpenAI``的账号注册到怎么整合**搜索引擎爬虫**和``OpenAI API``，手把手教大家搭建一个自己的聊天小助手。

## 1.快速通道
&emsp;要是有代码熟练度的读者想直接调试完整代码，可以到我的这个repository直接下载完整可运行的代码<font color="magenta">**求Star！**</font>：[https://github.com/lsl1229840757/chatbot](https://github.com/lsl1229840757/chatbot)。

## 2. OpenAI账号注册
&emsp;详细的注册方法可以参考这个博客[一文教你快速注册OpenAI（ChatGPT）](https://cloud.tencent.com/developer/article/2190154)。简而言之，用这个[https://sms-activate.org](https://sms-activate.org)平台去租借一个虚拟号码模拟外国手机接收账号注册的验证码。
![在这里插入图片描述](https://img-blog.csdnimg.cn/56fffd6d2c624b81aaf94b98495bfcb9.png)
## 3. ChatGPT历史的局限性与事实性错误
&emsp;在摘要之中博主已经详细分析了ChatGPT（1）无法回答2022年之后发生的事情；（2）会犯一些常识性的错误，这两大问题。下面让我们举个栗子来看看：

&emsp;当我们问他2022世界杯冠军队伍是哪支的时候，它说它无法预测。
![在这里插入图片描述](https://img-blog.csdnimg.cn/479ed6a733ad4666b29fe1fbbf8f02b5.png)
&emsp;当我们问他勾三股四弦五是什么的时候，它会一本正经的告诉我们这是中国古代乐器琴的调弦方法：
![在这里插入图片描述](https://img-blog.csdnimg.cn/18a545e811e34846bc9b36883754dc02.png)
## 4. 百度搜索引擎爬虫与ChatGPT整合
### 4.1 百度搜索引擎爬虫
&emsp;让我们来看看百度爬虫该怎么编写，话不多说，我们先看看百度之后返回的结果网页的Dom结构：
![在这里插入图片描述](https://img-blog.csdnimg.cn/c1f4b9630063441e8aa0037932e37835.png)
![在这里插入图片描述](https://img-blog.csdnimg.cn/67085d35f6be46a1b0e6c4d7fabb50a0.png)
&emsp;来自于百度知道的结果被放在了一个class为c-border的div之中，而其他普通结果每一个Item都被放到了class为result的div之中，而聚合结果会被放在class为result-op的div之中。所以我们使用``selenium``可以很容易地写出一个简易的百度数据获取代码<font color="magenta">**（后面有完整可运行的代码）**</font>：
```python
class ChatGPT(object):

    def __init__(self, api_key) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # 设置不弹出浏览器
        options.add_experimental_option('excludeSwitches',
                                        ['enable-logging'])  # 控制台不输出
        self.browser = webdriver.Chrome(options=options)

    def _grabbing_data(self, wd):
        url = f'https://www.baidu.com/s?wd={wd}'

        self.browser.get(url)
        self.browser.execute_script(
            'window.scrollTo(0, document.body.scrollHeight)')

        data = []
        results = self.browser.find_elements(By.CLASS_NAME, 'c-border') \
                + self.browser.find_elements(By.CLASS_NAME, 'result-op') \
                + self.browser.find_elements(By.CLASS_NAME, 'result')

        for result in results[:5]:

            a_link = result.find_element(By.TAG_NAME, 'a')
            href = a_link.get_attribute('href')
            data.append(result.text + f'来源:{href}')

        return data
```

### 4.2 OpenAI ChatGPT API
&emsp;要是用OpenAI ChatGPT API就需要先有一个OpenAI的账号，然后点击这里[https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)申请一个API Key。
![在这里插入图片描述](https://img-blog.csdnimg.cn/437b4a35f1a34e2f9ee541bb94774ed8.png)
&emsp;有了这个API Key我们就可以使用OpenAI的相关API服务了，这里放了它完整的[OpenAI API Doc](https://platform.openai.com/docs/introduction/overview)链接，有兴趣的读者可以点进去直接查看。下面我直接贴调用``Text completion``也就是我们熟悉的``ChatGPT``的代码：
```python
import warnings

import openai
from selenium import webdriver
from selenium.webdriver.common.by import By

warnings.filterwarnings('ignore')


class ChatGPT(object):

    def __init__(self, api_key) -> None:
        self._api_key = None
        self.api_key = api_key
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # 设置不弹出浏览器
        options.add_experimental_option('excludeSwitches',
                                        ['enable-logging'])  # 控制台不输出
        self.browser = webdriver.Chrome(options=options)

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        self._api_key = api_key
        # Load your API key
        openai.api_key = api_key

    def _grabbing_data(self, wd):
        url = f'https://www.baidu.com/s?wd={wd}'

        self.browser.get(url)
        self.browser.execute_script(
            'window.scrollTo(0, document.body.scrollHeight)')

        data = []
        results = self.browser.find_elements(By.CLASS_NAME, 'c-border') \
                + self.browser.find_elements(By.CLASS_NAME, 'result-op') \
                + self.browser.find_elements(By.CLASS_NAME, 'result')

        for result in results[:5]:

            a_link = result.find_element(By.TAG_NAME, 'a')
            href = a_link.get_attribute('href')
            data.append(result.text + f'来源:{href}')

        return data

    def _format_prompt(self, prompt):
        print(f'正在百度中搜索{prompt}相关资料...')
        data = self._grabbing_data(prompt)
        data = '\n'.join(data)
        prompt = f'请根据以下辅助信息回答问题: {data[:1000]}\n 请问:{prompt}'
        return prompt

    def get_answer(self, prompt):
        prompt = self._format_prompt(prompt)
        response = openai.Completion.create(model="text-davinci-003",
                                            prompt=prompt,
                                            temperature=0.6,
                                            max_tokens=2048)
        return response['choices'][0]['text']

    def chat(self):
        flag = True
        print('欢迎使用百度版ChatGPT, 我使用了百度作为资料搜索支撑引擎, 如果您想退出请输入exit!')
        while flag:
            prompt = input()
            if prompt != 'exit':
                print(self.get_answer(prompt))
            else:
                print('再见!')
                flag = False
```

## 5. 效果演示
&emsp;没有对比就没有伤害，咱们话不多说，直接上效果展示：
 * 询问2022世界杯冠军队伍
![在这里插入图片描述](https://img-blog.csdnimg.cn/41e708675f404477b976c1237e020947.png)
 * 询问勾股定理
![在这里插入图片描述](https://img-blog.csdnimg.cn/b22bd9fd65d9473195fbb1eb3c93587f.png)
 * 查看近期的新闻
![在这里插入图片描述](https://img-blog.csdnimg.cn/8f29fd74f78b4bb1ba3d81229f8edff7.png)
![在这里插入图片描述](https://img-blog.csdnimg.cn/3a63a3f50bed4093922c204bbef030b7.png)
## 6. 参考资料
 * https://cloud.tencent.com/developer/article/2190154
 * https://platform.openai.com/account/api-keys
 * https://platform.openai.com/docs/introduction/overview

