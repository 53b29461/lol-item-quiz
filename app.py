from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import requests
import random
import os
from urllib.parse import quote
from argon2 import PasswordHasher
import base64
import hashlib


app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'lol-item-quiz-secret-key-for-session-management-2025'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

patch_version = "15.18.1"

def get_items_data():
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json"
    response = requests.get(url)
    return response.json()

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
        'image_url': f"https://ddragon.leagueoflegends.com/cdn/{patch_version}/img/item/{item['image']['full']}",  # 画像URLを追加
        'tags': item.get('tags', [])
    }
    return node

def get_tree_item_names(tree, trees):
    if tree is None:
        return []
    names = [tree['name']]
    for parent_id in tree['parents']:
        names.extend(get_tree_item_names(trees[parent_id], trees))
    return names


def check_answers(selected_item_names, tree_item_names, user_answers):
    correct_answers = set([name for name in selected_item_names if name in tree_item_names])
    if correct_answers == set(user_answers):
        return f"oooo(*^▽^*)oooo"
    else:
        return f"(´・ω・`)"

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

    # Remove 500G filter to allow basic materials in choices
    # extended_family = [family_id for family_id in extended_family if items[family_id]['gold']['total'] >= 500]

    return extended_family

@app.route('/')
def index():
    session.clear()
    return render_template('index.html', patch_version=patch_version)

@app.route('/quiz_a_algorithm')
def quiz_a_algorithm():
    return render_template('quiz_a_algorithm.html', patch_version=patch_version)

@app.route('/quiz_a_algorithm_v2')
def quiz_a_algorithm_v2():
    return render_template('quiz_a_algorithm_v2.html', patch_version=patch_version)

@app.route('/quiz_a_full_graph')
def quiz_a_full_graph():
    return render_template('quiz_a_full_graph.html', patch_version=patch_version)

@app.route('/quiz_a', methods=['GET', 'POST'])
def quiz_a():
    submitted = False
    result = None
    is_correct = None
    sentakusi = 10
    consecutive_correct_answers = session.get('consecutive_correct_answers', 0)  # 連続正解回数をセッションから取得
    previous_consecutive_correct_answers = session.get('previous_consecutive_correct_answers', 0)

    if request.method == 'POST':
        options = session.get('options')
        answers = session.get('correct_answers')
        user_answers = request.form.getlist('answer')
        result = check_answers(options, answers, user_answers)
        session['result'] = result
        submitted = True
        answer_marks = [{ 'name': name, 'is_correct': (name in answers), 'checked': (name in user_answers) } for name in options]
        
        # 連続正解回数の更新
        if session['result'] == "oooo(*^▽^*)oooo":
            consecutive_correct_answers += 1
            is_correct = True
        else:
            consecutive_correct_answers = 0
            previous_consecutive_correct_answers = session.get('consecutive_correct_answers', 0)
            is_correct = False

        session['consecutive_correct_answers'] = consecutive_correct_answers  # セッションに保存
        session['previous_consecutive_correct_answers'] = previous_consecutive_correct_answers
    else:
        session['previous_consecutive_correct_answers'] = 0
        data = get_items_data()
        all_items = {item_id: item for item_id, item in data['data'].items() if item.get('requiredAlly') != 'Ornn'}
        filtered_items = filter_items(all_items)
        all_trees = {item_id: build_item_tree(item_id, filtered_items) for item_id in filtered_items}
        connect_parents(filtered_items, all_trees)

        large_trees = {item_id: tree for item_id, tree in all_trees.items() if tree and len(get_tree_item_names(tree, all_trees)) >= 5}
        session['item_id'] = random.choice(list(large_trees.keys()))
        extended_family = get_extended_family(session.get('item_id'), all_trees, all_items)
        extended_family_names = [filtered_items[family_id]['name'] for family_id in extended_family if family_id != session.get('item_id')]
        
        # Remove duplicates by converting to set, then back to list
        unique_extended_family_names = list(set(extended_family_names))
        
        # Use all available unique items, up to sentakusi (10) max
        max_options = min(len(unique_extended_family_names), sentakusi)
        session['options'] = random.sample(unique_extended_family_names, max_options)
        session['item_tree'] = large_trees[session.get('item_id')]
        session['correct_answers'] = get_tree_item_names(session.get('item_tree'), all_trees)[1:]
        answer_marks = [{ 'name': name, 'is_correct': False, 'checked': False } for name in session.get('options')]

    result = session.pop('result', None)

    return render_template('quiz_a.html', 
                           result=result, 
                           submitted=submitted, 
                           is_correct=is_correct,
                           item=session.get('item_tree'),
                           answer_marks=answer_marks, 
                           consecutive_correct_answers=consecutive_correct_answers, 
                           previous_consecutive_correct_answers=previous_consecutive_correct_answers,
                           patch_version=patch_version)

