import json
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate_reading(self, chart_data: Dict[str, Any], style: str = "friendly", sections: Optional[List[str]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        pass


class MockAIProvider(AIProvider):
    def generate_reading(self, chart_data: Dict[str, Any], style: str = "friendly", sections: Optional[List[str]] = None) -> Dict[str, Any]:
        soul_palace = None
        career_palace = None
        wealth_palace = None
        love_palace = None
        current_decadal = None

        for p in chart_data.get('palaces', []):
            if '命宫' in p.get('tags', []):
                soul_palace = p
            if p.get('name') == '官禄宫':
                career_palace = p
            if p.get('name') == '财帛宫':
                wealth_palace = p
            if p.get('name') == '夫妻宫':
                love_palace = p

        soul_stars = '·'.join(soul_palace['major_stars']) if soul_palace and soul_palace.get('major_stars') else '空宫'

        current_decadal_branch = ''
        current_decadal_display = ''
        for p in chart_data.get('palaces', []):
            if p.get('decadal_range') and '-' in p.get('decadal_range', ''):
                try:
                    start = int(p['decadal_range'].split('-')[0])
                    if 20 <= start <= 40:
                        current_decadal = p
                        current_decadal_branch = p['earthly_branch']
                        current_decadal_display = f"{p['earthly_branch']}宫·{'·'.join(p['major_stars'])}" if p.get('major_stars') else f"{p['earthly_branch']}宫"
                        break
                except:
                    pass

        cards = [
            {
                "title": "命盘底色 · 先天禀赋",
                "badge": soul_stars,
                "full": True,
                "highlight": True,
                "body": f"<strong>你的命宫主星是{soul_stars}</strong>，这个组合的核心气质是「思维敏捷，善于谋划」。<br><br>你是那种脑子里永远有想法的人——遇到问题第一反应不是逃避，是绕着问题转三圈，然后找出一条别人想不到的路。<br><br><em>优势：</em>领悟力强，学东西快，善于从复杂局面里抓住重点。<br><span class='warn'>注意：</span>想得多做得少，容易在选择里内耗。",
                "probabilities": [
                    {"label": "推算置信度", "pct": 70},
                    {"label": "校准后可达", "pct": 88}
                ]
            },
            {
                "title": "事业格局",
                "badge": '·'.join(career_palace['major_stars']) if career_palace and career_palace.get('major_stars') else '空宫',
                "body": "你的事业格局属于「主动开创型」。不适合在一个地方熬资历，更适合靠自己的本事吃饭——创业、做专家、或者在团队里负责一块独立的业务。<br><br><span class='good'>适合方向：</span>策划、咨询、技术、创业、自媒体",
                "probabilities": [
                    {"label": "匹配度", "pct": 75}
                ]
            },
            {
                "title": "财运模式",
                "badge": '·'.join(wealth_palace['major_stars']) if wealth_palace and wealth_palace.get('major_stars') else '空宫',
                "body": "你的财运不是省出来的，是挣出来的。财帛宫的配置说明你对钱有概念，但不是那种一分钱掰两半花的人。<br><br>说白了：你赚钱的能力比存钱的能力强。钱来了能接住，但是留不留得住，看你有没有主动去规划。",
                "probabilities": [
                    {"label": "赚钱能力", "pct": 78},
                    {"label": "守财能力", "pct": 60}
                ]
            },
            {
                "title": "感情模式",
                "badge": '·'.join(love_palace['major_stars']) if love_palace and love_palace.get('major_stars') else '空宫',
                "body": "你在感情里看重「精神共鸣」。颜值、经济条件这些都是基础门槛，过了门槛之后，能不能聊到一块儿去才是关键。<br><br><span class='warn'>提醒：</span>不要因为对方对你好就在一起，你真正需要的是「懂你」的人。"
            },
            {
                "title": "当前大限 · 核心课题",
                "badge": current_decadal_display if current_decadal_display else '进行中',
                "full": True,
                "teal": True,
                "body": f"<strong>这十年（{current_decadal['decadal_range'] if current_decadal else '---'}）的核心课题是：找到自己真正想做的事。</strong><br><br>这不是一个求安稳的阶段。你会发现自己越来越不满足于「就这么过下去」，总想做点什么不一样的。<br><br><span class='good'>机遇：</span>遇到贵人、找到新方向、能力跃迁<br><span class='warn'>注意：</span>不要急躁，每一步踩实了再走",
                "probabilities": [
                    {"label": "关键程度", "pct": 90}
                ]
            }
        ]

        calibration_questions = [
            {
                "text": "目前从事的行业或工作性质是？",
                "options": ["互联网/科技", "教育/学术", "金融/商业", "自由职业", "其他"]
            },
            {
                "text": "感情状态如何？",
                "options": ["单身", "恋爱中", "已婚", "其他"]
            },
            {
                "text": "近1-2年有没有明显的转折或压力事件？",
                "options": ["换工作", "搬家", "关系变化", "学业/考试", "没有明显变化"]
            },
            {
                "text": "你最困扰的事情是什么领域的？",
                "options": ["事业发展", "感情婚姻", "财运", "健康", "人际关系"]
            },
        ]

        return {
            "current_decadal_branch": current_decadal_branch,
            "current_decadal_display": current_decadal_display,
            "cards": cards,
            "calibration_questions": calibration_questions
        }

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        return "这是 Mock 模式的八字解读示例。\n\n你的命盘日主为戊土，生于夏季，土气偏旺。性格稳重踏实，做事有耐心，善于积累财富。\n\n事业上适合从事稳定的行业，不宜冒险投机。财运稳步上升，但需注意理财规划。\n\n感情方面，你对感情认真负责，一旦认定就会全心投入。健康上注意脾胃和消化系统。\n\n近期运势平稳，是蓄势待发的阶段，宜稳中求进。"


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def generate_reading(self, chart_data: Dict[str, Any], style: str = "friendly", sections: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url) if self.base_url else openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ValueError("openai package not installed")

        prompt = self._build_prompt(chart_data, style, sections)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位资深的紫微斗数命理咨询师，擅长用通俗的语言解读命盘。解读要有温度、有主见，用朋友聊天的语气，不要用教科书式的表述。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        content = response.choices[0].message.content
        return self._parse_response(content, chart_data)

    def _build_prompt(self, chart_data: Dict[str, Any], style: str, sections: Optional[List[str]]) -> str:
        return f"""
请根据以下紫微斗数排盘数据，生成一份命盘解读报告。

排盘数据：
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

解读风格：{style}（friendly=轻松朋友式 / formal=正式专业式 / direct=直话直说式）

请按以下 JSON 格式返回（不要有其他文字，只返回 JSON）：
{{
  "current_decadal_branch": "当前大限地支，如'辰'",
  "current_decadal_display": "当前大限展示文字",
  "cards": [
    {{
      "title": "章节标题",
      "badge": "主星名称",
      "full": true,
      "highlight": true,
      "teal": false,
      "body": "解读正文HTML，支持 <strong>白色强调</strong> <em>金色强调</em> <span class='warn'>橙色警告</span> <span class='good'>绿色利好</span> <br>换行",
      "probabilities": [
        {{"label": "置信度", "pct": 70}}
      ]
    }}
  ],
  "calibration_questions": [
    {{"text": "问题", "options": ["选项1", "选项2"]}}
  ]
}}

要求：
1. 至少包含5张卡片：命盘底色、事业、财运、感情、当前大限
2. 命盘底色和当前大限用 full:true 全宽卡片
3. 命盘底色用 highlight:true 红框高亮，当前大限用 teal:true 青框高亮
4. 每个卡片都要有正文和自己的判断
5. 校准问题3-5个，每个问题带 options 选项数组
"""

    def _parse_response(self, content: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])
        except:
            mock = MockAIProvider()
            return mock.generate_reading(chart_data)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=120) if self.base_url else openai.OpenAI(api_key=self.api_key, timeout=120)
        except ImportError:
            raise ValueError("openai package not installed")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content


