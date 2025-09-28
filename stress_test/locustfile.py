from locust import HttpUser, task, between
import random
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

class StressTestUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Run when a user starts"""
        logger.info("🚀 Virtual user started")
        
    @task(3)
    def text_chat(self):
        """Simulate text-only chat requests"""
        messages = [
            "如何办理退货？",
            "物流信息怎么查询",
            "这件商品有优惠吗",
            "推荐一款适合新手的相机",
            "How do I return an item?",
            "When will my order arrive?",
            "क्या इस उत्पाद पर कोई छूट है?"
        ]
        
        try:
            response = self.client.post(
                "/api/chat",
                data={
                    "message": random.choice(messages),
                    "language": random.choice(["zh", "en", "hi"])
                }
            )
            logger.info(f"Text chat response: {response.status_code} in {response.elapsed.total_seconds():.3f}s")
            logger.debug(f"Response content: {response.text}")
        except Exception as e:
            logger.error(f"Text chat failed: {str(e)}")
    
    @task(1)
    def image_chat(self):
        """Simulate image+text chat requests"""
        try:
            # Get absolute path to sample image
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "test_data", "sample.jpg")
            
            with open(image_path, "rb") as f:
                response = self.client.post(
                    "/api/chat",
                    files={"image": f},
                    data={
                        "message": "这个产品是什么？",
                        "language": random.choice(["zh", "en", "hi"])
                    }
                )
            logger.info(f"Image chat response: {response.status_code} in {response.elapsed.total_seconds():.3f}s")
            logger.debug(f"Response content: {response.text}")
        except Exception as e:
            logger.error(f"Image chat failed: {str(e)}")
    
    @task(2)
    def search_knowledge(self):
        """Simulate knowledge base searches"""
        queries = [
            "退货政策",
            "物流时效",
            "discount code",
            "return policy",
            "वापसी नीति"
        ]
        
        try:
            response = self.client.get(
                "/api/knowledge/search",
                params={"query": random.choice(queries), "top_k": random.randint(1, 10)}
            )
            logger.info(f"Knowledge search response: {response.status_code} in {response.elapsed.total_seconds():.3f}s")
            logger.debug(f"Response content: {response.text}")
        except Exception as e:
            logger.error(f"Knowledge search failed: {str(e)}")
