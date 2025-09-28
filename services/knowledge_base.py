import json
import os
import requests
from typing import List, Dict, Any
import faiss
import numpy as np
from config import Config

# 尝试导入sentence_transformers，如果失败则使用备用方案
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("警告: sentence_transformers 不可用，将使用简单的关键词匹配")

class KnowledgeBase:
    """知识库管理类"""
    
    def __init__(self):
        self.config = Config()
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.document_embeddings = []
        
        # 初始化embedding模型（使用本地缓存）
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("🔄 正在加载文本向量化模型...")
                print("📦 模型名称: paraphrase-multilingual-MiniLM-L12-v2")
                print("⏳ 请稍候，首次加载可能需要几分钟...")
                
                # 添加进度提示
                import time
                start_time = time.time()
                
                # 设置环境变量强制使用本地缓存
                import os
                cache_dir = os.path.join(os.getcwd(), 'model_cache')
                os.makedirs(cache_dir, exist_ok=True)
                os.environ['TRANSFORMERS_CACHE'] = cache_dir
                os.environ['HF_HOME'] = cache_dir
                os.environ['HF_HUB_OFFLINE'] = '1'  # 强制离线模式
                
                # 尝试从本地缓存加载模型
                local_model_path = "~/.cache/huggingface/hub/models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2/snapshots/86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d"
                
                if os.path.exists(local_model_path):
                    print(f"📁 使用本地模型路径: {local_model_path}")
                    try:
                        self.embedding_model = SentenceTransformer(local_model_path)
                        end_time = time.time()
                        load_time = end_time - start_time
                        print(f"✅ 文本向量化模型加载成功！耗时: {load_time:.2f}秒")
                    except Exception as local_error:
                        print(f"⚠️ 本地路径加载失败: {local_error}")
                        print("尝试使用模型名称加载...")
                        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                        end_time = time.time()
                        load_time = end_time - start_time
                        print(f"✅ 文本向量化模型加载成功！耗时: {load_time:.2f}秒")
                else:
                    print("⚠️ 本地模型路径不存在，尝试从网络加载...")
                    os.environ['HF_HUB_OFFLINE'] = '0'  # 允许网络连接
                    self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                    end_time = time.time()
                    load_time = end_time - start_time
                    print(f"✅ 文本向量化模型加载成功！耗时: {load_time:.2f}秒")
                    
            except Exception as e:
                print(f"⚠️ 模型加载失败: {e}")
                print("将使用简单的关键词匹配模式")
                self.embedding_model = None
        else:
            print("⚠️ sentence_transformers 不可用，将使用简单的关键词匹配")
            self.embedding_model = None
        
    def load_knowledge_base(self):
        """加载知识库数据"""
        print("📚 开始加载知识库...")
        knowledge_path = self.config.KNOWLEDGE_BASE_PATH
        
        # 加载FAQ知识库
        faq_path = os.path.join(knowledge_path, "product_faq.json")
        if os.path.exists(faq_path):
            print("📖 加载FAQ知识库...")
            with open(faq_path, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
                self._process_faq_data(faq_data)
            print(f"✅ FAQ知识库加载完成，共 {len(faq_data.get('faqs', []))} 个问题")
        else:
            print("⚠️ FAQ知识库文件不存在")
        
        # 加载商品分类知识库
        category_path = os.path.join(knowledge_path, "product_categories.json")
        if os.path.exists(category_path):
            print("🏷️ 加载商品分类知识库...")
            with open(category_path, 'r', encoding='utf-8') as f:
                category_data = json.load(f)
                self._process_category_data(category_data)
            print(f"✅ 商品分类知识库加载完成，共 {len(category_data.get('categories', []))} 个分类")
        else:
            print("⚠️ 商品分类知识库文件不存在")
        
        # 构建向量索引
        print("🔍 构建知识库索引...")
        self._build_vector_index()
        print("✅ 知识库加载完成！")
    
    def _process_faq_data(self, faq_data: Dict[str, Any]):
        """处理FAQ数据"""
        for faq in faq_data.get('faqs', []):
            # 创建文档内容
            content = f"问题：{faq['question']}\n答案：{faq['answer']}\n分类：{faq['category']}"
            
            # 添加关键词
            if 'keywords' in faq:
                content += f"\n关键词：{', '.join(faq['keywords'])}"
            
            self.documents.append({
                'content': content,
                'type': 'faq',
                'category': faq.get('category', ''),
                'question': faq['question'],
                'answer': faq['answer']
            })
    
    def _process_category_data(self, category_data: Dict[str, Any]):
        """处理商品分类数据"""
        for category in category_data.get('categories', []):
            category_name = category['name']
            
            for subcategory in category.get('subcategories', []):
                subcategory_name = subcategory['name']
                keywords = subcategory.get('keywords', [])
                common_questions = subcategory.get('common_questions', [])
                
                # 创建分类文档
                content = f"商品分类：{category_name} - {subcategory_name}\n"
                content += f"相关商品：{', '.join(keywords)}\n"
                content += f"常见问题：{', '.join(common_questions)}"
                
                self.documents.append({
                    'content': content,
                    'type': 'category',
                    'category': category_name,
                    'subcategory': subcategory_name,
                    'keywords': keywords,
                    'common_questions': common_questions
                })
    
    def _build_vector_index(self):
        """构建向量索引"""
        if not self.documents:
            return
        
        # 如果没有embedding模型，使用简单的关键词匹配
        if self.embedding_model is None:
            print("使用简单关键词匹配模式")
            return
        
        try:
            # 提取文档内容
            texts = [doc['content'] for doc in self.documents]
            print(f"📝 处理 {len(texts)} 个文档...")
            
            # 生成嵌入向量
            print("🧠 生成文本向量...")
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            self.document_embeddings = embeddings
            print(f"✅ 向量化完成！生成 {embeddings.shape[0]} 个向量，维度: {embeddings.shape[1]}")
            
            # 暂时跳过FAISS索引，直接使用向量相似度计算
            print("🔍 使用余弦相似度计算模式")
        except Exception as e:
            print(f"⚠️ 向量化失败: {e}")
            print("将使用简单关键词匹配模式")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关知识"""
        if not self.documents:
            return []
        
        # 如果没有向量索引，使用关键词匹配
        if self.index is None or self.embedding_model is None:
            return self._keyword_search(query, top_k)
        
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)
            
            # 计算余弦相似度
            results = []
            for i, doc in enumerate(self.documents):
                if self.document_embeddings is not None and i < len(self.document_embeddings):
                    doc_embedding = self.document_embeddings[i]
                    # 计算余弦相似度
                    similarity = np.dot(query_embedding[0], doc_embedding) / (
                        np.linalg.norm(query_embedding[0]) * np.linalg.norm(doc_embedding)
                    )
                    result = doc.copy()
                    result['similarity_score'] = float(similarity)
                    results.append(result)
            
            # 按相似度排序并返回top_k
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results[:top_k]
        except Exception as e:
            print(f"向量搜索失败，使用关键词匹配: {e}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """简单的关键词搜索"""
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            score = 0
            
            # 计算关键词匹配度
            for word in query_lower.split():
                if word in content_lower:
                    score += 1
            
            if score > 0:
                result = doc.copy()
                result['similarity_score'] = score / len(query.split())
                results.append(result)
        
        # 按分数排序并返回top_k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:top_k]
    
    def get_context_for_query(self, query: str, max_context_length: int = 1000) -> str:
        """获取查询相关的上下文信息"""
        search_results = self.search(query, top_k=3)
        
        context_parts = []
        current_length = 0
        
        for result in search_results:
            if result['type'] == 'faq':
                context_part = f"FAQ - {result['question']}: {result['answer']}"
            else:
                context_part = f"商品分类信息: {result['content']}"
            
            if current_length + len(context_part) <= max_context_length:
                context_parts.append(context_part)
                current_length += len(context_part)
            else:
                break
        
        return "\n\n".join(context_parts)
    
    def add_custom_knowledge(self, content: str, knowledge_type: str = "custom", **kwargs):
        """添加自定义知识"""
        document = {
            'content': content,
            'type': knowledge_type,
            **kwargs
        }
        
        self.documents.append(document)
        
        # 重新构建索引
        self._build_vector_index()
    
    def download_external_knowledge(self):
        """下载外部知识库"""
        for url in self.config.TAOBAO_KNOWLEDGE_URLS:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # 根据数据结构处理
                    if 'faqs' in data:
                        self._process_faq_data(data)
                    elif 'categories' in data:
                        self._process_category_data(data)
            except Exception as e:
                print(f"下载知识库失败 {url}: {e}")
    
    def save_knowledge_base(self, filepath: str):
        """保存知识库到文件"""
        data = {
            'documents': self.documents,
            'embeddings': self.document_embeddings if self.document_embeddings is not None else None
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_knowledge_base_from_file(self, filepath: str):
        """从文件加载知识库"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.documents = data.get('documents', [])
            embeddings_data = data.get('embeddings')
            
            if embeddings_data:
                self.document_embeddings = np.array(embeddings_data)
                self._build_vector_index() 