import scrapy
from coursespider.items import CourseItem
from urllib.parse import urlencode


class IcourseSpider(scrapy.Spider):
    name = "icourse"
    allowed_domains = ["icourses.cn"]
    start_urls = []

    # ✅ 分类字典：只抓取以下这些分类
    categories = {
        "1": "计算机",
        #"2": "经济管理",
        #"3": "心理学",
        #"4": "外语",
        #"5": "文学历史",
        #"7": "工学",
        #"8": "理学",
        #"9": "医药卫生",
        #"10": "哲学",
        #"11": "法学",
    }

    def start_requests(self):
        for cat_id, cat_name in self.categories.items():
            for page in range(1, 6):  # 每个分类最多抓取5页
                form_data = {
                    "kw": "",
                    "onlineStatus": "1",
                    "currentPage": str(page),
                    "catagoryId": cat_id,
                }
                yield scrapy.FormRequest(
                    url="https://www.icourses.cn/web//sword/portal/openSearchPage",
                    method="POST",
                    formdata=form_data,
                    callback=self.parse,
                    meta={"category": cat_name},
                    dont_filter=True,
                )

    def parse(self, response):
        self.logger.info("🧭 正在解析分类: %s", response.meta["category"])
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"🧭 正在解析分类: {response.meta['category']}\n")

        courses = response.xpath('//li[div[contains(@class, "icourse-item-modulebox-mooc")]]')
        self.logger.info("📦 本页课程数量: %d", len(courses))
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"📦 本页课程数量: {len(courses)}\n")

        for course in courses:
            item = CourseItem()
            item["title"] = ''.join(course.xpath('.//a[contains(@class,"icourse-desc-title")]/b/text()').getall()).strip()
            item["url"] = course.xpath('.//a[contains(@class,"icourse-desc-title")]/@href').get(default='').strip()
            item["platform"] = "中国大学MOOC"
            item["school"] = ''.join(course.xpath('.//div[contains(@class,"icourse-desc-school")]/b/text()').getall()).strip()
            item["teacher"] = ""  # 暂无教师字段
            item["description"] = ""
            item["learners"] = self.parse_learners(course.xpath('.//span[@class="icourse-study-cout"]/text()').get())
            item["tags"] = response.meta["category"]
            item["rating"] = None
            yield item

    def parse_learners(self, text):
        """辅助函数：将 '123' 提取为整数"""
        if not text:
            return 0
        import re
        match = re.search(r'(\d[\d,]*)', text.replace(',', ''))
        return int(match.group(1)) if match else 0
