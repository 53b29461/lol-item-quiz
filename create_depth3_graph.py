#!/usr/bin/env python3
"""
Giant's Beltを中心とした深さ3のグラフ構造を作成
"""

import requests
import json

patch_version = "15.13.1"

def create_depth3_graph():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== STEP 4: Giant\'s Belt中心の深さ3グラフ構造 ===')

    giants_belt_id = '1011'
    giants_belt = data['data'][giants_belt_id]
    
    # グラフ構造
    graph = {
        'center': {
            'id': giants_belt_id,
            'name': giants_belt['name'],
            'type': 'target'
        },
        'children': [],  # 素材（深さ-1）
        'parents': [],   # 直接の親（深さ+1）
        'grandparents': [], # 孫（深さ+2）
        'child_siblings': [], # 子の兄弟（深さ-1）
        'parent_siblings': [] # 親の兄弟（深さ+1）
    }
    
    # 1. 子アイテム（素材）
    if 'from' in giants_belt:
        for child_id in giants_belt['from']:
            if child_id in data['data']:
                child = data['data'][child_id]
                graph['children'].append({
                    'id': child_id,
                    'name': child['name'],
                    'type': 'child'
                })
    
    # 2. 親アイテム（Giant's Beltを使って作るもの）
    for item_id, item in data['data'].items():
        if 'from' in item and giants_belt_id in item['from']:
            graph['parents'].append({
                'id': item_id,
                'name': item['name'],
                'type': 'parent',
                'materials': item['from']
            })
    
    # 最も関連性の高い親アイテムを5個選択（ゲームで重要なもの）
    important_parents = [
        '3083',  # Warmog's Armor
        '3143',  # Randuin's Omen  
        '3116',  # Rylai's Crystal Scepter
        '3084',  # Heartsteel
        '6665'   # Jak'Sho, The Protean
    ]
    
    graph['parents'] = [p for p in graph['parents'] if p['id'] in important_parents]
    
    # 3. 祖父母アイテム（親の親）
    for parent in graph['parents']:
        for item_id, item in data['data'].items():
            if 'from' in item and parent['id'] in item['from']:
                graph['grandparents'].append({
                    'id': item_id,
                    'name': item['name'],
                    'type': 'grandparent',
                    'parent_id': parent['id']
                })
    
    # 祖父母は最大3個まで
    graph['grandparents'] = graph['grandparents'][:3]
    
    # 4. 子の兄弟（Ruby Crystalを使う他のアイテム）
    if graph['children']:
        ruby_crystal_id = graph['children'][0]['id']
        sibling_count = 0
        for item_id, item in data['data'].items():
            if ('from' in item and ruby_crystal_id in item['from'] and 
                item_id != giants_belt_id and sibling_count < 3):
                graph['child_siblings'].append({
                    'id': item_id,
                    'name': item['name'],
                    'type': 'child_sibling'
                })
                sibling_count += 1
    
    # 5. 親の兄弟（共通素材を持つアイテム）
    parent_sibling_count = 0
    for parent in graph['parents'][:2]:  # 最初の2つの親について
        if parent_sibling_count >= 4:
            break
        for material_id in parent['materials']:
            if material_id != giants_belt_id and parent_sibling_count < 4:
                for item_id, item in data['data'].items():
                    if ('from' in item and material_id in item['from'] and 
                        item_id != parent['id'] and giants_belt_id not in item.get('from', []) and
                        parent_sibling_count < 4):
                        graph['parent_siblings'].append({
                            'id': item_id,
                            'name': item['name'],
                            'type': 'parent_sibling',
                            'shared_material': material_id
                        })
                        parent_sibling_count += 1
                        break
    
    # 結果出力
    print(f'\\n🎯 中心: {graph["center"]["name"]}')
    
    print(f'\\n📥 子アイテム（素材）: {len(graph["children"])}個')
    for child in graph['children']:
        print(f'  - {child["name"]} (ID: {child["id"]})')
    
    print(f'\\n📤 親アイテム: {len(graph["parents"])}個')
    for parent in graph['parents']:
        print(f'  - {parent["name"]} (ID: {parent["id"]})')
    
    print(f'\\n🔺 祖父母アイテム: {len(graph["grandparents"])}個')
    for grandparent in graph['grandparents']:
        print(f'  - {grandparent["name"]} (ID: {grandparent["id"]})')
    
    print(f'\\n🔄 子の兄弟: {len(graph["child_siblings"])}個')
    for sibling in graph['child_siblings']:
        print(f'  - {sibling["name"]} (ID: {sibling["id"]})')
    
    print(f'\\n🔄 親の兄弟: {len(graph["parent_siblings"])}個')
    for sibling in graph['parent_siblings']:
        print(f'  - {sibling["name"]} (ID: {sibling["id"]})')
    
    # Cytoscape用のデータ生成
    print(f'\\n=== Cytoscape.js用データ生成 ===')
    
    # ノード生成
    nodes = []
    edges = []
    
    # 中心ノード
    nodes.append(f"{{ data: {{ id: 'giants-belt', label: 'Giant\\'s\\\\nBelt', type: 'target' }} }}")
    
    # 子ノード
    for child in graph['children']:
        node_id = child['id'].replace("'", "\\'")
        label = child['name'].replace("'", "\\'").replace(' ', '\\\\n')
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'child' }} }}")
        edges.append(f"{{ data: {{ source: '{node_id}', target: 'giants-belt', type: 'parent-child' }} }}")
    
    # 親ノード
    for parent in graph['parents']:
        node_id = parent['id'].replace("'", "\\'")
        label = parent['name'].replace("'", "\\'").replace(' ', '\\\\n')
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'parent' }} }}")
        edges.append(f"{{ data: {{ source: 'giants-belt', target: '{node_id}', type: 'parent-child' }} }}")
    
    # 子の兄弟ノード
    for sibling in graph['child_siblings']:
        node_id = sibling['id'].replace("'", "\\'")
        label = sibling['name'].replace("'", "\\'").replace(' ', '\\\\n')
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'child_sibling' }} }}")
        if graph['children']:
            child_id = graph['children'][0]['id']
            edges.append(f"{{ data: {{ source: '{child_id}', target: '{node_id}', type: 'sibling' }} }}")
    
    # 親の兄弟ノード
    for sibling in graph['parent_siblings'][:3]:  # 最大3個
        node_id = sibling['id'].replace("'", "\\'")
        label = sibling['name'].replace("'", "\\'").replace(' ', '\\\\n')
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'parent_sibling' }} }}")
        edges.append(f"{{ data: {{ source: 'giants-belt', target: '{node_id}', type: 'cousin' }} }}")
    
    print(f'\\n// ノード ({len(nodes)}個)')
    for node in nodes:
        print(f'    {node},')
    
    print(f'\\n// エッジ ({len(edges)}個)')
    for edge in edges:
        print(f'    {edge},')

if __name__ == "__main__":
    create_depth3_graph()