import importlib
import math
import os
import sys

import pygame


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINAL_SYS_PATH = sys.path[:]
FILTERED_SYS_PATH = [
    path for path in sys.path
    if os.path.abspath(path or os.getcwd()) != SCRIPT_DIR
]

try:
    sys.path = FILTERED_SYS_PATH
    chess = importlib.import_module("chess")
finally:
    sys.path = ORIGINAL_SYS_PATH


LIGHT_SQUARE = "#EBECD0"
DARK_SQUARE = "#779556"
BACKGROUND = "#1E1F22"
SIDEBAR_BG = "#26282D"
SIDEBAR_PANEL = "#2F3238"
TEXT_COLOR = "#F4F4F4"
MUTED_TEXT = "#C9CDD3"
SELECTED_COLOR = "#F4D35E"
CHECK_GLOW = (235, 97, 80, 185)
MOVE_DOT = (35, 35, 35, 80)

WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 720
DEFAULT_SIZE = (1100, 760)
PADDING = 24
SIDEBAR_MIN_WIDTH = 280

ELO_RANGES = [
    "100 - 400",
    "400 - 600",
    "600 - 900",
    "900 - 1200",
    "1200 - 1500",
]

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 330,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

DISPLAY_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

UNICODE_PIECES = {
    chess.Piece(chess.KING, chess.WHITE): "♔",
    chess.Piece(chess.QUEEN, chess.WHITE): "♕",
    chess.Piece(chess.ROOK, chess.WHITE): "♖",
    chess.Piece(chess.BISHOP, chess.WHITE): "♗",
    chess.Piece(chess.KNIGHT, chess.WHITE): "♘",
    chess.Piece(chess.PAWN, chess.WHITE): "♙",
    chess.Piece(chess.KING, chess.BLACK): "♚",
    chess.Piece(chess.QUEEN, chess.BLACK): "♛",
    chess.Piece(chess.ROOK, chess.BLACK): "♜",
    chess.Piece(chess.BISHOP, chess.BLACK): "♝",
    chess.Piece(chess.KNIGHT, chess.BLACK): "♞",
    chess.Piece(chess.PAWN, chess.BLACK): "♟",
}

PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0,
]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,
]

KING_TABLE = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,
]

PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


class ChessAI:
    def __init__(self, color=chess.BLACK, depth=2):
        self.color = color
        self.depth = depth

    def choose_move(self, board):
        import random
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Shuffle to resolve ties randomly
        random.shuffle(legal_moves)
        ordered = self.order_moves(board, legal_moves)
        best_move = ordered[0]

        alpha = -math.inf
        beta = math.inf

        if self.color == chess.WHITE:
            best_score = -math.inf
            for move in ordered:
                board.push(move)
                score = self.minimax(board, self.depth - 1, alpha, beta)
                board.pop()
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, best_score)
        else:
            best_score = math.inf
            for move in ordered:
                board.push(move)
                score = self.minimax(board, self.depth - 1, alpha, beta)
                board.pop()
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, best_score)

        return best_move

    def minimax(self, board, depth, alpha, beta):
        if self.is_terminal(board):
            return self.evaluate(board)
            
        if depth == 0:
            return self.quiescence(board, alpha, beta)

        moves = self.order_moves(board, board.legal_moves)
        if board.turn == chess.WHITE:
            value = -math.inf
            for move in moves:
                board.push(move)
                value = max(value, self.minimax(board, depth - 1, alpha, beta))
                board.pop()
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value

        value = math.inf
        for move in moves:
            board.push(move)
            value = min(value, self.minimax(board, depth - 1, alpha, beta))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value
        
    def quiescence(self, board, alpha, beta):
        if self.is_terminal(board):
            return self.evaluate(board)
            
        stand_pat = self.evaluate(board)
        
        if board.turn == chess.WHITE:
            if stand_pat >= beta:
                return beta
            if alpha < stand_pat:
                alpha = stand_pat
                
            captures = list(board.generate_legal_captures())
            moves = self.order_moves(board, captures)
            for move in moves:
                board.push(move)
                score = self.quiescence(board, alpha, beta)
                board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            if beta > stand_pat:
                beta = stand_pat
                
            captures = list(board.generate_legal_captures())
            moves = self.order_moves(board, captures)
            for move in moves:
                board.push(move)
                score = self.quiescence(board, alpha, beta)
                board.pop()
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
            return beta

    def is_terminal(self, board):
        return (
            board.is_checkmate()
            or board.is_stalemate()
            or board.is_repetition(3)
            or board.is_insufficient_material()
            or board.can_claim_fifty_moves()
        )

    def evaluate(self, board):
        if board.is_checkmate():
            return -100000 if board.turn == chess.WHITE else 100000
        if board.is_stalemate() or board.is_repetition(3) or board.is_insufficient_material() or board.can_claim_fifty_moves():
            return 0

        score = 0
        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            table = PIECE_SQUARE_TABLES[piece.piece_type]
            table_value = table[square] if piece.color == chess.WHITE else table[chess.square_mirror(square)]
            if piece.color == chess.WHITE:
                score += value + table_value
            else:
                score -= value + table_value

        # Small penalty for repetitions to prevent looping
        if board.is_repetition(2):
            score += 50 if board.turn == chess.WHITE else -50

        if board.is_check():
            score += 20 if board.turn == chess.BLACK else -20

        return score

    def order_moves(self, board, moves):
        def move_score(move):
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if attacker is not None:
                    score += 10 * DISPLAY_VALUES.get(victim.piece_type, 0) if victim else 0
                    score -= DISPLAY_VALUES.get(attacker.piece_type, 0)
            if move.promotion:
                score += DISPLAY_VALUES.get(move.promotion, 0) + 9
            if board.gives_check(move):
                score += 2
            if board.is_castling(move):
                score += 3
            return score

        return sorted(list(moves), key=move_score, reverse=True)


