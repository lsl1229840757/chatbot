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
                                            temperature=0,
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


if __name__ == '__main__':
    bot = ChatGPT('<Put your api key here!>')
    bot.chat()
