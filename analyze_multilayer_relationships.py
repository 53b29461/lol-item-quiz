#!/usr/bin/env python3
"""
Giant's Belt周辺の多層的な親子関係を整理
"""

import requests
from collections import defaultdict

patch_version = "15.13.1"

def analyze_multilayer_relationships():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== Giant\'s Belt周辺の多層的親子関係分析 ===')
    
    giants_belt_id = '1011'
    ruby_crystal_id = '1028'
    
    # STEP 1: Ruby Crystal（子）の異なる親たち
    print(f'\n🔍 STEP 1: Ruby Crystal（子）の異なる親たち')
    print(f'Ruby Crystal (ID: {ruby_crystal_id}) から作られるアイテム：')
    
    ruby_parents = []
    for item_id, item in data['data'].items():
        if 'from' in item and ruby_crystal_id in item['from']:
            ruby_parents.append({
                'id': item_id,
                'name': item['name'],
                'gold': item['gold']['total'],
                'materials': item['from'],
                'is_giants_belt': item_id == giants_belt_id
            })
    
    ruby_parents.sort(key=lambda x: x['gold'])
    
    giants_belt_info = None
    other_parents = []
    
    for parent in ruby_parents:
        if parent['is_giants_belt']:
            giants_belt_info = parent
        else:
            other_parents.append(parent)
            
    print(f'  🎯 Giant\'s Belt: {giants_belt_info["name"]} ({giants_belt_info["gold"]}G)')
    
    print(f'  📋 他の親アイテム ({len(other_parents)}個):')
    for i, parent in enumerate(other_parents[:10]):  # 最初の10個
        materials_names = [data['data'][mid]['name'] for mid in parent['materials'] if mid in data['data']]
        print(f'    {i+1:2d}. {parent["name"]} ({parent["gold"]}G)')
        print(f'        素材: {" + ".join(materials_names)}')
    
    if len(other_parents) > 10:
        print(f'    ... 他{len(other_parents) - 10}個')
    
    # STEP 2: Giant's Beltの各親の異なる子たち
    print(f'\n🔍 STEP 2: Giant\'s Beltの各親の異なる子たち')
    
    # Giant's Beltを使う親アイテムを取得
    giants_belt_parents = []
    for item_id, item in data['data'].items():
        if 'from' in item and giants_belt_id in item['from']:
            giants_belt_parents.append({
                'id': item_id,
                'name': item['name'],
                'materials': item['from']
            })
    
    giants_belt_parents.sort(key=lambda x: x['name'])
    
    for parent in giants_belt_parents[:5]:  # 最初の5個を詳細分析
        print(f'\\n  📤 親アイテム: {parent["name"]}')
        
        # この親の全ての子（素材）
        all_children = []
        for material_id in parent['materials']:
            if material_id in data['data']:
                material = data['data'][material_id]
                is_giants_belt = material_id == giants_belt_id
                all_children.append({
                    'id': material_id,
                    'name': material['name'],
                    'gold': material['gold']['total'],
                    'is_giants_belt': is_giants_belt
                })
        
        all_children.sort(key=lambda x: x['gold'])
        
        print(f'    必要な子アイテム ({len(all_children)}個):')
        for child in all_children:
            marker = '🎯' if child['is_giants_belt'] else '  '
            print(f'      {marker} {child["name"]} ({child["gold"]}G)')
        
        # 各子アイテムの兄弟を調査
        print(f'    各子の兄弟関係:')
        for child in all_children:
            if not child['is_giants_belt']:  # Giant's Belt以外
                # この子を使う他のアイテム（兄弟）
                siblings = []
                for item_id, item in data['data'].items():
                    if 'from' in item and child['id'] in item['from'] and item_id != parent['id']:
                        siblings.append(item['name'])
                
                sibling_count = len(siblings)
                print(f'      - {child["name"]}: {sibling_count}個の兄弟')
                if sibling_count <= 3:
                    for sibling in siblings:
                        print(f'        • {sibling}')
                else:
                    for sibling in siblings[:3]:
                        print(f'        • {sibling}')
                    print(f'        • ... 他{sibling_count - 3}個')
    
    # STEP 3: 関係ネットワークサマリー
    print(f'\\n🔍 STEP 3: 関係ネットワークサマリー')
    
    # Ruby Crystalのネットワーク
    ruby_network_size = len(ruby_parents)
    print(f'  🔸 Ruby Crystalのネットワーク: {ruby_network_size}個のアイテム')
    
    # Giant's Beltのネットワーク
    giants_belt_network_size = len(giants_belt_parents)
    print(f'  🔸 Giant\'s Beltのネットワーク: {giants_belt_network_size}個のアイテム')
    
    # 推奨グラフ構造
    print(f'\\n📊 推奨グラフ構造（深さ2-3レベル）:')
    print(f'  🎯 中心: Giant\'s Belt')
    print(f'  📥 下位層: Ruby Crystal + Ruby Crystalの代表的兄弟 3-4個')
    print(f'  📤 上位層: Giant\'s Beltの代表的親 4-5個')
    print(f'  🔄 関連層: 各親の他の子アイテム 2-3個')

if __name__ == "__main__":
    analyze_multilayer_relationships()