@app.route('/quiz_b', methods=['GET', 'POST'])
def quiz_b():
    submitted = False
    result = None
    is_correct = None
    consecutive_correct_answers = session.get('consecutive_correct_answers', 0)  # 連続正解回数をセッションから取得
    previous_consecutive_correct_answers = session.get('previous_consecutive_correct_answers', 0)

    if request.method == 'POST':
        selected_item = session.get('selected_item')
        if not request.form.get('price'):
            user_answer = 0
        else:
            user_answer = int(request.form.get('price'))
        correct_answer = session.get('correct_price')
        submitted = True
        if user_answer == correct_answer:
            result = "正解です！"
            consecutive_correct_answers += 1
            is_correct = True
        else:
            result = f"不正解です。正解は {correct_answer} です。"
            consecutive_correct_answers = 0
            previous_consecutive_correct_answers = session.get('consecutive_correct_answers', 0)
            is_correct = False

        session['result'] = result
        session['consecutive_correct_answers'] = consecutive_correct_answers  # セッションに保存
        session['previous_consecutive_correct_answers'] = previous_consecutive_correct_answers
    else:
        session['previous_consecutive_correct_answers'] = 0
        data = get_items_data()
        items_dict = {item_id: item for item_id, item in data['data'].items() if item.get('requiredAlly') != 'Ornn'}
        filtered_items_dict = filter_items(items_dict)
        filtered_items_list = list(filtered_items_dict.values())
        selected_item = random.choice(filtered_items_list)
        session['selected_item'] = selected_item
        session['correct_price'] = selected_item['gold']['total']

    result = session.pop('result', None)

    return render_template('quiz_b.html', 
                           item=selected_item, 
                           result=result, 
                           submitted=submitted,
                           is_correct=is_correct,
                           consecutive_correct_answers=consecutive_correct_answers, 
                           previous_consecutive_correct_answers=previous_consecutive_correct_answers,
                           patch_version=patch_version)  

@app.route('/next_question_a', methods=['GET'])
def next_question_a():
    session.pop('submitted', None)
    session.pop('result', None)
    return redirect(url_for('quiz_a'))

@app.route('/next_question_b', methods=['GET'])
def next_question_b():
    session.pop('submitted', None)
    session.pop('result', None)
    return redirect(url_for('quiz_b'))

@app.route('/etc')
def etc():
    return render_template('etc.html', patch_version=patch_version)

@app.route('/math-game')
def math_game():
    return render_template('math_game.html', patch_version=patch_version)

@app.route('/champion-4d-viz')
def champion_4d_viz():
    return render_template('champion_4d_viz.html')

