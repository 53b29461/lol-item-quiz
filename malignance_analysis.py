#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random

# アプリからの関数をインポート
def filter_items(all_items):
    map_filtered_items = {item_id: item for item_id, item in all_items.items() if item.get('maps', {}).get('11', False) and not all(item.get('maps', {}).get(map_id, False) for map_id in ['11', '12', '21', '30'])}
    
    target_tags = ['Consumable', 'Trinket', 'Boots', 'Jungle', 'Lane']
    exclude_item_names = ['ロング ソード']
    tag_filtered_items = {item_id: item for item_id, item in all_items.items() if any(tag in item.get('tags', []) for tag in target_tags) and item['name'] not in exclude_item_names}
    
    final_filtered_items = {item_id: item for item_id, item in map_filtered_items.items() if item_id not in tag_filtered_items}
    
    exclude_ids = ['6693', '6673', '4641', '4637', '1516', '1517', '1518', '1519']
    last_final_filtered_items = {item_id: item for item_id, item in final_filtered_items.items() if item_id not in exclude_ids}
    
    # アリーナ版アイテム（IDが32で始まる）を除外
    arena_filtered_items = {item_id: item for item_id, item in last_final_filtered_items.items() if not item_id.startswith('32')}
    
    return arena_filtered_items

def build_item_tree(item_id, items):
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
    for item_id, item in items.items():
        if 'from' in item:
            for parent_id in item['from']:
                if parent_id in trees:
                    trees[item_id].setdefault('children', []).append(parent_id)
                    trees[parent_id]['parents'].append(item_id)

def get_immediate_family(item_id, trees):
    item_tree = trees.get(item_id)
    if item_tree is None:
        return []

    family = []
    if 'parents' in item_tree:
        family.extend(item_tree['parents'])
    if 'children' in item_tree:
        family.extend(item_tree['children'])
    return family

def get_extended_family(item_id, trees, items):
    immediate_family = get_immediate_family(item_id, trees)
    extended_family = set(immediate_family)  # Use a set to avoid duplicates

    for family_member_id in immediate_family:
        family_member_family = get_immediate_family(family_member_id, trees)
        for family_member_family_id in family_member_family:
            family_member_family_member_family = get_immediate_family(family_member_family_id, trees)
            extended_family.update(family_member_family_member_family)

    return extended_family

def analyze_malignance():
    # アイテムデータを取得
    patch_version = '15.13.1'
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json'
    response = requests.get(url)
    data = response.json()

    all_items = {item_id: item for item_id, item in data['data'].items() if item.get('requiredAlly') != 'Ornn'}
    filtered_items = filter_items(all_items)
    all_trees = {item_id: build_item_tree(item_id, filtered_items) for item_id in filtered_items}
    connect_parents(filtered_items, all_trees)

    # マリグナンス（3118）の拡張ファミリーを取得
    malignance_id = '3118'
    print(f'=== マリグナンス（{malignance_id}）の拡張ファミリー分析 ===')

    immediate_family = get_immediate_family(malignance_id, all_trees)
    print(f'immediate_family IDs: {immediate_family}')

    # immediate_familyのアイテム名を表示
    print(f'\n== immediate_family のアイテム名 ==')
    for family_id in immediate_family:
        if family_id in filtered_items:
            print(f'{family_id}: {filtered_items[family_id]["name"]} (ゴールド: {filtered_items[family_id]["gold"]["total"]})')

    extended_family = get_extended_family(malignance_id, all_trees, all_items)
    print(f'\nextended_family IDs: {list(extended_family)}')

    # extended_familyのアイテム名を表示
    print(f'\n== extended_family のアイテム名（マリグナンス除く） ==')
    extended_family_without_self = [f for f in extended_family if f != malignance_id]
    for family_id in extended_family_without_self:
        if family_id in filtered_items:
            item = filtered_items[family_id]
            print(f'{family_id}: {item["name"]} (ゴールド: {item["gold"]["total"]}, タグ: {item.get("tags", [])})')

    print(f'\n総extended_family数: {len(extended_family)}')
    print(f'マリグナンス除く総ひっかけ候補数: {len(extended_family_without_self)}')
    
    # 各段階での分析
    print(f'\n=== 段階別分析 ===')
    print(f'1. immediate_family (直接関係): {len(immediate_family)}個')
    print(f'2. extended_family (2次関係まで): {len(extended_family)}個')
    print(f'3. ひっかけ候補 (マリグナンス除く): {len(extended_family_without_self)}個')
    
    # 関係性の説明
    print(f'\n=== 関係性の分析 ===')
    for family_id in immediate_family:
        if family_id in filtered_items:
            family_item = filtered_items[family_id]
            immediate_of_family = get_immediate_family(family_id, all_trees)
            print(f'\n{family_id}: {family_item["name"]}')
            print(f'  この素材/完成品のfamily: {immediate_of_family}')
            for sub_family_id in immediate_of_family:
                if sub_family_id in filtered_items and sub_family_id != malignance_id:
                    sub_item = filtered_items[sub_family_id]
                    print(f'    → {sub_family_id}: {sub_item["name"]}')