class VolcengineProvider(AIProvider):
    """火山方舟（豆包大模型） - OpenAI 兼容模式"""

    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, api_key: str, model: str = "doubao-pro-32k", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or self.BASE_URL

    def generate_reading(self, chart_data: Dict[str, Any], style: str = "friendly", sections: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            raise ValueError("openai package not installed")

        prompt = self._build_prompt(chart_data, style, sections)
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的紫微斗数命理咨询师，擅长用通俗的语言解读命盘。解读要有温度、有主见，用朋友聊天的语气，不要用教科书式的表述。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )
            content = response.choices[0].message.content
            return self._parse_response(content, chart_data)
        except Exception as e:
            raise ValueError(f"火山方舟调用失败: {str(e)}")

    def _build_prompt(self, chart_data: Dict[str, Any], style: str, sections: Optional[List[str]]) -> str:
        return f"""
请根据以下紫微斗数排盘数据，生成一份命盘解读报告。

排盘数据：
{json.dumps(chart_data, ensure_ascii=False, indent=2)}

解读风格：{style}（friendly=轻松朋友式 / formal=正式专业式 / direct=直话直说式）

请按以下 JSON 格式返回（不要有其他文字，只返回 JSON）：
{{
  "current_decadal_branch": "当前大限地支，如'辰'",
  "current_decadal_display": "当前大限展示文字",
  "cards": [
    {{
      "title": "章节标题",
      "badge": "主星名称",
      "full": true,
      "highlight": true,
      "teal": false,
      "body": "解读正文HTML，支持 <strong>白色强调</strong> <em>金色强调</em> <span class='warn'>橙色警告</span> <span class='good'>绿色利好</span> <br>换行",
      "probabilities": [
        {{"label": "置信度", "pct": 70}}
      ]
    }}
  ],
  "calibration_questions": [
    {{"text": "问题", "options": ["选项1", "选项2"]}}
  ]
}}

要求：
1. 至少包含5张卡片：命盘底色、事业、财运、感情、当前大限
2. 命盘底色和当前大限用 full:true 全宽卡片
3. 命盘底色用 highlight:true 红框高亮，当前大限用 teal:true 青框高亮
4. 每个卡片都要有正文和自己的判断
5. 校准问题3-5个，每个问题带 options 选项数组
"""

    def _parse_response(self, content: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])
        except:
            mock = MockAIProvider()
            return mock.generate_reading(chart_data)

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=120)
        except ImportError:
            raise ValueError("openai package not installed")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content


# 火山方舟默认配置（全局默认 AI 服务）
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_API_KEY = "ark-5fdd8a51-478e-49e8-aebb-46b8e03af7d8-2cd0f"
DEFAULT_MODEL = "ark-code-latest"
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"


def get_ai_provider(provider: str = None, **kwargs) -> AIProvider:
    # 如果没指定 provider 或是 mock，使用默认火山方舟配置
    if not provider or provider == "mock":
        provider = DEFAULT_AI_PROVIDER

    # 获取 API Key，如果用户没配就用默认的
    api_key = kwargs.get("api_key") or DEFAULT_API_KEY
    model = kwargs.get("model") or DEFAULT_MODEL
    base_url = kwargs.get("base_url") or DEFAULT_BASE_URL

    if provider == "openai":
        return OpenAIProvider(
            api_key=api_key,
            base_url=base_url,
            model=model
        )
    elif provider == "volcengine":
        return VolcengineProvider(
            api_key=api_key,
            model=model,
            base_url=base_url
        )
    else:
        return MockAIProvider()
