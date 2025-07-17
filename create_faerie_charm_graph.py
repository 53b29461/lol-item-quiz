#!/usr/bin/env python3
"""
Faerie Charmを中心とした5層構造のグラフを作成
"""

import requests

patch_version = "15.13.1"

def create_faerie_charm_graph():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== Faerie Charm 5層構造グラフ作成 ===')
    
    faerie_charm_id = '1004'
    
    # 1. 中心: Faerie Charm
    center = {
        'id': faerie_charm_id,
        'name': data['data'][faerie_charm_id]['name'],
        'type': 'center'
    }
    
    # 2. 中心の子: なし（基本アイテム）
    center_child = None
    
    # 3. 中心の親: Faerie Charmを使うアイテム（代表的な4個選択）
    center_parents_ids = ['3504', '3012', '3128', '3222']  # Ardent Censer, Chalice of Blessing, Harmonic Echo, Mikael's Crucible
    center_parents = []
    
    for parent_id in center_parents_ids:
        if parent_id in data['data']:
            item = data['data'][parent_id]
            if 'from' in item and faerie_charm_id in item['from']:
                center_parents.append({
                    'id': parent_id,
                    'name': item['name'],
                    'type': 'center_parent',
                    'materials': item['from']
                })
    
    # 4. 中心の子の別親: なし（基本アイテムなので子がない）
    child_other_parents = []
    
    # 5. 中心の親の別子: 各親の他の素材（Faerie Charm以外）
    parent_other_children = []
    used_materials = set()
    
    for parent in center_parents:
        for material_id in parent['materials']:
            if material_id != faerie_charm_id and material_id not in used_materials and material_id in data['data']:
                material = data['data'][material_id]
                parent_other_children.append({
                    'id': material_id,
                    'name': material['name'],
                    'type': 'parent_other_child',
                    'parent_id': parent['id']
                })
                used_materials.add(material_id)
                if len(parent_other_children) >= 4:  # 最大4個まで
                    break
        if len(parent_other_children) >= 4:
            break
    
    # 結果表示
    print(f'\\n🎯 中心: {center["name"]} (基本アイテム)')
    print(f'📥 中心の子: なし（基本アイテムのため）')
    
    print(f'\\n📤 中心の親 ({len(center_parents)}個):')
    for parent in center_parents:
        print(f'  - {parent["name"]} (ID: {parent["id"]})')
    
    print(f'\\n🔄 中心の子の別親: なし（子がないため）')
    
    print(f'\\n🔄 中心の親の別子 ({len(parent_other_children)}個):')
    for child in parent_other_children:
        parent_name = next((p['name'] for p in center_parents if p['id'] == child['parent_id']), 'Unknown')
        print(f'  - {child["name"]} (ID: {child["id"]}) <- {parent_name}の素材')
    
    # Cytoscape.js用データ生成
    print(f'\\n=== Faerie Charm Cytoscape.js用データ ===')
    
    # ノード生成
    nodes = []
    edges = []
    
    # 1. 中心ノード
    nodes.append("{ data: { id: 'faerie-charm', label: 'Faerie\\\\nCharm', type: 'center' } }")
    
    # 2. 中心の親ノード
    for parent in center_parents:
        node_id = f"parent-{parent['id']}"
        label = parent['name'].replace("'", "\\'").replace(' ', '\\\\n')
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'center_parent' }} }}")
        edges.append(f"{{ data: {{ source: 'faerie-charm', target: '{node_id}', type: 'parent-child' }} }}")
    
    # 3. 中心の親の別子ノード
    for child in parent_other_children:
        node_id = f"material-{child['id']}"
        label = child['name'].replace("'", "\\'").replace(' ', '\\\\n')
        parent_node_id = f"parent-{child['parent_id']}"
        nodes.append(f"{{ data: {{ id: '{node_id}', label: '{label}', type: 'parent_other_child' }} }}")
        edges.append(f"{{ data: {{ source: '{node_id}', target: '{parent_node_id}', type: 'child-parent' }} }}")
    
    print(f'\\n// ノード ({len(nodes)}個)')
    for node in nodes:
        print(f'    {node},')
    
    print(f'\\n// エッジ ({len(edges)}個)')
    for edge in edges:
        print(f'    {edge},')
    
    # レイアウト座標の提案
    print(f'\\n// レイアウト座標')
    print(f"positions: {{")
    print(f"    'faerie-charm': {{ x: 400, y: 250 }},")
    
    # 親アイテムを上部に配置
    for i, parent in enumerate(center_parents):
        x = 200 + i * 120
        print(f"    'parent-{parent['id']}': {{ x: {x}, y: 120 }},")
    
    # 親の別子を上部に配置
    for i, child in enumerate(parent_other_children):
        x = 180 + i * 110
        print(f"    'material-{child['id']}': {{ x: {x}, y: 50 }},")
    
    print(f"}}")

if __name__ == "__main__":
    create_faerie_charm_graph()