#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Steam 游戏评论批量获取工具 V2 - 改进版
添加去重和智能停止功能
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional, Set
import sys

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class SteamReviewsFetcherV2:
    """Steam 评论抓取器 V2"""

    BASE_URL = "https://store.steampowered.com/appreviews/{appid}"

    def __init__(self, app_id: str, config: Optional[Dict] = None):
        self.app_id = app_id
        self.config = config or {}

        self.params = {
            'json': '1',
            'filter': self.config.get('filter', 'all'),
            'language': self.config.get('language', 'all'),
            'review_type': self.config.get('review_type', 'all'),
            'purchase_type': self.config.get('purchase_type', 'all'),
            'num_per_page': str(self.config.get('num_per_page', 100)),
        }

        if self.config.get('day_range'):
            self.params['day_range'] = str(self.config['day_range'])

        if self.config.get('filter_offtopic_activity') is False:
            self.params['filter_offtopic_activity'] = '0'

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 用于去重
        self.seen_ids: Set[str] = set()

    def fetch_page(self, cursor: str = "*") -> Dict:
        """获取单页评论数据"""
        url = self.BASE_URL.format(appid=self.app_id)
        params = self.params.copy()
        params['cursor'] = cursor

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if data.get('success') != 1:
                    raise Exception(f"API 返回失败: {data}")

                return data

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"\n请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception(f"请求失败，已达最大重试次数: {e}")

    def fetch_all(self) -> tuple[List[Dict], Dict]:
        """获取所有评论（带去重）"""
        all_reviews = []
        cursor = "*"
        page_count = 0
        query_summary = None
        duplicate_count = 0
        no_new_data_rounds = 0

        print(f"\n开始获取 App ID: {self.app_id} 的评论数据...")
        print(f"参数配置: {json.dumps(self.params, ensure_ascii=False, indent=2)}\n")

        first_response = self.fetch_page(cursor)
        query_summary = first_response.get('query_summary', {})

        total_reviews = query_summary.get('total_reviews', 0)
        print(f"评论总数: {total_reviews}")
        print(f"好评数: {query_summary.get('total_positive', 0)}")
        print(f"差评数: {query_summary.get('total_negative', 0)}")
        print(f"评分: {query_summary.get('review_score_desc', 'N/A')}\n")

        pbar = None
        if HAS_TQDM and total_reviews > 0:
            pbar = tqdm(total=total_reviews, desc="获取评论", unit="条")

        try:
            while True:
                if cursor == "*":
                    data = first_response
                else:
                    data = self.fetch_page(cursor)
                    time.sleep(self.config.get('delay', 0.5))

                reviews = data.get('reviews', [])

                if not reviews:
                    if pbar:
                        pbar.close()
                    print("\n当前页无数据，抓取结束")
                    break

                new_reviews = []
                for review in reviews:
                    review_id = review.get('recommendationid')
                    if review_id and review_id not in self.seen_ids:
                        self.seen_ids.add(review_id)
                        new_reviews.append(review)
                    else:
                        duplicate_count += 1

                if not new_reviews:
                    no_new_data_rounds += 1
                    print(f"\n[警告] 第 {page_count + 1} 页全是重复数据 ({len(reviews)} 条)")

                    if no_new_data_rounds >= 3:
                        if pbar:
                            pbar.close()
                        print(f"\n连续 {no_new_data_rounds} 页没有新数据，停止抓取")
                        break
                else:
                    no_new_data_rounds = 0
                    all_reviews.extend(new_reviews)
                    page_count += 1

                    if pbar:
                        pbar.update(len(new_reviews))
                    else:
                        print(f"第 {page_count} 页: 新增 {len(new_reviews)} 条，重复 {len(reviews) - len(new_reviews)} 条 (累计: {len(all_reviews)}/{total_reviews})")

                if len(all_reviews) >= total_reviews:
                    if pbar:
                        pbar.close()
                    print(f"\n已获取所有评论 ({len(all_reviews)} 条)")
                    break

                new_cursor = data.get('cursor')

                if not new_cursor or new_cursor == cursor:
                    if pbar:
                        pbar.close()
                    print("\n已到达最后一页")
                    break

                cursor = new_cursor

        except KeyboardInterrupt:
            if pbar:
                pbar.close()
            print("\n\n用户中断，保存已获取的数据...")

        except Exception as e:
            if pbar:
                pbar.close()
            print(f"\n发生错误: {e}")
            print("保存已获取的数据...")

        print(f"\n去重统计: 发现 {duplicate_count} 条重复评论")
        return all_reviews, query_summary

    def save_json(self, reviews: List[Dict], query_summary: Dict, output_file: str):
        """保存为 JSON 格式"""
        data = {
            'app_id': self.app_id,
            'fetch_time': datetime.now().isoformat(),
            'total_fetched': len(reviews),
            'query_summary': query_summary,
            'config': self.params,
            'reviews': reviews
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n[成功] JSON 文件已保存: {output_file}")

    def save_csv(self, reviews: List[Dict], output_file: str):
        """保存为 CSV 格式"""
        try:
            import csv

            if not reviews:
                print("没有数据可保存")
                return

            fields = [
                'recommendationid',
                'language',
                'review',
                'voted_up',
                'votes_up',
                'votes_funny',
                'weighted_vote_score',
                'comment_count',
                'steam_purchase',
                'received_for_free',
                'written_during_early_access',
                'timestamp_created',
                'timestamp_updated',
            ]

            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                writer.writeheader()

                for review in reviews:
                    row = review.copy()
                    if 'author' in review:
                        row.update({f"author_{k}": v for k, v in review['author'].items()})
                    writer.writerow(row)

            print(f"[成功] CSV 文件已保存: {output_file}")

        except ImportError:
            print("[失败] CSV 导出需要 csv 模块")


def load_config(config_file: str = 'config.json') -> Dict:
    """加载配置文件"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def main():
    """主函数"""
    config = load_config()

    app_id = sys.argv[1] if len(sys.argv) > 1 else config.get('app_id', '3081280')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = config.get('output_dir', 'output')
    os.makedirs(output_dir, exist_ok=True)

    json_file = os.path.join(output_dir, f"reviews_{app_id}_{timestamp}.json")
    csv_file = os.path.join(output_dir, f"reviews_{app_id}_{timestamp}.csv")

    fetcher = SteamReviewsFetcherV2(app_id, config)

    reviews, query_summary = fetcher.fetch_all()

    if reviews:
        fetcher.save_json(reviews, query_summary, json_file)

        if config.get('export_csv', True):
            fetcher.save_csv(reviews, csv_file)

        print(f"\n[统计数据]")
        print(f"   获取评论数: {len(reviews)}")
        print(f"   好评数: {sum(1 for r in reviews if r.get('voted_up'))}")
        print(f"   差评数: {sum(1 for r in reviews if not r.get('voted_up'))}")

        languages = {}
        for r in reviews:
            lang = r.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1

        print(f"\n   语言分布:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     {lang}: {count} 条")

    else:
        print("\n[警告] 未获取到任何评论数据")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已终止")
        sys.exit(0)
    except Exception as e:
        print(f"\n[失败] 程序错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
