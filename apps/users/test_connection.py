from py2neo import Graph

try:
    # 替换为你的密码
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "123456789"))
    # 执行简单查询
    graph.run("MATCH () RETURN 1 LIMIT 1")
    print("✅ 成功连接到Neo4j")
except Exception as e:
    print(f"❌ 连接失败: {str(e)}")