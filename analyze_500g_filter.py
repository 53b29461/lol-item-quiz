#!/usr/bin/env python3
"""
League of Legends クイズアプリで500ゴールドフィルターによって除外されるアイテムの分析
"""

import requests
import json
import sys

patch_version = "15.13.1"

def get_items_data():
    """APIからアイテムデータを取得"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json"
    print(f"APIからデータ取得中: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"エラー: APIからデータを取得できませんでした (ステータス: {response.status_code})")
        sys.exit(1)
    return response.json()

def filter_items(all_items):
    """app.pyのfilter_items関数と同じフィルタリングを適用"""
    # Step 1: マップフィルタリング
    map_filtered_items = {
        item_id: item for item_id, item in all_items.items() 
        if item.get('maps', {}).get('11', False) and 
        not all(item.get('maps', {}).get(map_id, False) for map_id in ['11', '12', '21', '30'])
    }
    
    # Step 2: タグフィルタリング
    target_tags = ['Consumable', 'Trinket', 'Boots', 'Jungle', 'Lane']
    exclude_item_names = ['ロング ソード']
    tag_filtered_items = {
        item_id: item for item_id, item in all_items.items() 
        if any(tag in item.get('tags', []) for tag in target_tags) and 
        item['name'] not in exclude_item_names
    }
    
    # Step 3: 最終フィルタリング（タグフィルタリングされたアイテムを除外）
    final_filtered_items = {
        item_id: item for item_id, item in map_filtered_items.items() 
        if item_id not in tag_filtered_items
    }
    
    # Step 4: 手動除外リスト
    exclude_ids = ['6693', '6673', '4641', '4637', '1516', '1517', '1518', '1519']
    last_final_filtered_items = {
        item_id: item for item_id, item in final_filtered_items.items() 
        if item_id not in exclude_ids
    }
    
    return last_final_filtered_items

def build_item_tree(item_id, items):
    """アイテムツリーノードを構築"""
    item = items.get(item_id)
    if item is None or item.get('requiredAlly') == 'Ornn':
        return None
    node = {
        'id': item_id,
        'name': item['name'],
        'parents': [],
        'gold': item['gold']['total'],
        'image': item['image']['full'],
        'tags': item.get('tags', [])
    }
    return node

def connect_parents(items, trees):
    """親子関係を接続"""
    for item_id, item in items.items():
        if 'from' in item:
            for parent_id in item['from']:
                if parent_id in trees:
                    trees[item_id].setdefault('children', []).append(parent_id)
                    trees[parent_id]['parents'].append(item_id)

def get_immediate_family(item_id, trees):
    """直接的な親子関係を取得"""
    item_tree = trees.get(item_id)
    if item_tree is None:
        return []

    family = []
    if 'parents' in item_tree:
        family.extend(item_tree['parents'])
    if 'children' in item_tree:
        family.extend(item_tree['children'])
    return family

def get_extended_family_analysis(item_id, trees, items):
    """拡張家族の分析（500Gフィルター前後）"""
    immediate_family = get_immediate_family(item_id, trees)
    extended_family = set(immediate_family)

    for family_member_id in immediate_family:
        family_member_family = get_immediate_family(family_member_id, trees)
        for family_member_family_id in family_member_family:
            family_member_family_member_family = get_immediate_family(family_member_family_id, trees)
            extended_family.update(family_member_family_member_family)

    # 500Gフィルター前のアイテム
    all_extended_family = list(extended_family)
    
    # 500Gフィルター後のアイテム（app.pyと同じロジック）
    filtered_extended_family = [
        family_id for family_id in extended_family 
        if items[family_id]['gold']['total'] >= 500
    ]
    
    # 除外されたアイテム（500G未満）
    excluded_items = [
        family_id for family_id in extended_family 
        if items[family_id]['gold']['total'] < 500
    ]
    
    return all_extended_family, filtered_extended_family, excluded_items

def analyze_500g_filter():
    """500ゴールドフィルターで除外されるアイテムを分析"""
    print("=== League of Legends クイズアプリ: 500ゴールドフィルター除外アイテム分析 ===\n")
    
    # データ取得
    data = get_items_data()
    all_items = {
        item_id: item for item_id, item in data['data'].items() 
        if item.get('requiredAlly') != 'Ornn'
    }
    
    print(f"全アイテム数（Ornn専用除く）: {len(all_items)}")
    
    # フィルタリング
    filtered_items = filter_items(all_items)
    print(f"フィルタリング後アイテム数: {len(filtered_items)}")
    
    # ツリー構築
    all_trees = {item_id: build_item_tree(item_id, filtered_items) for item_id in filtered_items}
    connect_parents(filtered_items, all_trees)
    
    # 500G未満で除外される可能性があるアイテムを収集
    excluded_by_500g = set()
    
    print("\n=== 各アイテムの拡張家族分析 ===")
    
    for item_id, tree in all_trees.items():
        if tree is None:
            continue
            
        all_family, filtered_family, excluded = get_extended_family_analysis(item_id, all_trees, all_items)
        
        if excluded:
            excluded_by_500g.update(excluded)
            print(f"\nアイテム: {tree['name']} (ID: {item_id})")
            print(f"  拡張家族総数: {len(all_family)}")
            print(f"  500G以上: {len(filtered_family)}")
            print(f"  500G未満（除外）: {len(excluded)}")
            
            if excluded:
                for exc_id in excluded:
                    exc_item = all_items[exc_id]
                    print(f"    - {exc_item['name']} ({exc_item['gold']['total']}G)")
    
    # 除外されたアイテムの詳細リスト
    print(f"\n=== 500ゴールドフィルターで除外されるアイテム一覧 ===")
    print(f"除外アイテム総数: {len(excluded_by_500g)}")
    
    if excluded_by_500g:
        excluded_items_info = []
        for item_id in excluded_by_500g:
            item = all_items[item_id]
            excluded_items_info.append({
                'id': item_id,
                'name': item['name'],
                'gold': item['gold']['total'],
                'tags': item.get('tags', []),
                'description': item.get('plaintext', '説明なし')
            })
        
        # 価格順でソート
        excluded_items_info.sort(key=lambda x: x['gold'])
        
        print("\n【除外アイテム詳細】")
        print("-" * 80)
        for item in excluded_items_info:
            tags_str = ', '.join(item['tags']) if item['tags'] else 'なし'
            print(f"アイテム名: {item['name']}")
            print(f"価格: {item['gold']}ゴールド")
            print(f"カテゴリ: {tags_str}")
            print(f"説明: {item['description']}")
            print(f"ID: {item['id']}")
            print("-" * 80)
    else:
        print("除外されるアイテムは見つかりませんでした。")
    
    # 統計情報
    print(f"\n=== 統計情報 ===")
    if excluded_by_500g:
        prices = [all_items[item_id]['gold']['total'] for item_id in excluded_by_500g]
        print(f"除外アイテム数: {len(excluded_by_500g)}")
        print(f"価格範囲: {min(prices)}G - {max(prices)}G")
        print(f"平均価格: {sum(prices) / len(prices):.1f}G")
        
        # カテゴリ別集計
        category_count = {}
        for item_id in excluded_by_500g:
            tags = all_items[item_id].get('tags', [])
            for tag in tags:
                category_count[tag] = category_count.get(tag, 0) + 1
        
        if category_count:
            print(f"\nカテゴリ別分布:")
            for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}個")

if __name__ == "__main__":
    analyze_500g_filter()