import tornado
from openai import OpenAI


class TornadoSSEHandler(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        api_key = "sk-0da03bdfd5414766ae05a0050134cfb1"
        base_url = "https://api.deepseek.com"
        client = OpenAI(api_key=api_key, base_url=base_url)
        message = self.get_argument("msg")
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system",
                     "content": "你是一个很有帮助的私人助理，知识面很广。可以回答用户提出的各种问题。不过记住一点，对于对话中已经回答过的问题，就不要再回答了。专注于新的问题解答即可"},
                    {"role": "user", "content": f'{message}'},
                ],
                presence_penalty=1.5,
                stream=True
            )
            for part in response:
                self.write(f"data: {part}\n\n")
                self.flush()
            self.finish()
        except Exception as e:
            self.write("data: Error Occurred\n\n")
            self.finish()
