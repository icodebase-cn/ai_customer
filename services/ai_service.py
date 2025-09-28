import asyncio
import base64
import io
import json
import logging
import time
from typing import Any, Dict, List, Optional

import openai
from PIL import Image

from config import Config  # 确保Config可用
from prompts.chinese_prompts import ChinesePrompts
from prompts.english_prompts import EnglishPrompts
from prompts.hindi_prompts import HindiPrompts
from services.knowledge_base import KnowledgeBase


class AIService:
    """AI服务类，处理文字和图片查询"""

    def __init__(self):
        print("🤖 初始化AI服务...")
        self.config = Config()
        self.logger = logging.getLogger(__name__)

        print("🔧 初始化API客户端...")

        print(f"✅ 使用API: {self.config.TEXT_MODEL}")
        self.client = openai.OpenAI(
            api_key=self.config.AIQIANJI_API_KEY,
            base_url=self.config.AIQIANJI_BASE_URL
        )

        print("📚 初始化知识库...")
        # 初始化知识库
        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load_knowledge_base()

        # 对话历史管理
        self.conversation_history = []
        self.max_history_length = 10  # 保留最近10轮对话

        print("✅ AI服务初始化完成！")

    def add_to_conversation_history(self, role: str, content: str, image_data: Optional[bytes] = None):
        """添加对话到历史记录"""
        conversation_item = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "has_image": image_data is not None
        }

        self.conversation_history.append(conversation_item)

        # 保持历史记录在合理长度内
        if len(self.conversation_history) > self.max_history_length * 2:  # 用户和AI各一条
            self.conversation_history = self.conversation_history[-self.max_history_length * 2:]

    def get_conversation_context(self) -> str:
        """获取对话上下文"""
        if not self.conversation_history:
            return ""

        context_parts = []
        for item in self.conversation_history[-6:]:  # 只取最近6条记录
            role_name = "用户" if item["role"] == "user" else "助手"
            context_parts.append(f"{role_name}: {item['content']}")

        return "\n".join(context_parts)

    def process_text_query(self, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """处理文字查询"""
        try:
            # 从知识库获取相关上下文
            knowledge_context = self.knowledge_base.get_context_for_query(user_question)

            # 获取对话历史上下文
            conversation_context = self.get_conversation_context()

            # 根据语言选择提示词
            if lang == 'zh':
                prompt_cls = ChinesePrompts
            elif lang == 'en':
                prompt_cls = EnglishPrompts
            elif lang == 'hi':
                prompt_cls = HindiPrompts
            else:
                prompt_cls = ChinesePrompts  # 默认使用中文

            # 构建提示词 - 添加用户信息
            prompt = prompt_cls.get_prompt_by_type(
                "text_chat",
                user_question=user_question,
                user_info=user_info,  # 新增用户信息参数
                knowledge_context=knowledge_context,
                conversation_context=conversation_context
            )

            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
                extra_body={"chat_template_kwargs": {"thinking": False}}
            )

            answer = response.choices[0].message.content

            # 添加到对话历史
            self.add_to_conversation_history("user", user_question or "")
            self.add_to_conversation_history("assistant", answer or "")

            return {
                "success": True,
                "answer": answer,
                "knowledge_context": knowledge_context,
                "model_used": self.config.TEXT_MODEL,
                "conversation_length": len(self.conversation_history)
            }

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error processing text query: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "answer": "抱歉，处理您的问题时出现了错误，请稍后重试。"
            }

    def process_image_query(self, image_data: bytes, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """处理图片查询"""
        try:
            # 处理图片
            try:
                image = Image.open(io.BytesIO(image_data))
                if image.format.lower() not in [fmt.strip('.') for fmt in Config.SUPPORTED_IMAGE_FORMATS]:
                    raise ValueError(f"不支持的图片格式: {image.format}")
            except Exception as e:
                print(f"❌ 图片处理失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"图片处理失败: {str(e)}",
                    "answer": "抱歉，无法处理您上传的图片，请检查图片格式是否正确"
                }

            # 压缩图片以符合API要求
            try:
                image = self._resize_image(image)
            except Exception as e:
                print(f"❌ 图片压缩失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"图片压缩失败: {str(e)}",
                    "answer": "抱歉，处理图片时出现错误"
                }

            # 转换为base64
            try:
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG" if image.format.lower() in ['jpg', 'jpeg'] else image.format)
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
            except Exception as e:
                print(f"❌ 图片编码失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"图片编码失败: {str(e)}",
                    "answer": "抱歉，处理图片时出现错误"
                }

            # 从知识库获取相关上下文
            knowledge_context = self.knowledge_base.get_context_for_query(user_question)

            # 获取对话历史上下文
            conversation_context = self.get_conversation_context()

            # 根据语言选择提示词
            if lang == 'zh':
                prompt_cls = ChinesePrompts
            elif lang == 'en':
                prompt_cls = EnglishPrompts
            elif lang == 'hi':
                prompt_cls = HindiPrompts
            else:
                prompt_cls = ChinesePrompts  # 默认使用中文

            # 根据语言设置图片描述
            image_desc = "用户上传的商品图片"
            if lang == 'en':
                image_desc = "User uploaded product image"
            elif lang == 'hi':
                image_desc = "उपयोगकर्ता द्वारा अपलोड की गई उत्पाद छवि"

            # 构建提示词 - 添加用户信息
            prompt = prompt_cls.get_prompt_by_type(
                "image_analysis",
                image_description=image_desc,
                user_question=user_question,
                user_info=user_info,  # 新增用户信息参数
                conversation_context=conversation_context
            )

            # 调用OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.config.VISION_MODEL,
                messages=[
                    {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )

            answer = response.choices[0].message.content

            # 添加到对话历史
            self.add_to_conversation_history("user", f"{user_question or ''} [图片]", image_data)
            self.add_to_conversation_history("assistant", answer or "")

            return {
                "success": True,
                "answer": answer,
                "knowledge_context": knowledge_context,
                "model_used": self.config.VISION_MODEL,
                "image_processed": True,
                "conversation_length": len(self.conversation_history)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "抱歉，处理图片时出现了错误，请检查图片格式或稍后重试。"
            }

    def _resize_image(self, image: Image.Image, max_size: int = 1024) -> Image.Image:
        """调整图片大小"""
        # 获取图片尺寸
        width, height = image.size

        # 如果图片太大，按比例缩小
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return image

    def classify_query_type(self, user_question: str) -> str:
        """分类查询类型"""
        query_lower = user_question.lower()

        # 退款售后相关
        if any(keyword in query_lower for keyword in ["退款", "退货", "换货", "质量问题", "坏了", "破损"]):
            return "after_sales"

        # 物流相关
        if any(keyword in query_lower for keyword in ["物流", "快递", "发货", "配送", "什么时候到", "快递单号"]):
            return "logistics_query"

        # 价格优惠相关
        if any(keyword in query_lower for keyword in ["价格", "优惠", "折扣", "便宜", "多少钱", "优惠券"]):
            return "price_discount"

        # 商品推荐相关
        if any(keyword in query_lower for keyword in ["推荐", "建议", "买什么", "哪个好", "选择"]):
            return "product_recommendation"

        # 默认文字对话
        return "text_chat"

    def get_local_keyword_response(self, user_question: str) -> str:
        """本地关键词兜底回复"""
        q = user_question.lower()

        # 检查是否有对话历史
        if self.conversation_history:
            last_user_msg = None
            for item in reversed(self.conversation_history):
                if item["role"] == "user":
                    last_user_msg = item["content"]
                    break

            # 如果有上下文，提供更连贯的回复
            if last_user_msg:
                if "退款" in q or "退货" in q:
                    return f"关于您提到的退款/退货问题，我可以为您详细说明流程：1. 在订单页面申请退款 2. 联系卖家协商 3. 如果卖家不同意，可以申请平台介入。您想了解哪个具体步骤？"
                elif "物流" in q or "快递" in q or "发货" in q:
                    return f"关于物流问题，让我为您解答：1. 您可以在订单页面查看物流信息 2. 如果长时间未发货，可以联系卖家 3. 如果物流异常，可以联系快递公司。您遇到什么具体问题？"
                elif "价格" in q or "优惠" in q or "便宜" in q:
                    return f"关于价格优惠，我建议您：1. 关注店铺优惠券 2. 参与平台活动 3. 使用积分抵扣 4. 等待促销活动。您想了解哪种优惠方式？"
                elif "推荐" in q or "建议" in q:
                    return f"我可以根据您的需求推荐商品，请告诉我：1. 您想买什么类型的商品？2. 您的预算范围？3. 有什么特殊要求吗？"

        # 默认回复
        if "你好" in q or "您好" in q:
            return "您好！我是多语言智能客服，很高兴为您服务！请问有什么可以帮助您的吗？"
        elif "退款" in q or "退货" in q:
            return "关于退款/退货，您可以：1. 在订单页面申请退款 2. 联系卖家协商 3. 如果卖家不同意，可以申请平台介入。请问您需要具体帮助吗？"
        elif "物流" in q or "快递" in q or "发货" in q:
            return "关于物流问题：1. 您可以在订单页面查看物流信息 2. 如果长时间未发货，可以联系卖家 3. 如果物流异常，可以联系快递公司。请问您遇到什么具体问题？"
        elif "价格" in q or "优惠" in q or "便宜" in q:
            return "关于价格优惠：1. 关注店铺优惠券 2. 参与平台活动 3. 使用积分抵扣 4. 等待促销活动。请问您想了解哪种优惠方式？"
        elif "推荐" in q or "建议" in q:
            return "我可以根据您的需求推荐商品，请告诉我：1. 您想买什么类型的商品？2. 您的预算范围？3. 有什么特殊要求吗？"
        else:
            return "感谢您的咨询！我是多语言智能客服，可以帮您解答：退款退货、物流配送、价格优惠、商品推荐等问题。请问您需要什么帮助？"

    def is_chitchat_by_model(self, user_question: str) -> bool:
        """使用AI模型判断用户输入是否为闲聊"""
        try:
            # 构建闲聊分类提示词
            chat_prompt = f"""请判断用户输入是否为闲聊（与博彩APP无关的问候、寒暄等）。如果是闲聊请回复"是"，否则回复"否"。
用户输入: {user_question}"""

            response = self.client.chat.completions.create(
                model=self.config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个分类器，只需回答'是'或'否'。"},
                    {"role": "user", "content": chat_prompt}
                ],
                max_tokens=2,
                temperature=0.0,
                extra_body={"chat_template_kwargs": {"thinking": False}}
            )

            answer = response.choices[0].message.content.strip()
            return answer == "是"
        except Exception:
            # 模型调用失败时使用本地检测
            q = user_question.strip().lower()
            chitchat_keywords = ["你好", "您好", "hi", "hello", "嗨", "早上好", "下午好", "晚上好",
                                "谢谢", "多谢", "感谢", "再见", "拜拜", "ok", "好的", "知道了",
                                "嗯", "哦", "哈哈", "嘿嘿"]
            return any(keyword in q for keyword in chitchat_keywords)

    def process_chitchat(self, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """处理闲聊查询，使用大模型自由回复"""
        try:
            # 根据语言选择提示词
            if lang == 'zh':
                prompt_cls = ChinesePrompts
            elif lang == 'en':
                prompt_cls = EnglishPrompts
            elif lang == 'hi':
                prompt_cls = HindiPrompts
            else:
                prompt_cls = ChinesePrompts  # 默认使用中文

            # 构建包含用户信息的消息
            full_question = f"{user_info}\n{user_question}" if user_info else user_question

            # 使用系统提示词但简化上下文
            messages = [
                {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                {"role": "user", "content": full_question}
            ]

            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.TEXT_MODEL,
                messages=messages,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )

            answer = response.choices[0].message.content
            return {
                "success": True,
                "answer": answer
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_enhanced_response(self, user_question: str, image_data: Optional[bytes] = None, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """获取增强回复，失败时用本地关键词兜底（并发版本）"""
        try:
            # 检查是否为闲聊
            if not image_data and self.is_chitchat_by_model(user_question):
                # 异步处理闲聊请求
                chitchat_result = await self.process_chitchat_async(user_question, lang, user_info)

                if chitchat_result["success"]:
                    answer = chitchat_result["answer"]
                    self.add_to_conversation_history("user", user_question, image_data)
                    self.add_to_conversation_history("assistant", answer)
                    return {
                        "success": True,
                        "answer": answer,
                        "chitchat": True,
                        "model_used": self.config.TEXT_MODEL,
                        "conversation_length": len(self.conversation_history)
                    }
                else:
                    # 模型调用失败时使用本地回复
                    answer = self.get_local_keyword_response(user_question)
                    self.add_to_conversation_history("user", user_question, image_data)
                    self.add_to_conversation_history("assistant", answer)
                    return {
                        "success": True,
                        "answer": answer,
                        "chitchat": True,
                        "fallback": True,
                        "error": chitchat_result["error"],
                        "conversation_length": len(self.conversation_history)
                    }

            # 并发处理图片和文本请求
            if image_data:
                return await self.process_image_query_async(image_data, user_question, lang, user_info)
            else:
                return await self.process_text_query_async(user_question, lang, user_info)

        except Exception as e:
            # 兜底本地关键词回复
            answer = self.get_local_keyword_response(user_question)
            self.add_to_conversation_history("user", user_question, image_data)
            self.add_to_conversation_history("assistant", answer)
            return {
                "success": True,
                "answer": answer,
                "fallback": True,
                "error": str(e),
                "conversation_length": len(self.conversation_history)
            }

    async def process_text_query_async(self, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """异步处理文字查询（带错误重试）"""
        # 最大重试次数和初始延迟
        max_retries = 3
        retry_delay = 1.0  # 初始延迟1秒

        for attempt in range(max_retries):
            try:
                # 并发获取知识库上下文和对话历史
                knowledge_context = self.knowledge_base.get_context_for_query(user_question)
                conversation_context = self.get_conversation_context()

                # 根据语言选择提示词
                if lang == 'zh':
                    prompt_cls = ChinesePrompts
                elif lang == 'en':
                    prompt_cls = EnglishPrompts
                elif lang == 'hi':
                    prompt_cls = HindiPrompts
                else:
                    prompt_cls = ChinesePrompts  # 默认使用中文

                # 构建提示词
                prompt = prompt_cls.get_prompt_by_type(
                    "text_chat",
                    user_question=user_question,
                    user_info=user_info,
                    knowledge_context=knowledge_context,
                    conversation_context=conversation_context
                )

                # 使用异步客户端调用API
                async_client = openai.AsyncOpenAI(
                    api_key=self.config.AIQIANJI_API_KEY,
                    base_url=self.config.AIQIANJI_BASE_URL
                )

                response = await async_client.chat.completions.create(
                    model=self.config.TEXT_MODEL,
                    messages=[
                        {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE
                )

                answer = response.choices[0].message.content

                # 添加到对话历史
                self.add_to_conversation_history("user", user_question)
                self.add_to_conversation_history("assistant", answer)

                return {
                    "success": True,
                    "answer": answer,
                    "knowledge_context": knowledge_context,
                    "model_used": self.config.TEXT_MODEL,
                    "conversation_length": len(self.conversation_history)
                }

            except openai.RateLimitError:
                # 速率限制错误 - 指数退避
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    print(f"Rate limit exceeded, retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded after retries",
                        "answer": "请求过于频繁，请稍后再试"
                    }

            except openai.APIConnectionError:
                # 连接错误 - 短暂延迟后重试
                if attempt < max_retries - 1:
                    print(f"API connection error, retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "API connection failed after retries",
                        "answer": "网络连接异常，请检查网络后重试"
                    }

            except Exception as e:
                # 其他错误直接返回
                return {
                    "success": False,
                    "error": str(e),
                    "answer": "抱歉，处理您的问题时出现了错误，请稍后重试。"
                }

    async def process_image_query_async(self, image_data: bytes, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """异步处理图片查询（带错误重试）"""
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                # 处理图片（CPU密集型操作，保持同步）
                image = Image.open(io.BytesIO(image_data))
                image = self._resize_image(image)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                # 并发获取知识库上下文和对话历史
                knowledge_context = self.knowledge_base.get_context_for_query(user_question)
                conversation_context = self.get_conversation_context()

                # 根据语言选择提示词
                if lang == 'zh':
                    prompt_cls = ChinesePrompts
                elif lang == 'en':
                    prompt_cls = EnglishPrompts
                elif lang == 'hi':
                    prompt_cls = HindiPrompts
                else:
                    prompt_cls = ChinesePrompts

                # 构建提示词
                image_desc = "用户上传的商品图片"
                if lang == 'en':
                    image_desc = "User uploaded product image"
                elif lang == 'hi':
                    image_desc = "उपयोगकर्ता द्वारा अपलोड की गई उत्पाद छवि"

                prompt = prompt_cls.get_prompt_by_type(
                    "image_analysis",
                    image_description=image_desc,
                    user_question=user_question,
                    user_info=user_info,
                    conversation_context=conversation_context
                )

                # 使用异步客户端调用API
                async_client = openai.AsyncOpenAI(
                    api_key=self.config.AIQIANJI_API_KEY,
                    base_url=self.config.AIQIANJI_BASE_URL
                )

                response = await async_client.chat.completions.create(
                    model=self.config.VISION_MODEL,
                    messages=[
                        {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE
                )
                answer = response.choices[0].message.content[0]["text"]

                # 添加到对话历史
                self.add_to_conversation_history("user", f"{user_question} [图片]", image_data)
                self.add_to_conversation_history("assistant", answer)

                return {
                    "success": True,
                    "answer": answer,
                    "knowledge_context": knowledge_context,
                    "model_used": self.config.VISION_MODEL,
                    "image_processed": True,
                    "conversation_length": len(self.conversation_history)
                }

            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    print(f"Rate limit exceeded, retrying in {delay:.1f}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded after retries",
                        "answer": "请求过于频繁，请稍后再试"
                    }

            except openai.APIConnectionError:
                if attempt < max_retries - 1:
                    print(f"API connection error, retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "API connection failed after retries",
                        "answer": "网络连接异常，请检查网络后重试"
                    }

            except Exception as e:
                print(f"API connection error, { e}")
                return {
                    "success": False,
                    "error": str(e),
                    "answer": "抱歉，处理图片时出现了错误，请检查图片格式或稍后重试。"
                }

    async def process_chitchat_async(self, user_question: str, lang: str = 'zh', user_info: Optional[str] = None) -> Dict[str, Any]:
        """异步处理闲聊查询（带错误重试）"""
        max_retries = 2  # 闲聊请求使用较少重试次数
        retry_delay = 0.5

        for attempt in range(max_retries):
            try:
                # 根据语言选择提示词
                if lang == 'zh':
                    prompt_cls = ChinesePrompts
                elif lang == 'en':
                    prompt_cls = EnglishPrompts
                elif lang == 'hi':
                    prompt_cls = HindiPrompts
                else:
                    prompt_cls = ChinesePrompts

                full_question = f"{user_info}\n{user_question}" if user_info else user_question
                messages = [
                    {"role": "system", "content": prompt_cls.SYSTEM_PROMPT},
                    {"role": "user", "content": full_question}
                ]

                # 使用异步客户端调用API
                async_client = openai.AsyncOpenAI(
                    api_key=self.config.AIQIANJI_API_KEY,
                    base_url=self.config.AIQIANJI_BASE_URL
                )

                response = await async_client.chat.completions.create(
                    model=self.config.TEXT_MODEL,
                    messages=messages,
                    max_tokens=self.config.MAX_TOKENS,
                    temperature=self.config.TEMPERATURE
                )

                answer = response.choices[0].message.content
                return {
                    "success": True,
                    "answer": answer
                }

            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded"
                    }

            except openai.APIConnectionError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    return {
                        "success": False,
                        "error": "API connection failed"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []
        return {"success": True, "message": "对话历史已清空"}

    def detect_language(self, text: str) -> str:
        """检测文本的语言

        Args:
            text: 要检测的文本

        Returns:
            语言代码 (zh, en, hi) 或 'en' 作为默认值
        """
        try:
            lang = self._detect_language_with_model(text)
            return lang
        except Exception as e:
            self.logger.error(f"语言检测失败: {str(e)}")
            return 'en'

    def _detect_language_with_model(self, text: str) -> str:
        """使用大模型检测语言"""
        try:
            # 系统提示词
            system_prompt = (
                "你是一个语言检测器。请分析用户输入的文本，并返回对应的语言代码：\n"
                "zh=中文, en=英文, hi=印地语。其他语言返回'en'。只返回语言代码。"
            )

            response = self.client.chat.completions.create(
                model=self.config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=5,
                temperature=0.0
            )

            answer = response.choices[0].message.content.strip().lower()

            # 验证返回结果
            if answer in ['zh', 'en', 'hi']:
                return answer
            return 'en'  # 默认返回英文
        except Exception as e:
            self.logger.error(f"模型语言检测失败: {str(e)}")
            return 'en'

    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        if not self.conversation_history:
            return {"success": True, "summary": "暂无对话记录"}

        try:
            # 统计对话信息
            user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
            assistant_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]

            summary = {
                "total_messages": len(self.conversation_history),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "conversation_duration": self.conversation_history[-1]["timestamp"] - self.conversation_history[0]["timestamp"] if len(self.conversation_history) > 1 else 0,
                "topics": self._extract_topics()
            }

            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_topics(self) -> List[str]:
        """提取对话主题"""
        topics = []
        all_content = " ".join([msg["content"] for msg in self.conversation_history])

        # 简单的关键词提取
        keywords = {
            "退款退货": ["退款", "退货", "换货", "质量问题"],
            "物流配送": ["物流", "快递", "发货", "配送"],
            "价格优惠": ["价格", "优惠", "折扣", "便宜"],
            "商品推荐": ["推荐", "建议", "买什么", "选择"]
        }

        for topic, words in keywords.items():
            if any(word in all_content for word in words):
                topics.append(topic)

        return topics

    def add_to_knowledge_base(self, question: str, answer: str, category: str = "custom"):
        """添加新知识到知识库"""
        try:
            self.knowledge_base.add_custom_knowledge(
                content=f"问题：{question}\n答案：{answer}",
                knowledge_type="custom",
                category=category,
                question=question,
                answer=answer
            )
            return {"success": True, "message": "知识已添加到知识库"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_knowledge_base(self, query: str, top_k: int = 5):
        """搜索知识库"""
        try:
            results = self.knowledge_base.search(query, top_k)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}