TIMING_MODES = [
    {"name": "10 + 10", "player": 10, "ai": 10},
    {"name": "10 + 5", "player": 10, "ai": 5},
    {"name": "3 + 3", "player": 3, "ai": 3},
    {"name": "3 + 1", "player": 3, "ai": 1},
    {"name": "1 + 1", "player": 1, "ai": 1},
]


class ChessApp:
    def _load_piece_images(self):
        neo_dir = os.path.join(SCRIPT_DIR, "assets", "neo")
        if not os.path.exists(neo_dir):
            return
           
        color_map = {chess.WHITE: 'w', chess.BLACK: 'b'}
        piece_map = {
            chess.PAWN: 'p', chess.KNIGHT: 'n', chess.BISHOP: 'b',
            chess.ROOK: 'r', chess.QUEEN: 'q', chess.KING: 'k'
        }
       
        for color, c_prefix in color_map.items():
            for p_type, p_prefix in piece_map.items():
                filename = f"{c_prefix}{p_prefix}.png"
                path = os.path.join(neo_dir, filename)
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.piece_images[chess.Piece(p_type, color)] = img
                    except pygame.error:
                        pass

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Player vs AI")
        self.screen = pygame.display.set_mode(DEFAULT_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.board = chess.Board()
        self.piece_images = {}
        self._load_piece_images()
        self.player_color = chess.WHITE
        self.elo_index = 2
        self.ai = ChessAI(color=chess.BLACK, depth=self.elo_index + 1)
        self.color_selected = False
        self.selected_square = None
        self.view_offset = 0
        self.pending_promotion = None
        self.promotion_rects = []
        self.legal_targets = []
        self.san_moves = []
        self.difficulty_rects = []
        self.timing_rects = []
        self.color_rects = []
        self.timing_index = 0
        self.result_message = ""
        self.game_over = False
        self.show_result_popup = True
       
        mode = TIMING_MODES[self.timing_index]
        self.times = {
            self.player_color: mode["player"] * 60.0,
            self.ai.color: mode["ai"] * 60.0
        }
        self.last_tick_time = pygame.time.get_ticks()
        self.animation = None
        self.layout = {}
        self.font_name = self.find_font_name()
        self.build_fonts(DEFAULT_SIZE)
        self.update_layout(DEFAULT_SIZE)

    def find_font_name(self):
        candidates = [
            "segoeuisymbol",
            "segoeui",
            "dejavusans",
            "arialunicode",
            "arial",
        ]
        for name in candidates:
            path = pygame.font.match_font(name)
            if path:
                return path
        return None

    def build_fonts(self, size):
        width, height = size
        sidebar_width = max(SIDEBAR_MIN_WIDTH, int(width * 0.28))
        board_space = min(width - sidebar_width - (PADDING * 3), height - (PADDING * 2))
        square_size = max(44, board_space // 8)
        piece_size = int(square_size * 0.82)

        self.title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.section_font = pygame.font.SysFont("arial", 20, bold=True)
        self.body_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 14)
        self.piece_font = pygame.font.Font(self.font_name, piece_size)
        self.ui_piece_font = pygame.font.Font(self.font_name, 32)

    def update_layout(self, size):
        width = max(size[0], WINDOW_MIN_WIDTH)
        height = max(size[1], WINDOW_MIN_HEIGHT)
        if self.screen.get_size() != (width, height):
            self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        sidebar_width = max(SIDEBAR_MIN_WIDTH, int(width * 0.28))
        available_board_width = width - sidebar_width - (PADDING * 3)
        available_board_height = height - (PADDING * 2)
        square_size = max(44, min(available_board_width // 8, available_board_height // 8))
        board_size = square_size * 8
        board_x = PADDING + max(0, (available_board_width - board_size) // 2)
        board_y = PADDING + max(0, (available_board_height - board_size) // 2)

        self.layout = {
            "window": (width, height),
            "board_rect": pygame.Rect(board_x, board_y, board_size, board_size),
            "sidebar_rect": pygame.Rect(board_x + board_size + PADDING, PADDING, sidebar_width, height - (PADDING * 2)),
            "square_size": square_size,
        }
        self.build_fonts((width, height))

    def run(self):
        running = True
        self.last_tick_time = pygame.time.get_ticks()
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_tick_time) / 1000.0
            self.last_tick_time = current_time

            if self.color_selected and not self.game_over and self.animation is None and self.view_offset == 0:
                if len(self.board.move_stack) > 0:
                    active_color = self.board.turn
                    self.times[active_color] -= dt
                    if self.times[active_color] <= 0:
                        self.times[active_color] = 0
                        winner = "Computer" if active_color == self.player_color else "Player"
                        self.result_message = f"Time out! {winner} wins."
                        self.game_over = True
                        self.show_result_popup = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.update_layout(event.size)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.result_message and self.show_result_popup:
                        if event.button == 3:
                            self.show_result_popup = False
                    elif self.animation is None:
                        if event.button == 1:
                            if not self.color_selected:
                                self.handle_color_selection_click(event.pos)
                            elif self.pending_promotion is not None:
                                self.handle_promotion_click(event.pos)
                            elif self.handle_sidebar_click(event.pos):
                                pass
                            else:
                                self.handle_left_click(event.pos)
                        elif event.button == 3:
                            if self.pending_promotion is None:
                                self.clear_selection()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.navigate_history(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.navigate_history(1)

            if self.animation is not None:
                if current_time - self.animation['start_time'] >= self.animation['duration']:
                    move = self.animation['move']
                    san = self.animation['san']
                    self.board.push(move)
                    self.san_moves.append(san)
                    self.update_result_message()
                    self.animation = None

            if running and self.color_selected and not self.game_over and self.board.turn == self.ai.color and self.animation is None and self.pending_promotion is None and self.view_offset == 0:
                if not hasattr(self, 'ai_timer_start') or self.ai_timer_start is None:
                    import random
                    self.ai_timer_start = current_time
                    self.ai_target_delay = random.uniform(600, 2000)

                if current_time - self.ai_timer_start >= self.ai_target_delay:
                    self.draw()
                    pygame.display.flip()
                    pygame.event.pump()
                    self.make_ai_move()
                    self.ai_timer_start = None

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_left_click(self, position):
        if self.game_over:
            return

        if self.view_offset < 0:
            self.view_offset = 0
            self.clear_selection()
            return

        if self.board.turn != self.player_color:
            return

        board_rect = self.layout["board_rect"]
        if not board_rect.collidepoint(position):
            self.clear_selection()
            return

        square = self.pixel_to_square(position)
        if square is None:
            return

        if self.selected_square is not None and square in self.legal_targets:
            self.make_player_move(square)
            return

        piece = self.board.piece_at(square)
        if piece and piece.color == self.player_color:
            self.selected_square = square
            self.legal_targets = sorted({move.to_square for move in self.board.legal_moves if move.from_square == square})
        else:
            self.clear_selection()

    def clear_selection(self):
        self.selected_square = None
        self.legal_targets = []

    def make_player_move(self, target_square):
        if self.selected_square is None:
            return

        piece = self.board.piece_at(self.selected_square)
        if piece and piece.piece_type == chess.PAWN:
            rank = chess.square_rank(target_square)
            if rank in (0, 7):
                self.pending_promotion = (self.selected_square, target_square)
                self.build_promotion_menu(target_square)
                return

        move = chess.Move(self.selected_square, target_square)
        if move in self.board.legal_moves:
            self.push_move(move)
        self.clear_selection()

    def build_promotion_menu(self, square):
        self.promotion_rects = []
        square_rect = self.square_to_rect(square)
        options = [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]
       
        rank = chess.square_rank(square)
        direction = 1 if rank == 7 else -1
       
        for i, piece_type in enumerate(options):
            rect = pygame.Rect(
                square_rect.x,
                square_rect.y + (i * square_rect.height * direction),
                square_rect.width,
               square_rect.height
            )
            self.promotion_rects.append((rect, piece_type))

    def handle_promotion_click(self, position):
        for rect, piece_type in self.promotion_rects:
            if rect.collidepoint(position):
                from_square, to_square = self.pending_promotion
                move = chess.Move(from_square, to_square, promotion=piece_type)
                if move in self.board.legal_moves:
                    self.pending_promotion = None
                    self.promotion_rects = []
                    self.push_move(move)
                    self.clear_selection()
                return
       
        self.pending_promotion = None
        self.promotion_rects = []
        self.clear_selection()

    def handle_sidebar_click(self, position):
        return False

    def handle_color_selection_click(self, position):
        for i, rect in enumerate(getattr(self, 'timing_rects', [])):
            if rect.collidepoint(position):
                self.timing_index = i
                return True
               
        for i, rect in enumerate(getattr(self, 'difficulty_rects', [])):
            if rect.collidepoint(position):
                self.elo_index = i
                self.ai.depth = self.elo_index + 1
                return True
               
        for rect, val in getattr(self, 'color_rects', []):
            if rect.collidepoint(position):
                if val is None:
                    import random
                    self.player_color = random.choice([chess.WHITE, chess.BLACK])
                else:
                    self.player_color = val
               
                self.ai.color = chess.BLACK if self.player_color == chess.WHITE else chess.WHITE
                self.color_selected = True
               
                mode = TIMING_MODES[self.timing_index]
                self.times[self.player_color] = mode["player"] * 60.0
                self.times[self.ai.color] = mode["ai"] * 60.0
                self.last_tick_time = pygame.time.get_ticks()
                return True
        return False

    def make_ai_move(self):
        start_time = pygame.time.get_ticks()
        move = self.ai.choose_move(self.board)
        calc_time = (pygame.time.get_ticks() - start_time) / 1000.0
       
        ai_color = self.board.turn
        self.times[ai_color] -= calc_time
        if self.times[ai_color] <= 0:
            self.times[ai_color] = 0
            self.result_message = "Time out! Player wins."
            self.game_over = True
            self.show_result_popup = True
           
        if move is not None and self.times[ai_color] > 0:
            self.push_move(move)
           
        self.last_tick_time = pygame.time.get_ticks()

    def push_move(self, move):
        self.view_offset = 0
        piece_moving = self.board.piece_at(move.from_square)
        if piece_moving is None:
            san = self.board.san(move)
            self.board.push(move)
            self.san_moves.append(san)
            self.update_result_message()
            self.clear_selection()
            return

        is_castling = self.board.is_castling(move)
        san = self.board.san(move)

        anim_pieces = []
        anim_pieces.append({
            'piece': piece_moving,
            'start_square': move.from_square,
            'end_square': move.to_square,
        })

        if is_castling:
            if move.to_square == chess.G1:
                anim_pieces.append({'piece': chess.Piece(chess.ROOK, chess.WHITE), 'start_square': chess.H1, 'end_square': chess.F1})
            elif move.to_square == chess.C1:
                anim_pieces.append({'piece': chess.Piece(chess.ROOK, chess.WHITE), 'start_square': chess.A1, 'end_square': chess.D1})
            elif move.to_square == chess.G8:
                anim_pieces.append({'piece': chess.Piece(chess.ROOK, chess.BLACK), 'start_square': chess.H8, 'end_square': chess.F8})
            elif move.to_square == chess.C8:
                anim_pieces.append({'piece': chess.Piece(chess.ROOK, chess.BLACK), 'start_square': chess.A8, 'end_square': chess.D8})

        self.animation = {
            'pieces': anim_pieces,
            'start_time': pygame.time.get_ticks(),
            'duration': 150,
            'move': move,
            'san': san
        }
        self.clear_selection()

    def navigate_history(self, delta):
        if self.animation is not None:
            return
       
        max_back = -len(self.board.move_stack)
        self.view_offset = clamp(self.view_offset + delta, max_back, 0)
        self.clear_selection()

    def get_display_board(self):
        if self.view_offset == 0:
            return self.board
       
        display_board = self.board.copy()
        for _ in range(abs(self.view_offset)):
            display_board.pop()
        return display_board

    def update_result_message(self):
        if self.board.is_checkmate():
            winner = "Player" if self.board.turn != self.player_color else "Computer"
            self.result_message = f"Checkmate! {winner} wins."
            self.game_over = True
            self.show_result_popup = True
        elif self.board.is_stalemate():
            self.result_message = "Draw by stalemate."
            self.game_over = True
            self.show_result_popup = True
        elif self.board.is_repetition(3):
            self.result_message = "Draw by threefold repetition."
            self.game_over = True
            self.show_result_popup = True
        elif self.board.is_insufficient_material():
            self.result_message = "Draw by insufficient material."
            self.game_over = True
            self.show_result_popup = True
        elif self.board.can_claim_fifty_moves():
            self.result_message = "Draw by fifty-move rule."
            self.game_over = True
            self.show_result_popup = True
        else:
            self.result_message = ""

    def pixel_to_square(self, position):
        board_rect = self.layout["board_rect"]
        square_size = self.layout["square_size"]
        x, y = position
        v_file = (x - board_rect.x) // square_size
        v_rank = (y - board_rect.y) // square_size
        if not (0 <= v_file < 8 and 0 <= v_rank < 8):
            return None
           
        if self.player_color == chess.BLACK:
            file_index = 7 - v_file
            rank = v_rank
        else:
            file_index = v_file
            rank = 7 - v_rank
           
        return chess.square(file_index, rank)

    def square_to_rect(self, square):
        board_rect = self.layout["board_rect"]
        square_size = self.layout["square_size"]
        file_index = chess.square_file(square)
        rank = chess.square_rank(square)
       
        if self.player_color == chess.BLACK:
            v_file = 7 - file_index
            v_rank = rank
        else:
            v_file = file_index
            v_rank = 7 - rank
           
        return pygame.Rect(
            board_rect.x + (v_file * square_size),
            board_rect.y + (v_rank * square_size),
            square_size,
            square_size,
        )

    def get_material_balance_text(self, display_board):
        player_score = 0
        ai_score = 0
        for piece in display_board.piece_map().values():
            if getattr(self, 'player_color', chess.WHITE) == piece.color:
                player_score += DISPLAY_VALUES[piece.piece_type]
            else:
                ai_score += DISPLAY_VALUES[piece.piece_type]

        diff = player_score - ai_score
        if diff > 0:
            return f"+{diff}"
        if diff < 0:
            return f"-{abs(diff)}"
        return "Equal Material"

    def get_status_text(self, display_board):
        if self.view_offset < 0:
            return f"Viewing history ({-self.view_offset} moves back)"
        if self.result_message:
            return self.result_message
        if display_board.turn == self.ai.color:
            return "Computer thinking..."
        if display_board.is_check():
            return "Your king is in check."
        return "Your move."

    def build_move_log_lines(self):
        lines = []
        for index in range(0, len(self.san_moves), 2):
            number = (index // 2) + 1
            white_move = self.san_moves[index]
            black_move = self.san_moves[index + 1] if index + 1 < len(self.san_moves) else ""
            lines.append(f"{number}. {white_move} {black_move}".strip())
        return lines

    def draw(self):
        self.screen.fill(BACKGROUND)
        display_board = self.get_display_board()
        self.draw_board(display_board)
        self.draw_sidebar(display_board)
        if self.pending_promotion is not None:
            self.draw_promotion_overlay()
        if self.result_message and getattr(self, 'show_result_popup', True) and self.view_offset == 0:
            self.draw_result_banner()
           
        if not self.color_selected:
            self.draw_color_selection()

    def draw_color_selection(self):
        width, height = self.layout["window"]
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        panel_w = 460
        panel_h = 460
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (width // 2, height // 2)
       
        pygame.draw.rect(self.screen, "#26282D", panel, border_radius=16)
        pygame.draw.rect(self.screen, SELECTED_COLOR, panel, width=3, border_radius=16)
       
        time_title = self.title_font.render("Select Time Control", True, TEXT_COLOR)
        self.screen.blit(time_title, time_title.get_rect(center=(panel.centerx, panel.top + 40)))
       
        self.timing_rects = []
        tw = 64
        gap = 12
        start_x = panel.centerx - (2.5 * tw + 2 * gap)
        y = panel.top + 80
        mouse_pos = pygame.mouse.get_pos()
       
        for i, mode in enumerate(TIMING_MODES):
            rect = pygame.Rect(start_x + i * (tw + gap), y, tw, 40)
            self.timing_rects.append(rect)
           
            is_selected = (i == self.timing_index)
            bg_color = SELECTED_COLOR if is_selected else "#2F3238"
            border_color = SELECTED_COLOR if is_selected else "#4A4D54"
            t_color = BACKGROUND if is_selected else MUTED_TEXT
           
            if not is_selected and rect.collidepoint(mouse_pos):
                bg_color = "#3A3D44"
               
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)
           
            text_surf = self.small_font.render(mode["name"], True, t_color)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        diff_title = self.title_font.render("Select AI Difficulty", True, TEXT_COLOR)
        self.screen.blit(diff_title, diff_title.get_rect(center=(panel.centerx, panel.top + 160)))
       
        self.difficulty_rects = []
        piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
        piece_names = ["Pawn", "Knight", "Bishop", "Rook", "Queen"]
       
        tw = 52
        gap = 12
        start_x = panel.centerx - (2.5 * tw + 2 * gap)
        y = panel.top + 200
       
        for i, p_type in enumerate(piece_types):
            rect = pygame.Rect(start_x + i * (tw + gap), y, tw, tw)
            self.difficulty_rects.append(rect)
           
            is_selected = (i == self.elo_index)
            bg_color = SELECTED_COLOR if is_selected else "#2F3238"
            border_color = SELECTED_COLOR if is_selected else "#4A4D54"
            piece_color = BACKGROUND if is_selected else MUTED_TEXT
           
            if not is_selected and rect.collidepoint(mouse_pos):
                bg_color = "#3A3D44"
               
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)
           
            piece_obj = chess.Piece(p_type, chess.WHITE)
            if hasattr(self, 'piece_images') and piece_obj in self.piece_images:
                img_size = int(tw * 0.75)
                self.draw_piece_at_pos(piece_obj, rect.centerx - img_size/2, rect.centery - img_size/2, img_size, img_size)
            else:
                glyph = UNICODE_PIECES[piece_obj]
                piece_surface = self.ui_piece_font.render(glyph, True, piece_color)
                piece_rect = piece_surface.get_rect(center=(rect.centerx, rect.centery - 2))
                self.screen.blit(piece_surface, piece_rect)

            elo_text = self.small_font.render(str(ELO_RANGES[i]), True, MUTED_TEXT)
            self.screen.blit(elo_text, elo_text.get_rect(center=(rect.centerx, rect.bottom + 14)))
           
        color_title = self.title_font.render("Choose Your Color", True, TEXT_COLOR)
        self.screen.blit(color_title, color_title.get_rect(center=(panel.centerx, panel.top + 310)))
       
        self.color_rects = []
        button_w = 100
        button_h = 80
        gap = 20
        start_x = panel.centerx - (1.5 * button_w + gap)
       
        colors = [
            ("White", "#F8F5F2", "#C98D5B", chess.WHITE),
            ("Random", "#888888", "#555555", None),
            ("Black", "#5A6270", "#303641", chess.BLACK)
        ]
       
        for i, (name, bg, outline, val) in enumerate(colors):
            rect = pygame.Rect(start_x + i * (button_w + gap), panel.top + 350, button_w, button_h)
            self.color_rects.append((rect, val))
           
            is_hover = rect.collidepoint(pygame.mouse.get_pos())
            color = SELECTED_COLOR if is_hover else "#2F3238"
           
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, "#4A4D54", rect, width=2, border_radius=12)
           
            if val == chess.WHITE:
                piece_obj = chess.Piece(chess.KING, chess.WHITE)
            elif val == chess.BLACK:
                piece_obj = chess.Piece(chess.KING, chess.BLACK)
            else:
                piece_obj = None
               
            if piece_obj:
                if hasattr(self, 'piece_images') and piece_obj in self.piece_images:
                    img_size = 56
                    self.draw_piece_at_pos(piece_obj, rect.centerx - img_size/2, rect.centery - img_size/2 - 10, img_size, img_size)
                else:
                    glyph = UNICODE_PIECES[piece_obj]
                    piece_surface = self.ui_piece_font.render(glyph, True, bg)
                    self.screen.blit(piece_surface, piece_surface.get_rect(center=(rect.centerx, rect.centery - 10)))
                text_surf = self.small_font.render(name, True, TEXT_COLOR)
                self.screen.blit(text_surf, text_surf.get_rect(center=(rect.centerx, rect.bottom - 16)))
            else:
                text_surf = self.section_font.render("?", True, TEXT_COLOR)
                self.screen.blit(text_surf, text_surf.get_rect(center=(rect.centerx, rect.centery - 10)))
                text_surf2 = self.small_font.render("Random", True, TEXT_COLOR)
                self.screen.blit(text_surf2, text_surf2.get_rect(center=(rect.centerx, rect.bottom - 16)))

    def draw_promotion_overlay(self):
        if not self.promotion_rects:
            return

        board_rect = self.layout["board_rect"]
        dim = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        self.screen.blit(dim, board_rect.topleft)

        first_rect = self.promotion_rects[0][0]
        last_rect = self.promotion_rects[-1][0]
       
        menu_y = min(first_rect.y, last_rect.y)
        menu_h = abs(last_rect.bottom - first_rect.top) if last_rect.y > first_rect.y else abs(first_rect.bottom - last_rect.top)
        menu_rect = pygame.Rect(first_rect.x, menu_y, first_rect.width, menu_h)
       
        pygame.draw.rect(self.screen, "#F4F4F4", menu_rect, border_radius=8)
        pygame.draw.rect(self.screen, "#333333", menu_rect, width=2, border_radius=8)
       
        mouse_pos = pygame.mouse.get_pos()
        for rect, piece_type in self.promotion_rects:
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, "#DDDDDD", rect, border_radius=8)
            piece = chess.Piece(piece_type, self.player_color)
            self.draw_piece_at_pos(piece, rect.x, rect.y, rect.width, rect.height)

    def draw_board(self, display_board):
        board_rect = self.layout["board_rect"]
        square_size = self.layout["square_size"]
        files = "abcdefgh"

        pygame.draw.rect(self.screen, "#D7DBC8", board_rect.inflate(8, 8), border_radius=10)

        highlight_squares = []
        if self.animation is not None and self.view_offset == 0:
            highlight_squares = [self.animation['move'].from_square, self.animation['move'].to_square]
        elif len(display_board.move_stack) > 0:
            last_move = display_board.peek()
            highlight_squares = [last_move.from_square, last_move.to_square]

        for v_rank in range(8):
            for v_file in range(8):
                if self.player_color == chess.BLACK:
                    file_index = 7 - v_file
                    logical_rank = v_rank
                else:
                    file_index = v_file
                    logical_rank = 7 - v_rank
                   
                square = chess.square(file_index, logical_rank)
                rect = pygame.Rect(
                    board_rect.x + (v_file * square_size),
                    board_rect.y + (v_rank * square_size),
                    square_size,
                    square_size,
                )
                color = LIGHT_SQUARE if (v_file + v_rank) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, rect)

                if square in highlight_squares:
                    highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                    highlight.fill((244, 211, 94, 105))
                    self.screen.blit(highlight, rect.topleft)

                if self.selected_square == square:
                    highlight = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                    highlight.fill((244, 211, 94, 105))
                    self.screen.blit(highlight, rect.topleft)
                    pygame.draw.rect(self.screen, SELECTED_COLOR, rect, width=4)
                elif square in self.legal_targets:
                    dot_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                    center = (square_size // 2, square_size // 2)
                    radius = max(8, square_size // 8)
                    pygame.draw.circle(dot_surface, MOVE_DOT, center, radius)
                    self.screen.blit(dot_surface, rect.topleft)

                if v_file == 0:
                    rank_label = self.small_font.render(str(logical_rank + 1), True, "#5A6B3C" if color == LIGHT_SQUARE else "#EFF4D0")
                    self.screen.blit(rank_label, (rect.x + 6, rect.y + 4))
                if v_rank == 7:
                    file_label = self.small_font.render(files[file_index], True, "#5A6B3C" if color == LIGHT_SQUARE else "#EFF4D0")
                    self.screen.blit(file_label, (rect.right - 16, rect.bottom - 18))

        if display_board.is_check():
            king_square = display_board.king(display_board.turn)
            if king_square is not None:
                self.draw_check_glow(king_square)

        animating_start_squares = []
        if self.animation is not None and self.view_offset == 0:
            for anim in self.animation['pieces']:
                animating_start_squares.append(anim['start_square'])

        for square, piece in display_board.piece_map().items():
            if self.view_offset == 0 and square in animating_start_squares:
                continue
            self.draw_piece(square, piece)

        if self.animation is not None and self.view_offset == 0:
            current_time = pygame.time.get_ticks()
            progress = (current_time - self.animation['start_time']) / self.animation['duration']
            progress = clamp(progress, 0.0, 1.0)
            progress = 1 - (1 - progress) ** 2

            for anim in self.animation['pieces']:
                start_rect = self.square_to_rect(anim['start_square'])
                end_rect = self.square_to_rect(anim['end_square'])
               
                current_x = start_rect.x + (end_rect.x - start_rect.x) * progress
                current_y = start_rect.y + (end_rect.y - start_rect.y) * progress
               
                self.draw_piece_at_pos(anim['piece'], current_x, current_y, start_rect.width, start_rect.height)

    def draw_check_glow(self, square):
        rect = self.square_to_rect(square)
        glow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        glow.fill(CHECK_GLOW)
        pygame.draw.rect(glow, (138, 33, 24, 215), glow.get_rect(), width=3)
        self.screen.blit(glow, rect.topleft)

    def draw_piece_at_pos(self, piece, x, y, width, height, use_ui_font=False):
        if hasattr(self, 'piece_images') and piece in self.piece_images:
            if not hasattr(self, '_scaled_pieces'):
                self._scaled_pieces = {}
            key = (piece, int(width), int(height))
            if key not in self._scaled_pieces:
                self._scaled_pieces[key] = pygame.transform.smoothscale(
                    self.piece_images[piece], (int(width), int(height))
                )
            scaled_img = self._scaled_pieces[key]
            img_rect = scaled_img.get_rect(center=(x + width / 2, y + height / 2))
            self.screen.blit(scaled_img, img_rect)
            return

        glyph = UNICODE_PIECES[piece]
        main_color = "#F8F5F2" if piece.color == chess.WHITE else "#5A6270"
        outline_color = "#C98D5B" if piece.color == chess.WHITE else "#303641"
        center = (x + width / 2, y + height / 2)
       
        font = self.ui_piece_font if use_ui_font else self.piece_font

        for offset_x, offset_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            outline = font.render(glyph, True, outline_color)
            outline_rect = outline.get_rect(center=(center[0] + offset_x, center[1] + offset_y))
            self.screen.blit(outline, outline_rect)

        piece_surface = font.render(glyph, True, main_color)
        piece_rect = piece_surface.get_rect(center=(center[0], center[1] - 1))
        self.screen.blit(piece_surface, piece_rect)

    def draw_piece(self, square, piece):
        rect = self.square_to_rect(square)
        self.draw_piece_at_pos(piece, rect.x, rect.y, rect.width, rect.height)

    def draw_sidebar(self, display_board):
        rect = self.layout["sidebar_rect"]
        pygame.draw.rect(self.screen, SIDEBAR_BG, rect, border_radius=18)
        inner = rect.inflate(-20, -20)
        pygame.draw.rect(self.screen, SIDEBAR_PANEL, inner, border_radius=14)

        x = inner.x + 18
        y = inner.y + 18

        self.screen.blit(self.title_font.render("Player vs AI", True, TEXT_COLOR), (x, y))
        y += 44

        status = self.get_status_text(display_board)
        self.screen.blit(self.section_font.render("Status", True, TEXT_COLOR), (x, y))
        y += 28
        self.screen.blit(self.body_font.render(status, True, MUTED_TEXT), (x, y))
        y += 32

        # Draw Clocks
        def format_time(seconds):
            if seconds <= 0: return "0:00"
            mins = int(seconds) // 60
            secs = int(seconds) % 60
            if mins == 0 and seconds < 10:
                tenths = int((seconds * 10) % 10)
                return f"{secs}.{tenths}s"
            return f"{mins:02d}:{secs:02d}"

        game_active = self.color_selected and len(self.board.move_stack) > 0
        p_color = SELECTED_COLOR if self.board.turn == self.player_color and not self.result_message and self.view_offset == 0 and game_active else MUTED_TEXT
        a_color = SELECTED_COLOR if self.board.turn == self.ai.color and not self.result_message and self.view_offset == 0 and game_active else MUTED_TEXT
       
        p_rect = pygame.Rect(x, y, 100, 36)
        a_rect = pygame.Rect(x + 110, y, 100, 36)
       
        pygame.draw.rect(self.screen, "#3A3D44", p_rect, border_radius=6)
        pygame.draw.rect(self.screen, p_color, p_rect, width=2, border_radius=6)
        p_text = self.section_font.render(format_time(self.times[self.player_color]), True, p_color)
        self.screen.blit(p_text, p_text.get_rect(center=p_rect.center))
        pygame.draw.rect(self.screen, "#3A3D44", a_rect, border_radius=6)
        pygame.draw.rect(self.screen, a_color, a_rect, width=2, border_radius=6)
        a_text = self.section_font.render(format_time(self.times[self.ai.color]), True, a_color)
        self.screen.blit(a_text, a_text.get_rect(center=a_rect.center))
        y += 48
        self.screen.blit(self.section_font.render("AI Difficulty", True, TEXT_COLOR), (x, y))
        y += 28

        piece_names = ["Pawn", "Knight", "Bishop", "Rook", "Queen"]
        elo_text = f"Level {self.elo_index + 1}: {piece_names[self.elo_index]} ({ELO_RANGES[self.elo_index]})"
        self.screen.blit(self.body_font.render(elo_text, True, MUTED_TEXT), (x, y))
        y += 42
        self.screen.blit(self.section_font.render("Material", True, TEXT_COLOR), (x, y))
        y += 28
        material = self.get_material_balance_text(display_board)
        self.screen.blit(self.body_font.render(material, True, MUTED_TEXT), (x, y))
        y += 42
        self.screen.blit(self.section_font.render("Move Log (SAN)", True, TEXT_COLOR), (x, y))
        y += 30

        lines = self.build_move_log_lines()
        available_height = inner.bottom - y - 12
        line_height = 24
        max_lines = max(1, available_height // line_height)
        visible_lines = lines[-max_lines:]

        if not visible_lines:
            self.screen.blit(self.body_font.render("No moves yet.", True, MUTED_TEXT), (x, y))
        else:
            for line in visible_lines:
                self.screen.blit(self.body_font.render(line, True, MUTED_TEXT), (x, y))
                y += line_height

    def draw_result_banner(self):
        width, height = self.layout["window"]
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        banner = pygame.Rect(0, 0, 560, 140)
        banner.center = (width // 2, height // 2)
       
        shadow = banner.copy()
        shadow.y += 6
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow, border_radius=16)
       
        pygame.draw.rect(self.screen, "#26282D", banner, border_radius=16)
        pygame.draw.rect(self.screen, SELECTED_COLOR, banner, width=3, border_radius=16)

        game_over_surface = self.section_font.render("GAME OVER", True, SELECTED_COLOR)
        go_rect = game_over_surface.get_rect(center=(banner.centerx, banner.top + 32))
        self.screen.blit(game_over_surface, go_rect)

        message_surface = self.title_font.render(self.result_message, True, TEXT_COLOR)
        message_rect = message_surface.get_rect(center=(banner.centerx, banner.centery + 10))
        self.screen.blit(message_surface, message_rect)

        subtext = self.body_font.render("Right-click anywhere to close this message.", True, MUTED_TEXT)
        subtext_rect = subtext.get_rect(center=(banner.centerx, banner.bottom - 24))
        self.screen.blit(subtext, subtext_rect)


def main():
    ChessApp().run()


if __name__ == "__main__":
    main()