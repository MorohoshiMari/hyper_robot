#!/usr/bin/env python3
"""
sample5の設計・検証
"""

from collections import deque

BOARD = 16
CENTER = {(7,7),(7,8),(8,7),(8,8)}
COLORS = ['red','blue','yellow','green']

def is_center(i,j):
    return (i,j) in CENTER

def can_move_wall(i, j, di, dj, walls_h, walls_v):
    if di == -1:
        if i == 0: return False
        return not walls_v[i][j]
    elif di == 1:
        if i == BOARD-1: return False
        return not walls_v[i+1][j]
    elif dj == -1:
        if j == 0: return False
        return not walls_h[i][j]
    elif dj == 1:
        if j == BOARD-1: return False
        return not walls_h[i][j+1]
    return False

def compute_dest(ri, rj, color, robots, walls_h, walls_v, di, dj):
    i, j = ri, rj
    while True:
        if not can_move_wall(i, j, di, dj, walls_h, walls_v):
            break
        ni, nj = i+di, j+dj
        if is_center(ni, nj):
            break
        occupied = any(robots[c] == (ni,nj) for c in COLORS if c != color)
        if occupied:
            break
        i, j = ni, nj
    return (i, j)

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

def bfs(target_color, robots_init, chips, walls_h, walls_v, max_depth=10):
    goal = chips[target_color]

    def to_state(r):
        return tuple(r[c] for c in COLORS)

    if robots_init[target_color] == goal:
        return 0, []

    init_state = to_state(robots_init)
    queue = deque()
    queue.append((init_state, 0, []))
    visited = {init_state}

    while queue:
        state, depth, path = queue.popleft()
        if depth >= max_depth:
            continue

        robots = {c: state[i] for i,c in enumerate(COLORS)}

        for color in COLORS:
            ri, rj = robots[color]
            for di, dj in DIRECTIONS:
                dest = compute_dest(ri, rj, color, robots, walls_h, walls_v, di, dj)
                if dest == robots[color]:
                    continue

                new_robots = dict(robots)
                new_robots[color] = dest
                new_state = to_state(new_robots)

                if new_state in visited:
                    continue
                visited.add(new_state)

                new_path = path + [(color, di, dj, dest)]
                if new_robots[target_color] == goal:
                    return depth+1, new_path

                queue.append((new_state, depth+1, new_path))

    return None, None

def dir_name(di, dj):
    return {(-1,0):"上",(1,0):"下",(0,-1):"左",(0,1):"右"}[(di,dj)]

def make_walls():
    return [[False]*16 for _ in range(16)]

def set_wall_h(walls_h, i, j):
    assert 1 <= j <= 15
    walls_h[i][j] = True

def set_wall_v(walls_v, i, j):
    assert 1 <= i <= 15
    walls_v[i][j] = True

def encode_walls(walls_h, walls_v):
    s_lines = []
    for i in range(16):
        row = ""
        for j in range(1, 16):
            row += "1" if walls_h[i][j] else "0"
        s_lines.append(row)
    t_lines = []
    for j in range(16):
        col = ""
        for i in range(1, 16):
            col += "1" if walls_v[i][j] else "0"
        t_lines.append(col)
    return s_lines, t_lines

def build_problem_text(robots, chips, walls_h, walls_v):
    s_lines, t_lines = encode_walls(walls_h, walls_v)
    lines = []
    for c in COLORS:
        ri,rj = robots[c]
        ci,cj = chips[c]
        lines.append(f"{ri} {rj} {ci} {cj}")
    lines.extend(s_lines)
    lines.extend(t_lines)
    return "\n".join(lines) + "\n"

def verify(robots, chips, walls_h, walls_v, name):
    print(f"\n=== {name} ===")
    all_ok = True
    for color in COLORS:
        depth, path = bfs(color, robots, chips, walls_h, walls_v, max_depth=10)
        if depth is None:
            print(f"  [{color:6s}] 解なし (10手以内)")
            all_ok = False
        else:
            steps = " -> ".join(f"{p[0]} {dir_name(p[1],p[2])}" for p in path)
            status = "OK" if 3 <= depth <= 8 else f"範囲外({depth}手)"
            print(f"  [{color:6s}] {depth}手 [{status}]: {steps}")
            if depth < 3 or depth > 8:
                all_ok = False
    return all_ok