def analyze_distractor_categories():
    # アイテムデータを取得
    patch_version = '15.13.1'
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json'
    response = requests.get(url)
    data = response.json()

    # マリグナンスの正解素材
    correct_materials = ['ロスト チャプター', '増魔の書', 'サファイア クリスタル', '輝きのモート', 'ブラスティング ワンド']

    # ひっかけ選択肢の分析
    malignance_extended_family = [
        '2508', '3057', '4632', '2020', '3803', '1043', '3116', '1011', '3114', '1026', 
        '3067', '3113', '3124', '3024', '4635', '3916', '3147', '3133', '3145', '4642', 
        '6660', '4630', '2420', '3802', '3108', '1052', '2421', '3070'
    ]

    print('\n=== ひっかけ選択肢の分類 ===')

    # カテゴリ別分析
    lost_chapter_builds = []  # ロストチャプターから作れるアイテム
    blast_wand_builds = []   # ブラスティングワンドから作れるアイテム
    component_materials = [] # 素材の素材
    lost_chapter_materials = [] # ロストチャプターの素材

    for item_id in malignance_extended_family:
        item = data['data'].get(item_id)
        if not item:
            continue
        
        item_name = item['name']
        item_from = item.get('from', [])
        
        # ロストチャプターから作れるアイテム
        if '3802' in item_from and item_id != '3118':
            lost_chapter_builds.append(f'{item_name} (ID: {item_id})')
        
        # ブラスティングワンドから作れるアイテム
        elif '1026' in item_from and item_id != '3118':
            blast_wand_builds.append(f'{item_name} (ID: {item_id})')
        
        # ロストチャプターの直接素材
        elif item_id in ['1052', '1027', '2022']:
            lost_chapter_materials.append(f'{item_name} (ID: {item_id})')
        
        # その他（2次的関係）
        else:
            component_materials.append(f'{item_name} (ID: {item_id})')

    print('1. ロストチャプターから作れるアイテム（姉妹アイテム）:')
    for item in lost_chapter_builds:
        print(f'   • {item}')

    print('\n2. ブラスティングワンドから作れるアイテム（姉妹アイテム）:')
    for item in blast_wand_builds:
        print(f'   • {item}')

    print('\n3. ロストチャプターの素材:')
    for item in lost_chapter_materials:
        print(f'   • {item}')

    print('\n4. その他の2次的関係アイテム:')
    for item in component_materials:
        print(f'   • {item}')

    print('\n=== ひっかけになる理由 ===')
    print('• 姉妹アイテム: 同じ素材（ロストチャプター/ブラスティングワンド）を使うため混同しやすい')
    print('• 素材の素材: マリグナンスの構成に含まれているため一見正解に見える')
    print('• 2次的関係: 素材を共有するアイテムの別の完成品で、関連性があると錯覚しやすい')

if __name__ == "__main__":
    analyze_malignance()
    analyze_distractor_categories()