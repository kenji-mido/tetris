import random
import curses
import time

# ゲーム設定の定数
GAME_CONST = {
    # ゲームボードのサイズ
    'BOARD_HEIGHT': 22,      # ボードの高さ
    'BOARD_WIDTH': 12,       # ボードの幅
    'MIN_TERM_HEIGHT': 24,   # 必要な最小ターミナル高さ
    'MIN_TERM_WIDTH': 40,    # 必要な最小ターミナル幅
    
    # 表示設定
    'INFO_MARGIN': 4,        # 情報表示領域までの余白
    'BLOCK_CHAR': '██',      # ブロックの表示文字
    'EMPTY_CHAR': '. ',      # 空きスペースの表示文字
    
    # ゲーム速度
    'FALL_SPEED': 0.5,      # 落下速度（秒）
    'FRAME_RATE': 0.05,     # 画面更新間隔（秒）
    
    # スコア設定
    'SCORES': [0, 100, 300, 500, 800],  # 0,1,2,3,4ライン消しのスコア

    # ゲーム制御
    'KEY_QUIT': ord('q'),    # 終了キー
    'KEY_DROP': ord(' '),    # ハードドロップキー
    
    # 色設定
    'COLOR_PAIRS': [
        (curses.COLOR_CYAN, curses.COLOR_BLACK),     # I piece
        (curses.COLOR_YELLOW, curses.COLOR_BLACK),   # O piece
        (curses.COLOR_MAGENTA, curses.COLOR_BLACK),  # T piece
        (curses.COLOR_BLUE, curses.COLOR_BLACK),     # L piece
        (curses.COLOR_WHITE, curses.COLOR_BLACK),    # J piece
        (curses.COLOR_GREEN, curses.COLOR_BLACK),    # S piece
        (curses.COLOR_RED, curses.COLOR_BLACK),      # Z piece
    ]
}

# テトリミノの定義（既存のまま）
TETRIMINOS = [
    {'shape': [[1, 1, 1, 1]], 'color': 1},      # I: シアン
    {'shape': [[1, 1], [1, 1]], 'color': 2},    # O: 黄色
    {'shape': [[1, 1, 1], [0, 1, 0]], 'color': 3},  # T: マゼンタ
    {'shape': [[1, 1, 1], [1, 0, 0]], 'color': 4},  # L: 青
    {'shape': [[1, 1, 1], [0, 0, 1]], 'color': 5},  # J: オレンジ
    {'shape': [[1, 1, 0], [0, 1, 1]], 'color': 6},  # S: 緑
    {'shape': [[0, 1, 1], [1, 1, 0]], 'color': 7},  # Z: 赤
]

