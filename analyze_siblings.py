#!/usr/bin/env python3
"""
Giant's Beltの親アイテムの兄弟関係を調査
"""

import requests

patch_version = "15.13.1"

def analyze_siblings():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== STEP 2: 各親アイテムの兄弟調査 ===')

    # Giant's Beltを使う親アイテムのリスト
    giants_belt_id = '1011'
    parent_items = []
    for item_id, item in data['data'].items():
        if 'from' in item and giants_belt_id in item['from']:
            parent_items.append({
                'id': item_id,
                'name': item['name'],
                'materials': item['from']
            })

    parent_items.sort(key=lambda x: x['name'])

    for parent in parent_items:
        print(f'\n【親アイテム: {parent["name"]}】')
        print(f'  素材: {[data["data"][mid]["name"] for mid in parent["materials"] if mid in data["data"]]}')
        
        # この親アイテムの他の素材を使って作られる兄弟を探す
        siblings = set()
        
        for material_id in parent['materials']:
            if material_id != giants_belt_id:  # Giant's Belt以外の素材
                # この素材を使う他のアイテムを探す
                for item_id, item in data['data'].items():
                    if 'from' in item and material_id in item['from'] and item_id != parent['id']:
                        siblings.add((item_id, item['name']))
        
        print(f'  兄弟アイテム数: {len(siblings)}個')
        # 兄弟が多い場合は最初の5個だけ表示
        sibling_list = sorted(list(siblings), key=lambda x: x[1])
        for i, (sibling_id, sibling_name) in enumerate(sibling_list[:5]):
            print(f'    - {sibling_name} (ID: {sibling_id})')
        if len(sibling_list) > 5:
            print(f'    ... 他{len(sibling_list) - 5}個')

if __name__ == "__main__":
    analyze_siblings()