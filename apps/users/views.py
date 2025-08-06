from django.shortcuts import render
from django.contrib.auth.decorators import login_required  
from django.shortcuts import render, redirect  
from .forms import ProfileUpdateForm  
from django.contrib.auth.management.commands.changepassword import UserModel
from django.http import JsonResponse, HttpResponse
from PIL import Image
import os
from io import BytesIO
from py2neo import Graph
from django.http import Http404

from django.conf import settings
import time
from django.contrib import messages  # 添加消息框架
import logging
logger = logging.getLogger(__name__)

graph = Graph("bolt://localhost:7687", auth=("neo4j", "12345678"))
def get_neo4j_data(request):  # 获取neo4j的节点（除了labels为Course的节点）
    print("--------------------------------------------------------------------------------------------------")  # 调试信息
    search_term = request.GET.get('search', '').strip()

    nodes = []
    edges = []

    # 基础查询
    node_query = '''
        MATCH (n)
        WHERE NOT 'Course' IN labels(n)
        RETURN id(n) AS id, n.name AS name, labels(n) AS labels'''
    edge_query = "MATCH (n)-[r]->(m) RETURN id(r) AS id, id(n) AS source, id(m) AS target, type(r) AS type"

    if search_term:
        # 搜索匹配节点及其子节点
        node_query = f"""
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower('{search_term}')
        WITH collect(n) AS matchedNodes
        UNWIND matchedNodes AS n
        MATCH path=(m)-[*0..3]->(n)
        UNWIND nodes(path) AS node
        RETURN DISTINCT id(node) AS id, node.name AS name, labels(node) AS labels
        """

        edge_query = f"""
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower('{search_term}')
        WITH collect(n) AS matchedNodes
        UNWIND matchedNodes AS n
        MATCH path=(m)-[r*0..3]->(n)
        UNWIND relationships(path) AS rel
        RETURN DISTINCT id(rel) AS id, id(startNode(rel)) AS source, id(endNode(rel)) AS target, type(rel) AS type
        """

    # 执行查询
    node_results = graph.run(node_query)
    for record in node_results:
        nodes.append({
            "id": record["id"],
            "name": record["name"],
            "type": record["labels"][0] if record["labels"] else "default"
        })
        print("search_node: ", record)  # 调试信息

    print(nodes)

    edge_results = graph.run(edge_query)
    for record in edge_results:
        edges.append({
            "id": record["id"],
            "from": record["source"],
            "to": record["target"],
            "type": record["type"]
        })
        print("search_edge: ", record)  # 调试信息

    if not nodes:  # 无结果时
        print(f"未找到包含'{search_term}'的节点")
        return JsonResponse({
            "nodes": [],
            "edges": [],
            "message": f"未找到包含'{search_term}'的节点"
        }, status=200)

    return JsonResponse({"nodes": nodes, "edges": edges, "search_term": search_term})

def click_node(request):
    node_id = request.GET.get('node_id')
    if not node_id or not node_id.isdigit():
        raise Http404("无效的节点ID")

    query = """
        MATCH (n) WHERE ID(n) = $node_id
        OPTIONAL MATCH (n)<-[:SUB_TOPIC_OF*0..2]-(midNode)<-[:BELONGS_TO]-(course:Course)
        RETURN n, COLLECT(DISTINCT course) AS courses
        """

    result = graph.run(query, node_id=int(node_id)).data()

    if not result:
        raise Http404("节点不存在")

    data = result[0]
    return render(request, 'click-node.html', {
        'current_node': dict(data['n']),
        'courses': [dict(course) for course in data['courses']]
    })

def home_view(request):
    """主页视图函数"""
    return render(request, 'home.html')

