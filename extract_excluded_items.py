#!/usr/bin/env python3
"""
500ゴールドフィルターで除外されるアイテムの詳細リストを抽出
"""

import requests
import json

patch_version = "15.13.1"

def get_items_data():
    """APIからアイテムデータを取得"""
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json"
    response = requests.get(url)
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

def get_excluded_items():
    """500ゴールドフィルターで除外されるアイテムを取得"""
    print("=== League of Legends クイズアプリ: 500ゴールド除外アイテム詳細リスト ===\n")
    
    # データ取得
    data = get_items_data()
    all_items = {
        item_id: item for item_id, item in data['data'].items() 
        if item.get('requiredAlly') != 'Ornn'
    }
    
    # フィルタリング
    filtered_items = filter_items(all_items)
    
    # ツリー構築
    all_trees = {item_id: build_item_tree(item_id, filtered_items) for item_id in filtered_items}
    connect_parents(filtered_items, all_trees)
    
    # 500G未満で除外される可能性があるアイテムを収集
    excluded_by_500g = set()
    
    for item_id, tree in all_trees.items():
        if tree is None:
            continue
            
        immediate_family = get_immediate_family(item_id, all_trees)
        extended_family = set(immediate_family)

        for family_member_id in immediate_family:
            family_member_family = get_immediate_family(family_member_id, all_trees)
            for family_member_family_id in family_member_family:
                family_member_family_member_family = get_immediate_family(family_member_family_id, all_trees)
                extended_family.update(family_member_family_member_family)

        # 500G未満のアイテムを除外対象として特定
        excluded = [
            family_id for family_id in extended_family 
            if all_items[family_id]['gold']['total'] < 500
        ]
        
        excluded_by_500g.update(excluded)
    
    # 除外されたアイテムの詳細リスト作成
    if excluded_by_500g:
        excluded_items_info = []
        for item_id in excluded_by_500g:
            item = all_items[item_id]
            excluded_items_info.append({
                'id': item_id,
                'name': item['name'],
                'gold': item['gold']['total'],
                'tags': item.get('tags', []),
                'description': item.get('plaintext', '説明なし'),
                'image_url': f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/item/{item['image']['full']}"
            })
        
        # 価格順でソート
        excluded_items_info.sort(key=lambda x: x['gold'])
        
        print(f"500ゴールドフィルターで除外されるアイテム総数: {len(excluded_items_info)}")
        print("=" * 90)
        
        for i, item in enumerate(excluded_items_info, 1):
            tags_str = ', '.join(item['tags']) if item['tags'] else 'なし'
            print(f"{i:2d}. {item['name']}")
            print(f"    価格: {item['gold']}ゴールド")
            print(f"    カテゴリ: {tags_str}")
            print(f"    説明: {item['description']}")
            print(f"    ID: {item['id']}")
            print(f"    画像URL: {item['image_url']}")
            print("-" * 90)
        
        # カテゴリ別統計
        print(f"\n=== カテゴリ別統計 ===")
        category_count = {}
        for item in excluded_items_info:
            tags = item['tags']
            if not tags:
                category_count['タグなし'] = category_count.get('タグなし', 0) + 1
            else:
                for tag in tags:
                    category_count[tag] = category_count.get(tag, 0) + 1
        
        print(f"除外アイテム数: {len(excluded_items_info)}")
        print(f"価格範囲: {excluded_items_info[0]['gold']}G - {excluded_items_info[-1]['gold']}G")
        print(f"平均価格: {sum(item['gold'] for item in excluded_items_info) / len(excluded_items_info):.1f}G")
        
        print(f"\nカテゴリ別分布:")
        for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}個")
        
        # 用途別分類
        print(f"\n=== 用途別分類 ===")
        
        # 基礎アイテム（ビルド素材）
        basic_items = [item for item in excluded_items_info if 'Damage' in item['tags'] or 'SpellDamage' in item['tags'] or 'Armor' in item['tags'] or 'SpellBlock' in item['tags'] or 'Mana' in item['tags'] or 'Health' in item['tags']]
        
        print(f"基礎アイテム（ビルド素材）: {len(basic_items)}個")
        for item in basic_items:
            print(f"  - {item['name']} ({item['gold']}G) - {', '.join(item['tags'])}")
        
        # クイズでの影響
        print(f"\n=== クイズでの影響 ===")
        print("これらのアイテムは、get_extended_family関数の500Gフィルターによって")
        print("選択肢から除外されるため、プレイヤーには表示されません。")
        print("主に基礎アイテム（ビルド素材）が除外対象となっています。")
        
    else:
        print("除外されるアイテムは見つかりませんでした。")

if __name__ == "__main__":
    get_excluded_items()