def generate_argon_password(master_password, site_identifier, security_profile='default', 
                          password_length=64, include_symbols=True, include_numbers=True, 
                          include_uppercase=True, include_lowercase=True):
    """
    Argon2idを使用してカスタマイズ可能なパスワードを生成
    argonpassアルゴリズムの実装 + カスタマイズ機能
    """
    # セキュリティプロファイル設定
    profiles = {
        'fast': {'time_cost': 10, 'memory_cost': 64 * 1024, 'parallelism': 1},
        'balanced': {'time_cost': 25, 'memory_cost': 128 * 1024, 'parallelism': 1},
        'paranoid': {'time_cost': 50, 'memory_cost': 512 * 1024, 'parallelism': 1},
        'default': {'time_cost': 42, 'memory_cost': 256 * 1024, 'parallelism': 1}
    }
    
    profile = profiles.get(security_profile, profiles['default'])
    
    # 文字セットの構築
    charset = ""
    if include_lowercase:
        charset += "abcdefghijklmnopqrstuvwxyz"
    if include_uppercase:
        charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if include_numbers:
        charset += "0123456789"
    if include_symbols:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # 最低限の文字セットチェック
    if not charset:
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    # サイト識別子をソルトとして使用
    salt = hashlib.sha256(site_identifier.encode()).digest()[:16]
    
    # Argon2idでキー導出
    try:
        from argon2.low_level import hash_secret_raw, Type
        
        # 充分な長さのキーを生成（最大128文字対応）
        key_length = max(64, (password_length * 2) // 3 + 32)  
        
        key = hash_secret_raw(
            secret=master_password.encode(),
            salt=salt,
            time_cost=profile['time_cost'],
            memory_cost=profile['memory_cost'],
            parallelism=profile['parallelism'],
            hash_len=key_length,
            type=Type.ID  # Argon2id
        )
        
        # キーから指定文字セットでパスワード生成
        password = ""
        key_index = 0
        
        # 各文字タイプが最低1文字含まれるように最初に配置
        required_chars = []
        if include_lowercase and "abcdefghijklmnopqrstuvwxyz" in charset:
            required_chars.append("abcdefghijklmnopqrstuvwxyz"[key[key_index % len(key)] % 26])
            key_index += 1
        if include_uppercase and "ABCDEFGHIJKLMNOPQRSTUVWXYZ" in charset:
            required_chars.append("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[key[key_index % len(key)] % 26])
            key_index += 1
        if include_numbers and "0123456789" in charset:
            required_chars.append("0123456789"[key[key_index % len(key)] % 10])
            key_index += 1
        if include_symbols and "!@#$%^&*()_+-=[]{}|;:,.<>?" in charset:
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            required_chars.append(symbols[key[key_index % len(key)] % len(symbols)])
            key_index += 1
        
        # 残りの文字を生成
        for i in range(password_length - len(required_chars)):
            if key_index >= len(key):
                # キーが足りない場合は新しいキーを生成
                additional_salt = hashlib.sha256((site_identifier + str(i)).encode()).digest()[:16]
                additional_key = hash_secret_raw(
                    secret=master_password.encode(),
                    salt=additional_salt,
                    time_cost=profile['time_cost'],
                    memory_cost=profile['memory_cost'],
                    parallelism=profile['parallelism'],
                    hash_len=32,
                    type=Type.ID
                )
                key = key + additional_key
            
            char_index = key[key_index % len(key)] % len(charset)
            password += charset[char_index]
            key_index += 1
        
        # 必須文字を結果に混合（シャッフル）
        final_password = list(password + ''.join(required_chars))
        
        # キーベースでシャッフル（決定論的）
        for i in range(len(final_password)):
            j = key[(key_index + i) % len(key)] % len(final_password)
            final_password[i], final_password[j] = final_password[j], final_password[i]
        
        return ''.join(final_password[:password_length])
        
    except Exception as e:
        return None

@app.route('/argon2-algorithm')
def argon2_algorithm():
    return render_template('argon2_algorithm.html', patch_version=patch_version)

@app.route('/password-generator', methods=['GET', 'POST'])
def password_generator():
    generated_password = None
    error_message = None
    processing_time = None
    password_settings = {}
    
    if request.method == 'POST':
        master_password = request.form.get('master_password')
        site_identifier = request.form.get('site_identifier')
        security_profile = request.form.get('security_profile', 'default')
        
        # パスワードカスタマイズオプション
        password_length = int(request.form.get('password_length', 64))
        include_symbols = request.form.get('include_symbols') == 'on'
        include_numbers = request.form.get('include_numbers') == 'on'
        include_uppercase = request.form.get('include_uppercase') == 'on'
        include_lowercase = request.form.get('include_lowercase') == 'on'
        
        # 設定を保持（フォーム再表示用）
        password_settings = {
            'password_length': password_length,
            'include_symbols': include_symbols,
            'include_numbers': include_numbers,
            'include_uppercase': include_uppercase,
            'include_lowercase': include_lowercase,
            'security_profile': security_profile
        }
        
        if not master_password or not site_identifier:
            error_message = "マスターパスワードとサイト識別子の両方を入力してください"
        elif password_length < 4 or password_length > 128:
            error_message = "パスワード長は4-128文字の範囲で設定してください"
        elif not (include_symbols or include_numbers or include_uppercase or include_lowercase):
            error_message = "少なくとも1つの文字種を選択してください"
        else:
            import time
            start_time = time.time()
            
            generated_password = generate_argon_password(
                master_password=master_password,
                site_identifier=site_identifier,
                security_profile=security_profile,
                password_length=password_length,
                include_symbols=include_symbols,
                include_numbers=include_numbers,
                include_uppercase=include_uppercase,
                include_lowercase=include_lowercase
            )
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            if generated_password is None:
                error_message = "パスワード生成に失敗しました"
    else:
        # デフォルト設定
        password_settings = {
            'password_length': 64,
            'include_symbols': True,
            'include_numbers': True,
            'include_uppercase': True,
            'include_lowercase': True,
            'security_profile': 'default'
        }
    
    return render_template('password_generator.html', 
                         generated_password=generated_password,
                         error_message=error_message,
                         processing_time=processing_time,
                         password_settings=password_settings,
                         patch_version=patch_version)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 環境変数PORTからポート番号を取得
    app.run(host='0.0.0.0', port=port, debug=True)