# ================================================================
# sample5 設計: 対称な配置で壁を活用するパズル
#
# 設計方針:
#   ロボットを四隅付近に配置し、チップを中央部寄りに配置
#   各色3〜5手で解けるよう壁を設置
#
# 赤(0,0) → chip(4,11):
#   (0,0)→下→(4,0)→右→(4,11) [壁で止まる] = 2手 (少なすぎ)
#   壁で(4,0)に止まれないようにし、別経路を使う
#   (0,0)→右→(0,11)→下→(4,11) [壁で止まる] = 2手 (少なすぎ)
#
# 2手にならないよう工夫: チップ位置を再考
# 赤(0,0) → chip(11,4):
#   直接経路: (0,0)→右→(0,4)→下→(11,4) [壁で止まる] = 2手
#   壁を使って2手直接経路をブロックし、3手にする
#
# もっとシンプルに: ロボット同士の連携で3〜5手にする配置

# 新しい設計:
# ロボット:
#   赤 (1, 1)
#   青 (1, 14)
#   黄 (14, 1)
#   緑 (14, 14)
#
# チップ:
#   赤 (9, 6)
#   青 (6, 9)
#   黄 (9, 9)
#   緑 (6, 6)
#
# 壁で各色3〜5手を実現

def make_sample5_v2():
    robots = {
        'red':    ( 1,  1),
        'blue':   ( 1, 14),
        'yellow': (14,  1),
        'green':  (14, 14),
    }
    chips = {
        'red':    ( 9,  6),
        'blue':   ( 6,  9),
        'yellow': ( 9,  9),
        'green':  ( 6,  6),
    }
    walls_h = make_walls()
    walls_v = make_walls()

    # 赤(1,1)→chip(9,6):
    # 案: (1,1)→右→(1,6)→下→(9,6) [壁でストップ]
    # (1,1)→右→(1,6): walls_h[1][7]=True でストップ
    # (1,6)→下→(9,6): walls_v[10][6]=True でストップ
    # = 2手 → 3手にするため工夫
    # 案: (1,1)→下→(9,1)→右→(9,6) [壁でストップ]
    # (1,1)→下→(9,1): walls_v[10][1]=True でストップ
    # (9,1)→右→(9,6): walls_h[9][7]=True でストップ
    # = 2手 → これも2手

    # 3手にするには間に他ロボットや壁が必要
    # 赤(1,1)→chip(9,6):
    # (1,1)→下→(14,1)[黄がいる行の手前、黄(14,1)がいるので(13,1)で止まる]
    # wait 黄(14,1)がいると赤は(13,1)で止まる
    # (13,1)→右→(13,?)→上→(9,?) ... 複雑すぎ

    # シンプルに、BFSで調べながら壁を調整する
    # まず壁なし状態でBFSを確認
    r0 = verify(robots, chips, walls_h, walls_v, "sample5_v2 壁なし")

    return robots, chips, walls_h, walls_v

r, c, wh, wv = make_sample5_v2()

# 壁なし確認後、壁を追加

# 再設計: 各色について手動で解を設計
# robots を少し変更して、より良い配置を見つける

