#!/usr/bin/env python3
"""
Ruby Crystal（Giant's Beltの子アイテム）の兄弟関係を調査
"""

import requests

patch_version = "15.13.1"

def analyze_ruby_siblings():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== STEP 3: Ruby Crystal（子アイテム）の兄弟調査 ===')

    ruby_crystal_id = '1028'
    ruby_crystal = data['data'][ruby_crystal_id]

    print(f'子アイテム: {ruby_crystal["name"]} (ID: {ruby_crystal_id})')

    # Ruby Crystalを使って作られるアイテム（Giant's Belt以外）
    siblings = []
    for item_id, item in data['data'].items():
        if 'from' in item and ruby_crystal_id in item['from'] and item_id != '1011':
            siblings.append({
                'id': item_id,
                'name': item['name'],
                'gold': item['gold']['total'],
                'materials': item['from']
            })

    siblings.sort(key=lambda x: x['gold'])

    print(f'\nRuby Crystalを使う兄弟アイテム: {len(siblings)}個')
    for sibling in siblings[:10]:  # 最初の10個
        materials_names = [data['data'][mid]['name'] for mid in sibling['materials'] if mid in data['data']]
        print(f'  - {sibling["name"]} (ID: {sibling["id"]}, {sibling["gold"]}G)')
        print(f'    素材: {" + ".join(materials_names)}')

    if len(siblings) > 10:
        print(f'  ... 他{len(siblings) - 10}個')

if __name__ == "__main__":
    analyze_ruby_siblings()