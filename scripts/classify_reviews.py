#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论智能分类工具
按照优先级、类别、问题类型等维度分析所有评论
"""

import json
import re
import glob
import os
from datetime import datetime
from collections import defaultdict

class ReviewClassifier:
    """评论分类器"""

    ISSUE_KEYWORDS = {
        '技术问题': ['崩溃', '闪退', '卡顿', '掉帧', 'crash', 'bug', '卡死', '黑屏', '无法', '不能', 'fps', '延迟', '卡屏'],
        '内容不足': ['内容少', '内容不足', '太少', '缺少', '职业少', '技能少', '装备少', '道具少', '单调', '重复', '没有新意'],
        '战斗机制': ['战斗', '机制', '复杂', '难懂', '不平衡', '克制', '猜拳', '石头剪刀布', '霸体', '破势', '格防', '韧性'],
        '游戏节奏': ['节奏', '慢', '浪费时间', '转场', '动画', '太长', '冗长', '等待'],
        '上手难度': ['新手', '教程', '难', '不友好', '复杂', '看不懂', '学习曲线'],
        '游戏时长': ['太短', '结束', '快', '局外', '养成', '重玩性', 'roguelike'],
        '平衡性': ['平衡', '太强', '太弱', 'op', 'imba', '不公平', '运气'],
        '对比竞品': ['背包乱斗', 'backpack', '大巴扎', '不如'],
        '画面音效': ['画面', '音效', '音乐', '美术', '建模', '特效', '视觉'],
        'UI/UX': ['界面', 'UI', '操作', '交互', '提示', '说明'],
        '多人/联机': ['联机', '多人', 'pvp', '匹配', '对战'],
        '价格': ['价格', '贵', '便宜', '性价比', '值得', '不值'],
        '其他建议': []
    }

    POSITIVE_KEYWORDS = ['好玩', '有趣', '推荐', '喜欢', '优秀', '精致', '流畅', '创新',
                         '期待', '潜力', '不错', '可以', 'good', 'fun', 'great', 'nice']

    NEGATIVE_KEYWORDS = ['不推荐', '差', '烂', '垃圾', '失望', '后悔', '退款', 'bad',
                         'terrible', 'boring', '无聊', '浪费', '不值']

    def __init__(self, reviews_data):
        self.reviews = reviews_data.get('reviews', [])
        self.query_summary = reviews_data.get('query_summary', {})

    def classify_review(self, review):
        """分类单条评论"""
        review_text = review.get('review', '').lower()
        voted_up = review.get('voted_up', True)
        votes_up = review.get('votes_up', 0)
        playtime = review.get('author', {}).get('playtime_forever', 0) / 60

        sentiment = '好评' if voted_up else '差评'

        issues = []
        for issue_type, keywords in self.ISSUE_KEYWORDS.items():
            if issue_type == '其他建议':
                continue
            for keyword in keywords:
                if keyword in review_text:
                    if issue_type not in issues:
                        issues.append(issue_type)
                    break

        if not issues:
            if voted_up:
                issues.append('纯好评')
            else:
                issues.append('其他建议')

        priority = self._determine_priority(review, votes_up, issues, playtime, voted_up)
        tags = self._extract_tags(review_text, voted_up)
        key_points = self._extract_key_points(review_text, issues)

        return {
            'sentiment': sentiment,
            'issues': issues,
            'priority': priority,
            'tags': tags,
            'key_points': key_points,
            'playtime_hours': round(playtime, 1),
            'votes': votes_up,
            'language': review.get('language', 'unknown')
        }

    def _determine_priority(self, review, votes, issues, playtime, voted_up):
        """判定优先级"""
        score = 0

        if votes >= 50: score += 30
        elif votes >= 20: score += 20
        elif votes >= 10: score += 10
        elif votes >= 5: score += 5

        if playtime >= 20: score += 15
        elif playtime >= 10: score += 10
        elif playtime >= 5: score += 5
        elif playtime < 1: score -= 10

        if '技术问题' in issues: score += 25
        if '内容不足' in issues: score += 15
        if '战斗机制' in issues: score += 10
        if '上手难度' in issues: score += 10

        if not voted_up: score += 10

        if score >= 50: return 'P0-紧急'
        elif score >= 30: return 'P1-高'
        elif score >= 15: return 'P2-中'
        else: return 'P3-低'

    def _extract_tags(self, text, voted_up):
        """提取标签"""
        tags = []

        for keyword in self.POSITIVE_KEYWORDS:
            if keyword in text:
                tags.append('正面反馈')
                break

        for keyword in self.NEGATIVE_KEYWORDS:
            if keyword in text:
                tags.append('负面反馈')
                break

        if '建议' in text or 'suggest' in text:
            tags.append('有建议')
        if '期待' in text or '希望' in text:
            tags.append('有期待')
        if 'mod' in text.lower():
            tags.append('需要MOD')
        if '退款' in text or 'refund' in text:
            tags.append('退款风险')
        if '更新' in text or 'update' in text:
            tags.append('期待更新')

        return tags if tags else ['一般评价']

    def _extract_key_points(self, text, issues):
        """提取关键要点"""
        points = []
        sentences = re.split(r'[。！？\n]', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            for issue in issues:
                if issue in ['技术问题', '内容不足', '战斗机制', '上手难度']:
                    keywords = self.ISSUE_KEYWORDS.get(issue, [])
                    for keyword in keywords[:5]:
                        if keyword in sentence and len(sentence) < 100:
                            points.append(sentence)
                            break

            if len(points) >= 3:
                break

        return points if points else ['无特殊要点']

    def classify_all(self):
        """分类所有评论"""
        classified_reviews = []

        for idx, review in enumerate(self.reviews, 1):
            classification = self.classify_review(review)

            classified_review = {
                'ID': idx,
                'recommendationid': review.get('recommendationid'),
                'timestamp': datetime.fromtimestamp(review.get('timestamp_created', 0)).strftime('%Y-%m-%d %H:%M'),
                'sentiment': classification['sentiment'],
                'priority': classification['priority'],
                'issues': ', '.join(classification['issues']),
                'tags': ', '.join(classification['tags']),
                'language': classification['language'],
                'playtime_hours': classification['playtime_hours'],
                'votes_up': classification['votes'],
                'votes_funny': review.get('votes_funny', 0),
                'review_text': review.get('review', '')[:500],
                'key_points': ' | '.join(classification['key_points']),
                'steam_purchase': '是' if review.get('steam_purchase') else '否',
                'author_games_owned': review.get('author', {}).get('num_games_owned', 0),
            }

            classified_reviews.append(classified_review)

        return classified_reviews

    def generate_summary(self, classified_reviews):
        """生成分类汇总"""
        summary = {
            '总评论数': len(classified_reviews),
            '好评数': sum(1 for r in classified_reviews if r['sentiment'] == '好评'),
            '差评数': sum(1 for r in classified_reviews if r['sentiment'] == '差评'),
        }

        priority_dist = defaultdict(int)
        for r in classified_reviews:
            priority_dist[r['priority']] += 1
        summary['优先级分布'] = dict(priority_dist)

        issue_count = defaultdict(int)
        for r in classified_reviews:
            for issue in r['issues'].split(', '):
                issue_count[issue] += 1
        summary['问题类型统计'] = dict(sorted(issue_count.items(), key=lambda x: x[1], reverse=True))

        lang_dist = defaultdict(int)
        for r in classified_reviews:
            lang_dist[r['language']] += 1
        summary['语言分布'] = dict(lang_dist)

        return summary


def find_latest_reviews_file(output_dir='output'):
    """查找最新的评论JSON文件"""
    pattern = os.path.join(output_dir, 'reviews_*.json')
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def main():
    """主函数"""
    # 自动查找最新的评论文件
    reviews_file = find_latest_reviews_file()
    if not reviews_file:
        print("[错误] 未找到评论数据文件，请先运行 steam_reviews_fetcher_v2.py")
        return

    print(f"读取文件: {reviews_file}")

    with open(reviews_file, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    print("开始分类评论...")
    classifier = ReviewClassifier(reviews_data)
    classified_reviews = classifier.classify_all()

    print(f"分类完成！共处理 {len(classified_reviews)} 条评论")

    summary = classifier.generate_summary(classified_reviews)

    print("\n=== 分类汇总 ===")
    for key, value in summary.items():
        print(f"\n{key}:")
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"  {value}")

    output = {
        'summary': summary,
        'reviews': classified_reviews
    }

    with open('output/classified_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n分类结果已保存到: output/classified_reviews.json")

    import csv
    with open('output/classified_reviews.csv', 'w', encoding='utf-8-sig', newline='') as f:
        if classified_reviews:
            writer = csv.DictWriter(f, fieldnames=classified_reviews[0].keys())
            writer.writeheader()
            writer.writerows(classified_reviews)

    print("CSV 文件已保存到: output/classified_reviews.csv")

    return classified_reviews, summary


if __name__ == "__main__":
    classified_reviews, summary = main()