def make_sample5_final():
    # 設計:
    # 赤(0, 3) → chip(5, 11)
    #   (0,3)→右→(0,11)→下→(5,11) [壁でストップ] = 2手 → walls_h[5][12]=True
    #   2手なので3手にする: (0,3)→下→(5,3)→右→(5,11) [壁でストップ] も2手
    #   3手: 他ロボットを踏み台にする
    #   青(3,0)にいると: (0,3)→左→(0,0)→下→(5,0)→右→(5,11) [壁]
    #   walls_h[5][12]=True でストップ = 3手 ✓

    # 青(3,0) → chip(11,6)
    #   (3,0)→下→(15,0)→右→(15,6)→上→(11,6) [壁でストップ]
    #   walls_v[12][6]=True でストップ = 3手 ✓

    # 黄(0,12) → chip(11,3)
    #   (0,12)→右→(0,15)→下→(15,15)→左→(15,3)→上→(11,3)
    #   walls_v[12][3]=True でストップ = 4手
    #   あるいは: (0,12)→下→(5,12)→左→(5,3)→下→(11,3) [壁]
    #   walls_v[12][3]=True でストップ = 3手 ✓
    #   (0,12)→下→(5,12): walls_v[6][12]=True でストップ
    #   (5,12)→左→(5,3): walls_h[5][4]=True でストップ... wait walls_h[5][3]は左端ではなくマス(5,2)と(5,3)の間
    #   左移動で(5,3)に止まるには walls_h[5][3]=True (マス(5,2)と(5,3)の間に壁)
    #   ただし左から来る場合: (5,12)→左→...→(5,3) で止まるには walls_h[5][3]=True

    # 緑(12,15) → chip(6,4)
    #   (12,15)→上→(6,15)→左→(6,4) [壁でストップ]
    #   walls_h[6][5]=True でストップ = 2手 → 3手に
    #   (12,15)→左→(12,0)→上→(6,0)→右→(6,4) [壁]
    #   walls_h[6][5]=True でストップ = 3手 ✓

    robots = {
        'red':    ( 0,  3),
        'blue':   ( 3,  0),
        'yellow': ( 0, 12),
        'green':  (12, 15),
    }
    chips = {
        'red':    ( 5, 11),
        'blue':   (11,  6),
        'yellow': (11,  3),
        'green':  ( 6,  4),
    }
    walls_h = make_walls()
    walls_v = make_walls()

    # 赤の解: (0,3)→左→(0,0)→下→(5,0)→右→(5,11) [walls_h[5][12]]
    # (0,3)→左→(0,0): 左端でストップ ✓
    # (0,0)→下→(5,0): 何かで止まる必要 walls_v[6][0]
    set_wall_v(walls_v, 6, 0)
    # (5,0)→右→(5,11): walls_h[5][12]
    set_wall_h(walls_h, 5, 12)

    # 青の解: (3,0)→下→(15,0)→右→(15,6)→上→(11,6)
    # (3,0)→下→(15,0): 下端でストップ ✓
    # (15,0)→右→(15,6): walls_h[15][7]
    set_wall_h(walls_h, 15, 7)
    # (15,6)→上→(11,6): walls_v[12][6]
    set_wall_v(walls_v, 12, 6)

    # 黄の解: (0,12)→下→(5,12)→左→(5,3)→下→(11,3)
    # (0,12)→下→(5,12): walls_v[6][12]
    set_wall_v(walls_v, 6, 12)
    # (5,12)→左→(5,3): walls_h[5][3] (マス(5,2)と(5,3)の間)
    set_wall_h(walls_h, 5, 3)
    # (5,3)→下→(11,3): walls_v[12][3]
    set_wall_v(walls_v, 12, 3)

    # 緑の解: (12,15)→左→(12,0)→上→(6,0)→右→(6,4)
    # (12,15)→左→(12,0): 左端でストップ ✓
    # (12,0)→上→(6,0): walls_v[6][0] はすでに設置済み... wait
    # walls_v[6][0]はマス(5,0)とマス(6,0)の間の壁
    # (12,0)→上→上方向に移動: 壁があるマスで止まる
    # walls_v[6][0]=True → マス(5,0)と(6,0)の間に壁 → (12,0)から上に移動すると(6,0)で止まる ✓
    # (6,0)→右→(6,4): walls_h[6][5]
    set_wall_h(walls_h, 6, 5)

    return robots, chips, walls_h, walls_v

print("\n" + "="*60)
print("sample5_final の検証")
print("="*60)

robots5, chips5, walls_h5, walls_v5 = make_sample5_final()
ok = verify(robots5, chips5, walls_h5, walls_v5, "sample5_final")

if ok:
    text = build_problem_text(robots5, chips5, walls_h5, walls_v5)
    print("\n--- sample5.txt ---")
    print(text)
else:
    print("\n再設計が必要です")

    # BFSで実際の解経路をもう少し詳しく確認
    print("\n詳細解析:")
    for color in COLORS:
        depth, path = bfs(color, robots5, chips5, walls_h5, walls_v5, max_depth=12)
        if depth is None:
            print(f"  [{color}] 12手以内で解なし")
        else:
            steps = " -> ".join(f"{p[0]} {dir_name(p[1],p[2])}→{p[3]}" for p in path)
            print(f"  [{color}] {depth}手: {steps}")
