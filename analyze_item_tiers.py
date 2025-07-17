#!/usr/bin/env python3
"""
アイテムの価格帯分析と縦配置レイアウト設計
"""

import requests

patch_version = "15.13.1"

def analyze_item_tiers():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()

    print('=== アイテム価格帯分析（縦配置設計用） ===')
    
    # Giant's Beltグラフのアイテム
    giants_belt_items = {
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
    
    # Faerie Charmグラフのアイテム
    faerie_charm_items = {
        'faerie-charm': '1004',
        'parent-3012': '3012',    # Chalice of Blessing
        'material-1028': '1028'   # Ruby Crystal
    }
    
    def get_item_price(item_id):
        if item_id in data['data']:
            return data['data'][item_id]['gold']['total']
        return 0
    
    def get_item_name(item_id):
        if item_id in data['data']:
            return data['data'][item_id]['name']
        return 'Unknown'
    
    print(f'\\n📊 Giant\'s Beltグラフアイテム価格帯:')
    giants_items_with_price = []
    for node_id, item_id in giants_belt_items.items():
        price = get_item_price(item_id)
        name = get_item_name(item_id)
        giants_items_with_price.append((node_id, item_id, name, price))
    
    giants_items_with_price.sort(key=lambda x: x[3])  # 価格順ソート
    
    for node_id, item_id, name, price in giants_items_with_price:
        tier = 'レジェンダリー' if price >= 3000 else '中間' if price >= 800 else '素材'
        print(f'  {name} ({node_id}): {price}G - {tier}')
    
    print(f'\\n📊 Faerie Charmグラフアイテム価格帯:')
    faerie_items_with_price = []
    for node_id, item_id in faerie_charm_items.items():
        price = get_item_price(item_id)
        name = get_item_name(item_id)
        faerie_items_with_price.append((node_id, item_id, name, price))
    
    faerie_items_with_price.sort(key=lambda x: x[3])
    
    for node_id, item_id, name, price in faerie_items_with_price:
        tier = 'レジェンダリー' if price >= 3000 else '中間' if price >= 800 else '素材'
        print(f'  {name} ({node_id}): {price}G - {tier}')
    
    # Y座標配置設計
    print(f'\\n🎯 Y座標配置設計:')
    print(f'  上段（y: 60）: レジェンダリー（3000G+）')
    print(f'  中段（y: 180）: 中間アイテム（800-2999G）')
    print(f'  下段（y: 300）: 素材アイテム（799G以下）')
    
    # Giant's Belt用座標生成
    print(f'\\n📍 Giant\'s Belt新座標:')
    legendary_x = 150
    intermediate_x = 150
    basic_x = 150
    
    for node_id, item_id, name, price in giants_items_with_price:
        if price >= 3000:
            y = 60
            x = legendary_x
            legendary_x += 130
        elif price >= 800:
            y = 180
            x = intermediate_x
            intermediate_x += 130
        else:
            y = 300
            x = basic_x
            basic_x += 130
        
        print(f"        '{node_id}': {{ x: {x}, y: {y} }},  // {name} ({price}G)")
    
    # Faerie Charm用座標生成
    print(f'\\n📍 Faerie Charm新座標:')
    legendary_x = 200
    intermediate_x = 200
    basic_x = 200
    
    for node_id, item_id, name, price in faerie_items_with_price:
        if price >= 3000:
            y = 60
            x = legendary_x
            legendary_x += 130
        elif price >= 800:
            y = 180
            x = intermediate_x
            intermediate_x += 130
        else:
            y = 300
            x = basic_x
            basic_x += 130
        
        print(f"        '{node_id}': {{ x: {x}, y: {y} }},  // {name} ({price}G)")

if __name__ == "__main__":
    analyze_item_tiers()