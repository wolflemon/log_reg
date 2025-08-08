from py2neo import Graph
import logging
from datetime import datetime

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Neo4jTester")

class Neo4jQueryTester:
    def __init__(self, neo4j_uri="bolt://localhost:7687", neo4j_user="neo4j", neo4j_password="123456789", test_user_id="1"):
        """初始化Neo4j连接"""
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.graph = None
        self.test_user_id = test_user_id  # 替换为你的测试用户ID（字符串类型）

    def connect(self):
        """连接Neo4j数据库"""
        try:
            self.graph = Graph(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # 测试连接
            self.graph.run("MATCH () RETURN 1 LIMIT 1")
            logger.info("✅ 成功连接到Neo4j数据库")
            return True
        except Exception as e:
            logger.error(f"❌ 连接Neo4j失败: {str(e)}")
            return False

    def test_basic_node_query(self):
        """测试基础节点查询（获取所有节点）"""
        logger.info("\n=== 测试基础节点查询 ===")
        query = """
        MATCH (n) 
        RETURN id(n) AS id, n.name AS name, labels(n) AS labels 
        ORDER BY id(n) 
        LIMIT 10
        """
        try:
            results = self.graph.run(query).data()
            if not results:
                logger.warning("⚠️ 基础节点查询未返回任何结果（数据库可能为空）")
            else:
                logger.info(f"✅ 找到 {len(results)} 个节点:")
                for i, node in enumerate(results[:5], 1):  # 显示前5个
                    logger.info(f"  {i}. ID: {node['id']}, 名称: {node['name']}, 标签: {node['labels']}")
            return results
        except Exception as e:
            logger.error(f"❌ 基础节点查询失败: {str(e)}")
            return None

    def test_user_graph_query(self):
        """测试用户图谱查询（模拟前端调用的接口逻辑）"""
        logger.info("\n=== 测试用户图谱查询 ===")
        query = """
        MATCH (r:Root)-[:OWNED]->(u:User {user_id: $user_id})
        OPTIONAL MATCH (n)-[:SUB_TOPIC_OF|BELONGS_TO|SELF_DEFINE_REL*]->(r)
        WITH r, collect(n) AS subNodes
        UNWIND [r] + subNodes AS node
        WITH node WHERE NOT 'Course' IN labels(node)
        RETURN DISTINCT id(node) AS id, node.name AS name, labels(node) AS labels
        """
        try:
            results = self.graph.run(query, user_id=self.test_user_id).data()
            logger.info(f"🔍 查询用户 {self.test_user_id} 的图谱节点:")
            if not results:
                logger.error("❌ 用户图谱查询未返回任何节点（可能用户Root节点未创建）")
            else:
                logger.info(f"✅ 找到 {len(results)} 个用户节点:")
                for i, node in enumerate(results[:5], 1):
                    logger.info(f"  {i}. ID: {node['id']}, 名称: {node['name']}, 标签: {node['labels']}")
            return results
        except Exception as e:
            logger.error(f"❌ 用户图谱查询失败: {str(e)}")
            return None

    def test_relationship_query(self):
        """测试关系查询（验证节点间关联）"""
        logger.info("\n=== 测试关系查询 ===")
        query = """
        MATCH (n)-[r]->(m) 
        RETURN 
            id(r) AS rel_id,
            id(n) AS from_id, n.name AS from_name,
            type(r) AS rel_type,
            id(m) AS to_id, m.name AS to_name
        LIMIT 5
        """
        try:
            results = self.graph.run(query).data()
            if not results:
                logger.warning("⚠️ 关系查询未返回任何结果（可能无节点关系）")
            else:
                logger.info(f"✅ 找到 {len(results)} 个关系:")
                for i, rel in enumerate(results, 1):
                    logger.info(f"  {i}. {rel['from_name']} -[{rel['rel_type']}]-> {rel['to_name']}")
            return results
        except Exception as e:
            logger.error(f"❌ 关系查询失败: {str(e)}")
            return None

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("\n===== Neo4j查询测试开始 =====")
        if not self.connect():
            return
            
        self.test_basic_node_query()
        user_nodes = self.test_user_graph_query()
        self.test_relationship_query()

        if user_nodes and len(user_nodes) > 0:
            logger.info("\n===== 测试总结 =====")
            logger.info("✅ 用户图谱数据存在，前端应能渲染图谱")
        else:
            logger.info("\n===== 测试总结 =====")
            logger.error("❌ 用户图谱数据缺失，请检查用户初始化逻辑")

if __name__ == "__main__":
    # 初始化测试器（替换为你的Neo4j密码和测试用户ID）
    tester = Neo4jQueryTester(
        neo4j_password="123456789",  # 替换为你的密码
        test_user_id="7"  # 替换为测试用户的ID（字符串类型）
    )
    tester.run_all_tests()