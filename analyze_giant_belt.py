#!/usr/bin/env python3
import requests
import json

def analyze_giant_belt():
    # Get current patch version and item data
    patch_version = '15.13.1'
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json'
    response = requests.get(url)
    data = response.json()

    ruby_crystal_id = '1028'
    giant_belt_id = '1011'

    print('=== ジャイアントベルトの完全な親子関係分析 ===\n')
    
    # Get Giant's Belt info
    giant_belt = data['data'][giant_belt_id]
    print(f'【対象アイテム】')
    print(f'名前: {giant_belt["name"]}')
    print(f'ID: {giant_belt_id}')
    print(f'価格: {giant_belt["gold"]["total"]}ゴールド')
    print(f'タグ: {giant_belt.get("tags", [])}')
    print()

    # 1. Analyze materials (children in the tree structure)
    print('【1. 素材（子アイテム）】')
    if 'from' in giant_belt:
        for material_id in giant_belt['from']:
            if material_id in data['data']:
                material = data['data'][material_id]
                print(f'- {material["name"]} (ID: {material_id}, 価格: {material["gold"]["total"]})')
    else:
        print('- なし（基本アイテム）')
    print()

    # 2. Find items that use Giant's Belt (parents in the tree structure)
    print('【2. ジャイアントベルトを使って作れるアイテム（親アイテム）】')
    items_using_giant_belt = []
    for item_id, item in data['data'].items():
        if 'from' in item and giant_belt_id in item['from']:
            items_using_giant_belt.append({
                'id': item_id,
                'name': item['name'],
                'total_cost': item['gold']['total'],
                'materials': item.get('from', [])
            })
    
    for item in sorted(items_using_giant_belt, key=lambda x: x['total_cost']):
        materials_names = []
        for mat_id in item['materials']:
            if mat_id in data['data']:
                materials_names.append(data['data'][mat_id]['name'])
        print(f'- {item["name"]} (ID: {item["id"]}, 価格: {item["total_cost"]})')
        print(f'  すべての素材: {", ".join(materials_names)}')
    print()

    # 3. Find sibling items (other items made from Ruby Crystal)
    print('【3. 兄弟アイテム（ルビークリスタルを使う他のアイテム）】')
    items_using_ruby = []
    for item_id, item in data['data'].items():
        if 'from' in item and ruby_crystal_id in item['from']:
            items_using_ruby.append({
                'id': item_id,
                'name': item['name'],
                'total_cost': item['gold']['total'],
                'materials': item.get('from', [])
            })

    # Filter out Giant's Belt itself and categorize by complexity
    direct_siblings = []  # Only Ruby Crystal
    complex_siblings = []  # Ruby Crystal + other materials
    
    for item in items_using_ruby:
        if item['id'] != giant_belt_id:
            if len(item['materials']) == 1:
                direct_siblings.append(item)
            else:
                complex_siblings.append(item)

    print('【3a. 直接の兄弟（ルビークリスタル単体から作成）】')
    for sibling in sorted(direct_siblings, key=lambda x: x['total_cost']):
        print(f'- {sibling["name"]} (ID: {sibling["id"]}, 価格: {sibling["total_cost"]})')

    print('\n【3b. 複合兄弟（ルビークリスタル + 他素材から作成）】')
    for sibling in sorted(complex_siblings, key=lambda x: x['total_cost']):
        materials_names = []
        for mat_id in sibling['materials']:
            if mat_id in data['data']:
                materials_names.append(data['data'][mat_id]['name'])
        print(f'- {sibling["name"]} (ID: {sibling["id"]}, 価格: {sibling["total_cost"]})')
        print(f'  すべての素材: {", ".join(materials_names)}')
    print()

    # 4. Analyze cousin relationships (grandchildren)
    print('【4. 従兄弟関係（孫アイテム - ジャイアントベルト製アイテムから作られるアイテム）】')
    grandchildren = []
    for parent_item in items_using_giant_belt:
        for item_id, item in data['data'].items():
            if 'from' in item and parent_item['id'] in item['from']:
                materials_names = []
                for mat_id in item['from']:
                    if mat_id in data['data']:
                        materials_names.append(data['data'][mat_id]['name'])
                grandchildren.append({
                    'name': item['name'],
                    'id': item_id,
                    'cost': item['gold']['total'],
                    'parent': parent_item['name'],
                    'materials': materials_names
                })

    for grandchild in sorted(grandchildren, key=lambda x: x['cost']):
        print(f'- {grandchild["name"]} (ID: {grandchild["id"]}, 価格: {grandchild["cost"]})')
        print(f'  直接の親: {grandchild["parent"]}')
        print(f'  すべての素材: {", ".join(grandchild["materials"])}')
    print()

    # 5. Summary for quiz context
    print('【5. クイズにおける関係性まとめ】')
    total_family = len(direct_siblings) + len(complex_siblings) + len(items_using_giant_belt) + len(grandchildren) + 1  # +1 for Ruby Crystal
    print(f'- 拡張ファミリー総数: {total_family} アイテム')
    print(f'- 直接の兄弟: {len(direct_siblings)} アイテム')
    print(f'- 複合兄弟: {len(complex_siblings)} アイテム') 
    print(f'- 子アイテム（ジャイアントベルト使用）: {len(items_using_giant_belt)} アイテム')
    print(f'- 孫アイテム: {len(grandchildren)} アイテム')
    print(f'- 素材: 1 アイテム（ルビークリスタル）')

if __name__ == '__main__':
    analyze_giant_belt()