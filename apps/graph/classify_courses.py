import json
import sys
import os
from tqdm import tqdm
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.openai_client import analyze_with_moonshot
#from config import DATABASE_URI
BASE_DIR = os.path.dirname(__file__)          # 当前 graph_builder.py 所在目录
file_path_c = os.path.join(BASE_DIR, "courses.json")
file_path_ct = os.path.join(BASE_DIR, "courses_tagged.json")
def classify_subject(title, description):
    prompt = f"""你是课程学科分类专家。请根据下面这门课程的标题和描述，判断它属于哪个一级学科领域。只输出“数学”“物理”“计算机”“化学”“生物”“经济”“管理”“语言”“艺术”“教育”“心理学”“医学”“历史”“哲学”“政治”“法学”“工程”“环境科学”“其他”这19个中的一个，直接输出，不要解释。

课程标题：{title}
课程描述：{description}

学科分类是："""
    return analyze_with_moonshot(prompt).strip()


def classify_all():
    with open(file_path_c, "r", encoding="utf-8") as f:
        courses = json.load(f)

    new_courses = []
    for c in tqdm(courses):
        subject = classify_subject(c["title"], c["description"])
        c["subject"] = subject
        new_courses.append(c)

    with open(file_path_ct, "w", encoding="utf-8") as f:
        json.dump(new_courses, f, ensure_ascii=False, indent=2)

    print(f"已为 {len(new_courses)} 门课程生成一级学科标签，并保存至 courses_tagged.json")


if __name__ == "__main__":
    classify_all()
