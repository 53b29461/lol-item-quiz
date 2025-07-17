#!/usr/bin/env python3
"""
キンドルジェム、ファージ、ランデュインオーメン、クリスタラインブレーサーの素材確認
"""

import requests

patch_version = "15.13.1"

def check_extended_materials():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== 拡張素材調査 ===')
    
    # 調査対象アイテム
    items_to_check = {
        '3067': 'キンドルジェム',
        '3044': 'ファージ', 
        '3143': 'ランデュインオーメン',
        '3801': 'クリスタラインブレーサー'
    }
    
    for item_id, jp_name in items_to_check.items():
        if item_id in data['data']:
            item = data['data'][item_id]
            price = item['gold']['total']
            print(f'\n🔍 {jp_name} ({item_id}): {price}G')
            print(f'  英語名: {item["name"]}')
            
            if 'from' in item:
                print(f'  素材ID: {item["from"]}')
                for material_id in item['from']:
                    if material_id in data['data']:
                        material = data['data'][material_id]
                        material_price = material['gold']['total']
                        print(f'    - {material["name"]} (ID: {material_id}, {material_price}G)')
            else:
                print('  素材: なし（基本アイテム）')
    
    # 価格帯別の分類（新基準1600G）
    print(f'\n📊 新価格帯分類（1600G基準）:')
    all_items = {}
    
    # 既存のアイテム
    existing_items = {
        'giants-belt': '1011',
        'ruby-crystal': '1028', 
        'parent-3083': '3083',  # Warmog's Armor
        'parent-3143': '3143',  # Randuin's Omen
        'parent-3116': '3116',  # Rylai's Crystal Scepter
        'parent-3084': '3084',  # Heartsteel
        'child-parent-3067': '3067',  # Kindlegem
        'child-parent-3066': '3066',  # Winged Moonplate
        'child-parent-3044': '3044',  # Phage
        'material-3801': '3801',  # Crystalline Bracer
        'material-3082': '3082',  # Warden's Mail
        'material-1026': '1026',  # Blasting Wand
        'material-1052': '1052'   # Amplifying Tome
    }
    
    all_items.update(existing_items)
    
    # 新しく追加する素材を調査
    new_materials = {}
    for item_id, jp_name in items_to_check.items():
        if item_id in data['data'] and 'from' in data['data'][item_id]:
            for material_id in data['data'][item_id]['from']:
                if material_id in data['data']:
                    material_name = data['data'][material_id]['name']
                    new_materials[f'new-material-{material_id}'] = material_id
    
    all_items.update(new_materials)
    
    # 価格帯別分類
    basic_items = []      # 799G以下
    intermediate_items = [] # 800-1600G
    legendary_items = []   # 1601G+
    
    for node_id, item_id in all_items.items():
        if item_id in data['data']:
            item = data['data'][item_id]
            price = item['gold']['total']
            name = item['name']
            
            if price <= 799:
                basic_items.append((node_id, item_id, name, price))
            elif price <= 1600:
                intermediate_items.append((node_id, item_id, name, price))
            else:
                legendary_items.append((node_id, item_id, name, price))
    
    print(f'\n🟢 素材アイテム（799G以下）:')
    for node_id, item_id, name, price in sorted(basic_items, key=lambda x: x[3]):
        print(f'  {name}: {price}G ({node_id})')
    
    print(f'\n🔵 中間アイテム（800-1600G）:')
    for node_id, item_id, name, price in sorted(intermediate_items, key=lambda x: x[3]):
        print(f'  {name}: {price}G ({node_id})')
    
    print(f'\n🟡 レジェンダリーアイテム（1601G+）:')
    for node_id, item_id, name, price in sorted(legendary_items, key=lambda x: x[3]):
        print(f'  {name}: {price}G ({node_id})')

if __name__ == "__main__":
    check_extended_materials()