#!/usr/bin/env python3
import requests
import json

def get_items_data():
    patch_version = '15.13.1'
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json'
    response = requests.get(url)
    return response.json()

def filter_items(all_items):
    # Original filter logic from app.py
    map_filtered_items = {item_id: item for item_id, item in all_items.items() if item.get('maps', {}).get('11', False) and not all(item.get('maps', {}).get(map_id, False) for map_id in ['11', '12', '21', '30'])}
    
    target_tags = ['Consumable', 'Trinket', 'Boots', 'Jungle', 'Lane']
    exclude_item_names = ['ロング ソード']
    tag_filtered_items = {item_id: item for item_id, item in all_items.items() if any(tag in item.get('tags', []) for tag in target_tags) and item['name'] not in exclude_item_names}
    
    final_filtered_items = {item_id: item for item_id, item in map_filtered_items.items() if item_id not in tag_filtered_items}
    
    exclude_ids = ['6693', '6673', '4641', '4637', '1516', '1517', '1518', '1519']
    last_final_filtered_items = {item_id: item for item_id, item in final_filtered_items.items() if item_id not in exclude_ids}
    
    return last_final_filtered_items

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

def get_tree_item_names(tree, trees):
    if tree is None:
        return []
    names = [tree['name']]
    for parent_id in tree['parents']:
        names.extend(get_tree_item_names(trees[parent_id], trees))
    return names

def get_extended_family(item_id, trees, items):
    item_tree = trees.get(item_id)
    if item_tree is None:
        return []

    family = []
    if 'parents' in item_tree:
        family.extend(item_tree['parents'])
    if 'children' in item_tree:
        family.extend(item_tree['children'])
    
    extended_family = set(family)  # Use a set to avoid duplicates

    for family_member_id in family:
        family_member_family = []
        family_tree = trees.get(family_member_id)
        if family_tree:
            if 'parents' in family_tree:
                family_member_family.extend(family_tree['parents'])
            if 'children' in family_tree:
                family_member_family.extend(family_tree['children'])
        
        for family_member_family_id in family_member_family:
            family_member_family_member_tree = trees.get(family_member_family_id)
            if family_member_family_member_tree:
                family_member_family_member_family = []
                if 'parents' in family_member_family_member_tree:
                    family_member_family_member_family.extend(family_member_family_member_tree['parents'])
                if 'children' in family_member_family_member_tree:
                    family_member_family_member_family.extend(family_member_family_member_tree['children'])
                extended_family.update(family_member_family_member_family)

    return extended_family

def analyze_giant_belt_in_quiz():
    # Get and filter items exactly like the app does
    data = get_items_data()
    all_items = {item_id: item for item_id, item in data['data'].items() if item.get('requiredAlly') != 'Ornn'}
    filtered_items = filter_items(all_items)
    
    # Build trees exactly like the app does
    all_trees = {item_id: build_item_tree(item_id, filtered_items) for item_id in filtered_items}
    connect_parents(filtered_items, all_trees)

    giant_belt_id = '1011'
    ruby_crystal_id = '1028'

    print('=== 実際のクイズで使用されるジャイアントベルトの関係 ===\n')

    # Check if Giant's Belt and Ruby Crystal are in filtered items
    print(f'【フィルタリング結果】')
    print(f'ジャイアントベルトはフィルタリング後に含まれる: {giant_belt_id in filtered_items}')
    print(f'ルビークリスタルはフィルタリング後に含まれる: {ruby_crystal_id in filtered_items}')
    
    if giant_belt_id not in filtered_items:
        print('❌ ジャイアントベルトがフィルタリングで除外されています！')
        return
    
    print(f'✅ ジャイアントベルトはクイズで使用されます')
    print()

    # Get the tree for Giant's Belt
    giant_belt_tree = all_trees[giant_belt_id]
    tree_item_names = get_tree_item_names(giant_belt_tree, all_trees)
    
    print(f'【ジャイアントベルトのツリー構造】')
    print(f'アイテム名: {giant_belt_tree["name"]}')
    print(f'価格: {giant_belt_tree["gold"]}')
    print(f'ツリー内のアイテム名: {tree_item_names}')
    print(f'ツリーサイズ: {len(tree_item_names)} アイテム')
    print()

    # Check if it qualifies for large_trees (>= 5 items)
    is_large_tree = len(tree_item_names) >= 5
    print(f'【大きなツリー判定】')
    print(f'5アイテム以上の条件を満たすか: {is_large_tree}')
    if not is_large_tree:
        print('❌ ジャイアントベルトは小さなツリーのため、クイズの対象から除外される可能性があります！')
    else:
        print('✅ ジャイアントベルトは大きなツリーとして分類され、クイズの対象になります')
    print()

    # Get extended family (quiz choices)
    extended_family = get_extended_family(giant_belt_id, all_trees, all_items)
    extended_family_names = [filtered_items[family_id]['name'] for family_id in extended_family if family_id != giant_belt_id and family_id in filtered_items]
    unique_extended_family_names = list(set(extended_family_names))
    
    print(f'【クイズでの選択肢候補】')
    print(f'拡張ファミリーID数: {len(extended_family)}')
    print(f'フィルタリング後の拡張ファミリー名数: {len(extended_family_names)}')
    print(f'重複除去後の選択肢候補数: {len(unique_extended_family_names)}')
    print()
    
    print('選択肢候補リスト:')
    for name in sorted(unique_extended_family_names):
        print(f'  - {name}')
    print()

    # Correct answers
    correct_answers = tree_item_names[1:]  # Exclude the item itself
    print(f'【正解アイテム（ツリー内の他のアイテム）】')
    print(f'正解数: {len(correct_answers)}')
    for answer in correct_answers:
        print(f'  - {answer}')
    print()

    # Check if there are any correct answers in the choice pool
    correct_in_choices = [answer for answer in correct_answers if answer in unique_extended_family_names]
    print(f'【選択肢に含まれる正解】')
    print(f'選択肢に含まれる正解数: {len(correct_in_choices)}')
    for answer in correct_in_choices:
        print(f'  - {answer}')
    
    if len(correct_in_choices) == 0:
        print('❌ 警告: 選択肢に正解が含まれていません！')
    else:
        print(f'✅ 正解率: {len(correct_in_choices)}/{len(correct_answers)} = {len(correct_in_choices)/len(correct_answers)*100:.1f}%')

if __name__ == '__main__':
    analyze_giant_belt_in_quiz()