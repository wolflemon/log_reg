# pipelines.py

import json
import os
from scrapy.exporters import JsonItemExporter

class CustomFilePipeline:
    """自定义文件输出管道"""
    
    # 爬虫与文件映射
    SPIDER_FILE_MAP = {
        "mooc": "mooc_data.json",
        "cnmooc": "cnmooc_data.json",
        "icourse": "icourse_data.json",
        "moocwang": "moocwang_data.json"
    }
    
    def open_spider(self, spider):
        """爬虫启动时创建文件"""
        self.files = {}
        self.exporters = {}
        
        # 为每个爬虫创建单独的文件
        if spider.name in self.SPIDER_FILE_MAP:
            filename = self.SPIDER_FILE_MAP[spider.name]
            file = open(filename, 'wb')
            self.files[spider.name] = file
            
            # 创建JSON导出器，添加indent参数使输出格式化
            exporter = JsonItemExporter(
                file, 
                encoding='utf-8', 
                ensure_ascii=False,
                indent=2  # 添加缩进使JSON格式化
            )
            exporter.start_exporting()
            self.exporters[spider.name] = exporter
    
    def process_item(self, item, spider):
        """处理每个item"""
        if spider.name in self.exporters:
            self.exporters[spider.name].export_item(item)
        return item
    
    def close_spider(self, spider):
        """爬虫关闭时关闭文件"""
        if spider.name in self.exporters:
            self.exporters[spider.name].finish_exporting()
            self.files[spider.name].close()
            del self.exporters[spider.name]
            del self.files[spider.name]

class CoursespiderPipeline:
    """日志管道"""
    def process_item(self, item, spider):
        spider.logger.info(f"✅ 抓取课程: {item['title']} | 学校: {item['school']} | 分类: {item['tags']}")
        return item