class Tetris:
    def __init__(self, height=GAME_CONST['BOARD_HEIGHT'], width=GAME_CONST['BOARD_WIDTH']):
        self.height = height
        self.width = width
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.board_colors = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.game_over = False
        self.score = 0
        
    def new_piece(self):
        # ランダムにテトリミノを選択
        piece = random.choice(TETRIMINOS)
        shape = piece['shape']
        
        # 新しいピースを作成
        self.current_piece = {
            'shape': shape[:],  # シェイプをコピー
            'color': piece['color'],
            'x': self.width // 2 - len(shape[0]) // 2,  # 中央に配置
            'y': 0
        }

    def valid_move(self, piece, x, y):
        for i in range(len(piece)):
            for j in range(len(piece[0])):
                if piece[i][j]:
                    if (y + i >= self.height or 
                        x + j < 0 or 
                        x + j >= self.width or 
                        self.board[y + i][x + j]):
                        return False
        return True

    def rotate_piece(self):
        if not self.current_piece:
            return
        shape = self.current_piece['shape']
        rotated = [[shape[y][x] for y in range(len(shape)-1, -1, -1)]
                  for x in range(len(shape[0]))]
        
        if self.valid_move(rotated, self.current_piece['x'], self.current_piece['y']):
            self.current_piece['shape'] = rotated

    def move_piece(self, dx):
        if not self.current_piece:
            return
        if self.valid_move(self.current_piece['shape'],
                          self.current_piece['x'] + dx,
                          self.current_piece['y']):
            self.current_piece['x'] += dx

    def drop_piece(self):
        if not self.current_piece:
            return
        while self.valid_move(self.current_piece['shape'],
                            self.current_piece['x'],
                            self.current_piece['y'] + 1):
            self.current_piece['y'] += 1

    def freeze_piece(self):
        if not self.current_piece:
            return
        
        piece = self.current_piece['shape']
        color = self.current_piece['color']
        for y in range(len(piece)):
            for x in range(len(piece[0])):
                if piece[y][x]:
                    self.board[self.current_piece['y'] + y][self.current_piece['x'] + x] = 1
                    self.board_colors[self.current_piece['y'] + y][self.current_piece['x'] + x] = color

    def clear_lines(self):
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(self.board[y]):
                lines_cleared += 1
                for ny in range(y, 0, -1):
                    self.board[ny] = self.board[ny-1][:]
                    self.board_colors[ny] = self.board_colors[ny-1][:]
                self.board[0] = [0] * self.width
                self.board_colors[0] = [0] * self.width
            else:
                y -= 1
        
        self.score += GAME_CONST['SCORES'][lines_cleared] if lines_cleared < len(GAME_CONST['SCORES']) else GAME_CONST['SCORES'][-1]

    def update(self):
        if not self.current_piece:
            self.new_piece()
            if not self.valid_move(self.current_piece['shape'], 
                                 self.current_piece['x'], 
                                 self.current_piece['y']):
                self.game_over = True
                return

        if self.valid_move(self.current_piece['shape'],
                          self.current_piece['x'],
                          self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
        else:
            self.freeze_piece()
            self.clear_lines()
            # 一番上の行にブロックがある場合はゲームオーバー
            if any(self.board[0]):
                self.game_over = True
                return
            self.new_piece()

def main(stdscr):
    # 画面初期化
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(1)
    
    # 色ペアの初期化
    for i, (fg, bg) in enumerate(GAME_CONST['COLOR_PAIRS'], 1):
        curses.init_pair(i, fg, bg)
    
    # ウィンドウサイズのチェック
    height, width = stdscr.getmaxyx()
    if height < GAME_CONST['MIN_TERM_HEIGHT'] or width < GAME_CONST['MIN_TERM_WIDTH']:
        raise Exception(f"Terminal window too small! Minimum size: {GAME_CONST['MIN_TERM_HEIGHT']}x{GAME_CONST['MIN_TERM_WIDTH']}")
    
    game = Tetris()
    info_x = game.width * 2 + GAME_CONST['INFO_MARGIN']
    
    # ゲームループの制御変数
    fall_speed = GAME_CONST['FALL_SPEED']
    frame_rate = GAME_CONST['FRAME_RATE']
    last_fall_time = time.time()
    last_frame_time = time.time()
    
    while True:
        try:
            current_time = time.time()
            delta_time = current_time - last_fall_time
            frame_delta = current_time - last_frame_time

            if frame_delta < frame_rate:
                time.sleep(frame_rate - frame_delta)
                continue

            last_frame_time = current_time
            
            key = stdscr.getch()
            if key == ord('q'):
                break

            if not game.game_over:
                if key == curses.KEY_LEFT:
                    game.move_piece(-1)
                elif key == curses.KEY_RIGHT:
                    game.move_piece(1)
                elif key == curses.KEY_UP:
                    game.rotate_piece()
                elif key == curses.KEY_DOWN:
                    game.update()
                    last_fall_time = current_time
                elif key == ord(' '):
                    game.drop_piece()
                    game.update()
                    last_fall_time = current_time

                if delta_time > fall_speed:
                    game.update()
                    last_fall_time = current_time

            stdscr.clear()

            # ボードの描画
            for y in range(game.height):
                for x in range(game.width):
                    if game.board[y][x]:
                        color = curses.color_pair(game.board_colors[y][x])
                        stdscr.addstr(y, x*2, GAME_CONST['BLOCK_CHAR'], color)
                    else:
                        stdscr.addstr(y, x*2, GAME_CONST['EMPTY_CHAR'])
            
            # 現在のピースの描画（ゲームオーバーでない場合のみ）
            if game.current_piece and not game.game_over:
                piece = game.current_piece['shape']
                color = curses.color_pair(game.current_piece['color'])
                for y in range(len(piece)):
                    for x in range(len(piece[0])):
                        if piece[y][x]:
                            stdscr.addstr(game.current_piece['y'] + y, 
                                        (game.current_piece['x'] + x) * 2, 
                                        GAME_CONST['BLOCK_CHAR'], color)
            
            # 情報表示
            info_x = game.width * 2 + GAME_CONST['INFO_MARGIN']
            stdscr.addstr(0, info_x, f"Score: {game.score}")
            
            if game.game_over:
                game_over_msg = "GAME OVER!"
                score_msg = f"Final Score: {game.score}"
                quit_msg = "Press 'Q' to quit"
                
                # 画面中央にメッセージを表示
                center_y = game.height // 2
                center_x = game.width
                
                stdscr.addstr(center_y - 1, center_x * 2 - len(game_over_msg) // 2, 
                             game_over_msg, curses.A_BOLD)
                stdscr.addstr(center_y + 1, center_x * 2 - len(score_msg) // 2, 
                             score_msg)
                stdscr.addstr(center_y + 3, center_x * 2 - len(quit_msg) // 2, 
                             quit_msg)
            else:
                stdscr.addstr(2, info_x, "Controls:")
                stdscr.addstr(3, info_x, "←→: Move")
                stdscr.addstr(4, info_x, "↑: Rotate")
                stdscr.addstr(5, info_x, "↓: Soft drop")
                stdscr.addstr(6, info_x, "Space: Hard drop")
                stdscr.addstr(7, info_x, "Q: Quit")
            
            stdscr.refresh()
                
        except curses.error:
            continue
      
if __name__ == '__main__':
    curses.wrapper(main) 