@login_required  
def profile_view(request):  
    # 获取当前登录用户的资料
    profile = request.user.profile
    print('[后端] 请求方法:', request.method)
    print('[后端] FILES键:', request.FILES.keys())  # 应显示 dict_keys(['avatar'])
    print('[后端] POST参数:', request.POST.keys())  # 应包含x,y,width,height
    logger.info('[后端] 1. 接收到请求: %s %s', request.method, request.path)
    if request.method == 'POST' and 'avatar' in request.FILES:

        logger.info('[后端] 2. 检测到头像上传请求')
        try:
        
            # 获取原始图片和裁剪参数
            image = Image.open(request.FILES['avatar'])
            x = float(request.POST.get('x'))
            y = float(request.POST.get('y'))
            width = float(request.POST.get('width'))
            height = float(request.POST.get('height'))
            
            
            # 关键修复：将RGBA转换为RGB（移除透明通道）
            if image.mode in ('RGBA', 'LA'):
                background = Image.new(image.mode[:-1], image.size, (255, 255, 255))  # 白色背景
                background.paste(image, image.split()[-1])
                image = background

           
            beta_path = os.path.join(settings.MEDIA_ROOT, 'beta', f'{request.user.id}.jpg')
            image.save(beta_path, 'JPEG', quality=90, optimize=True)  # 90%质量+优化

            # 获取裁剪参数并验证
            x = request.POST.get('x')
            y = request.POST.get('y')
            width = request.POST.get('width')
            height = request.POST.get('height')
            logger.info(f'[裁剪参数] x={x}, y={y}, width={width}, height={height}')
            
            # 转换为数字并验证
            x = float(x)
            y = float(y)
            width = float(width)
            height = float(height)

            # 只有提供了裁剪参数才进行裁剪
            if x and y and width and height:
                x = int(float(x))
                y = int(float(y))
                width = int(float(width))
                height = int(float(height))
                
                logger.info(f'[原始图片] 尺寸: {image.size} (宽x高)')
            
            
            
            # 检查裁剪区域是否超出图片边界
            max_width, max_height = image.size
            logger.info(f'[边界检查] 裁剪区域右下角: ({x+width}, {y+height}), 图片最大尺寸: ({max_width}, {max_height})')
            
            if x < 0 or y < 0 or (x + width) > max_width or (y + height) > max_height:
                logger.error('[裁剪错误] 裁剪区域超出图片边界！')
                # 强制调整到有效区域
                x = max(0, x)
                y = max(0, y)
                width = min(width, max_width - x)
                height = min(height, max_height - y)
                logger.info(f'[调整后参数] x={x}, y={y}, width={width}, height={height}')
                # 后端裁剪原始图片

            cropped_image = image.crop((x, y, x + width, y + height))
            
            
            # 保存图片（高画质设置）
            avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', f'{request.user.id}.jpg')
            cropped_image.save(avatar_path, 'JPEG', quality=90, optimize=True)  # 90%质量+优化
            
            # 更新用户头像时添加随机参数避免缓存 错误的
            # 移除URL参数，只保存纯净路径
            #虽然不知道为什么注释掉以下两行就没问题了但是跑起来了管他呢
            #request.user.profile.avatar = f'avatars/{request.user.id}.jpg'  # 移除?{time.time()}
            #request.user.profile.save()
            
            # 添加成功消息
            messages.success(request, '头像更新成功！')
            return redirect('users:profile')

        except Exception as e:
            logger.error('[后端] 错误详情: %s', str(e), exc_info=True)
            # 添加错误消息（用户可见）
            messages.error(request, f'头像上传失败：{str(e)[:50]}')
            return redirect('users:profile')  # 重定向回表单页
    else:
        print('[后端] 未进入分支原因:', 
              '方法不是POST' if request.method != 'POST' else 'avatar不在FILES中')

    if request.method == 'POST':
        # 用户提交表单时处理
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # 保存修改
            return redirect('users:profile')  # 刷新页面
    else:
        # 首次访问时显示表单
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'users/profile.html', {
        'form': form,
        'user': request.user
    })

