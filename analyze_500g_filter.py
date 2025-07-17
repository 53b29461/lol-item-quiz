#!/usr/bin/env python3
"""
League of Legends 500ゴールドフィルター分析スクリプト
APIから500G未満のアイテムを取得し、分類・分析を行う
"""

import requests
import json
from collections import defaultdict, Counter

def get_items_data():
    """League of Legends APIからアイテムデータを取得"""
    url = "https://ddragon.leagueoflegends.com/cdn/15.13.1/data/ja_JP/item.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API取得エラー: {e}")
        return None

def analyze_items_under_500g(items_data):
    """500G未満のアイテムを分析"""
    if not items_data:
        return
    
    all_items = items_data['data']
    under_500g_items = []
    
    # 500G未満のアイテムを抽出
    for item_id, item in all_items.items():
        if item.get('gold', {}).get('total', 0) < 500:
            under_500g_items.append({
                'id': item_id,
                'name': item.get('name', 'Unknown'),
                'total_price': item.get('gold', {}).get('total', 0),
                'base_price': item.get('gold', {}).get('base', 0),
                'sell_price': item.get('gold', {}).get('sell', 0),
                'tags': item.get('tags', []),
                'description': item.get('description', '').replace('<br>', '\n'),
                'plaintext': item.get('plaintext', ''),
                'maps': item.get('maps', {}),
                'requiredAlly': item.get('requiredAlly', ''),
                'requiredChampion': item.get('requiredChampion', ''),
                'from': item.get('from', []),
                'into': item.get('into', [])
            })
    
    # 価格順にソート
    under_500g_items.sort(key=lambda x: x['total_price'])
    
    print("=" * 80)
    print("League of Legends: 500ゴールド未満アイテム分析レポート")
    print("=" * 80)
    print(f"総アイテム数: {len(all_items)}")
    print(f"500G未満アイテム数: {len(under_500g_items)}")
    print(f"除外率: {len(under_500g_items)/len(all_items)*100:.1f}%")
    print()
    
    # 価格帯別分析
    price_ranges = {
        "0-99G": [],
        "100-199G": [],
        "200-299G": [],
        "300-399G": [],
        "400-499G": []
    }
    
    for item in under_500g_items:
        price = item['total_price']
        if price < 100:
            price_ranges["0-99G"].append(item)
        elif price < 200:
            price_ranges["100-199G"].append(item)
        elif price < 300:
            price_ranges["200-299G"].append(item)
        elif price < 400:
            price_ranges["300-399G"].append(item)
        else:
            price_ranges["400-499G"].append(item)
    
    print("📊 価格帯別分布:")
    for range_name, items in price_ranges.items():
        print(f"  {range_name}: {len(items)}件")
    print()
    
    # タグ別分析
    tag_counter = Counter()
    for item in under_500g_items:
        for tag in item['tags']:
            tag_counter[tag] += 1
    
    print("🏷️  タグ別分析:")
    for tag, count in tag_counter.most_common():
        print(f"  {tag}: {count}件")
    print()
    
    # カテゴリ別詳細分析
    print("📋 カテゴリ別詳細分析:")
    print()
    
    categories = {
        "基本ステータスアイテム": ["ManaRegen", "HealthRegen", "Armor", "SpellBlock", "Damage", "AttackSpeed", "CriticalStrike", "LifeSteal", "SpellVamp"],
        "消耗品": ["Consumable"],
        "ブーツ": ["Boots"],
        "アクティブアイテム": ["Active"],
        "ジャングルアイテム": ["Jungle"],
        "レーンアイテム": ["Lane"],
        "トリンケット": ["Trinket"],
        "その他": []
    }
    
    categorized = {cat: [] for cat in categories.keys()}
    
    for item in under_500g_items:
        item_categorized = False
        for category, tags in categories.items():
            if category == "その他":
                continue
            if any(tag in item['tags'] for tag in tags):
                categorized[category].append(item)
                item_categorized = True
                break
        
        if not item_categorized:
            categorized["その他"].append(item)
    
    # 各カテゴリの詳細表示
    for category, items in categorized.items():
        if items:
            print(f"--- {category} ({len(items)}件) ---")
            for item in items:
                tags_str = ", ".join(item['tags']) if item['tags'] else "なし"
                print(f"  • {item['name']} ({item['total_price']}G)")
                print(f"    タグ: {tags_str}")
                if item['plaintext']:
                    print(f"    説明: {item['plaintext']}")
                if item['from']:
                    print(f"    作成元: {item['from']}")
                if item['into']:
                    print(f"    アップグレード先: {item['into']}")
                print()
    
    # クイズ選択肢として不適切な理由の分析
    print("🚫 クイズ選択肢として不適切と考えられる理由:")
    print()
    
    # 消耗品の分析
    consumables = [item for item in under_500g_items if "Consumable" in item['tags']]
    if consumables:
        print(f"1. 消耗品 ({len(consumables)}件):")
        print("   - 一時的な効果のみ、永続的なアイテムビルドに含まれない")
        for item in consumables:
            print(f"   • {item['name']} ({item['total_price']}G)")
        print()
    
    # 基本アイテムの分析
    basic_items = [item for item in under_500g_items if not item['from'] and item['into']]
    if basic_items:
        print(f"2. 基本アイテム（素材）({len(basic_items)}件):")
        print("   - そのまま使用されることは少なく、より高価なアイテムの材料")
        for item in basic_items:
            print(f"   • {item['name']} ({item['total_price']}G) → {len(item['into'])}個のアイテムの材料")
        print()
    
    # 特殊条件アイテム
    special_items = [item for item in under_500g_items if item['requiredAlly'] or item['requiredChampion']]
    if special_items:
        print(f"3. 特殊条件アイテム ({len(special_items)}件):")
        print("   - 特定のチャンピオンや味方が必要")
        for item in special_items:
            print(f"   • {item['name']} ({item['total_price']}G)")
            if item['requiredAlly']:
                print(f"     必要な味方: {item['requiredAlly']}")
            if item['requiredChampion']:
                print(f"     必要なチャンピオン: {item['requiredChampion']}")
        print()
    
    # 完成アイテムの価格分析
    completed_items_over_500 = [item for item_id, item in all_items.items() 
                               if item.get('gold', {}).get('total', 0) >= 500 and not item.get('from')]
    
    print("💰 500G以上の完成アイテム価格分析:")
    if completed_items_over_500:
        prices = [item.get('gold', {}).get('total', 0) for item in completed_items_over_500]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"   • 500G以上の完成アイテム数: {len(completed_items_over_500)}")
        print(f"   • 平均価格: {avg_price:.0f}G")
        print(f"   • 最低価格: {min_price}G")
        print(f"   • 最高価格: {max_price}G")
        print()
    
    # 500G閾値の妥当性分析
    print("🎯 500G閾値の妥当性分析:")
    print()
    print("【妥当な理由】")
    print("1. 基本アイテムの除外:")
    print("   - 大部分の基本ステータスアイテム（300-400G）を除外")
    print("   - クイズの選択肢として紛らわしい「材料」を排除")
    print()
    print("2. 消耗品の除外:")
    print("   - ポーション類など一時的効果アイテムを除外")
    print("   - 永続的なビルド関連アイテムのみを対象")
    print()
    print("3. ゲームプレイ的意義:")
    print("   - 500G以上のアイテムは戦略的重要度が高い")
    print("   - プレイヤーが実際に意識して購入するアイテム")
    print()
    print("4. クイズの教育効果:")
    print("   - 実戦で重要なアイテム知識の習得")
    print("   - 基本材料よりも完成アイテムへの理解促進")
    
    return under_500g_items

def main():
    """メイン実行関数"""
    print("League of Legends APIからアイテムデータを取得中...")
    items_data = get_items_data()
    
    if items_data:
        analyze_items_under_500g(items_data)
    else:
        print("アイテムデータの取得に失敗しました。")

if __name__ == "__main__":
    main()