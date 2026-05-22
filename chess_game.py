"""
Chess Master — chess.com-inspired desktop chess.
v2 — Drag-and-drop, wooden sounds, redesigned UI, human-like AI timing.
"""

import importlib
import json
import math
import os
import random
import sys
import threading
from typing import Any, ClassVar, Literal, overload, cast

import pygame

# ──────────────────────────────────────────────────────────────────────────────
# PATH SETUP
# ──────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_orig = sys.path[:]
_filt = [p for p in sys.path if os.path.abspath(p or os.getcwd()) != SCRIPT_DIR]
try:
    sys.path = _filt
    chess = importlib.import_module("chess")
    chess_engine_mod = importlib.import_module("chess.engine")
finally:
    sys.path = _orig

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────
DATA_FILE      = os.path.join(SCRIPT_DIR, "player_data.json")
SF_PATH        = os.path.join(SCRIPT_DIR, "assets", "stockfish.exe")
NEO_DIR        = os.path.join(SCRIPT_DIR, "assets", "neo")

# ──────────────────────────────────────────────────────────────────────────────
# COLOURS  — chess.com dark palette
# ──────────────────────────────────────────────────────────────────────────────
C_BG        = "#161512"
C_SURFACE   = "#1E1C1A"
C_CARD      = "#262421"
C_CARD_HOV  = "#302D29"
C_BORDER    = "#3D3A35"
C_WHITE     = "#FFFFFF"
C_GRAY      = "#B2B0AC"
C_MUTED     = "#A5A39F"
C_GREEN     = "#81B64C"
C_GREEN_D   = "#4E7A2C"
C_RED       = "#E15554"
C_BLUE      = "#5B8DEF"
C_GOLD      = "#F6C64B"
C_CLK_LOW   = "#E15554"

# ──────────────────────────────────────────────────────────────────────────────
# BOARD THEMES
# ──────────────────────────────────────────────────────────────────────────────
THEMES = {
    "Green":  {"lt": "#EBECD0", "dk": "#779556", "hl": "#F4D35E"},
    "Blue":   {"lt": "#DEE3E6", "dk": "#8CA2AD", "hl": "#CDD26A"},
    "Brown":  {"lt": "#F0D9B5", "dk": "#B58863", "hl": "#CDD26A"},
    "Purple": {"lt": "#E2D6F3", "dk": "#7B5EA7", "hl": "#F4D35E"},
    "Dark":   {"lt": "#6F6F6F", "dk": "#3D3D3D", "hl": "#BCBCBC"},
}

# ──────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ──────────────────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1280, 820
MIN_W, MIN_H = 960, 660
NAV_H   = 52
STRIP_H = 56
EVAL_W  = 22
SB_W    = 308
PAD     = 16

# ──────────────────────────────────────────────────────────────────────────────
# PIECE DATA
# ──────────────────────────────────────────────────────────────────────────────
PVAL = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3,
        chess.ROOK:5, chess.QUEEN:9, chess.KING:0}
PVAL_CP = {chess.PAWN:100, chess.KNIGHT:330, chess.BISHOP:320,
           chess.ROOK:500, chess.QUEEN:900, chess.KING:0}
UGLYPH = {
    chess.Piece(chess.KING,   chess.WHITE):"♔", chess.Piece(chess.QUEEN, chess.WHITE):"♕",
    chess.Piece(chess.ROOK,   chess.WHITE):"♖", chess.Piece(chess.BISHOP,chess.WHITE):"♗",
    chess.Piece(chess.KNIGHT, chess.WHITE):"♘", chess.Piece(chess.PAWN,  chess.WHITE):"♙",
    chess.Piece(chess.KING,   chess.BLACK):"♚", chess.Piece(chess.QUEEN, chess.BLACK):"♛",
    chess.Piece(chess.ROOK,   chess.BLACK):"♜", chess.Piece(chess.BISHOP,chess.BLACK):"♝",
    chess.Piece(chess.KNIGHT, chess.BLACK):"♞", chess.Piece(chess.PAWN,  chess.BLACK):"♟",
}

# Piece-square tables (fallback AI)
_PST_PAWN   = [0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0]
_PST_KNIGHT = [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
_PST_BISHOP = [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
_PST_ROOK   = [0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
_PST_QUEEN  = [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
_PST_KING   = [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
PST = {chess.PAWN:_PST_PAWN, chess.KNIGHT:_PST_KNIGHT, chess.BISHOP:_PST_BISHOP,
       chess.ROOK:_PST_ROOK, chess.QUEEN:_PST_QUEEN, chess.KING:_PST_KING}

# ──────────────────────────────────────────────────────────────────────────────
# TIME CONTROLS
# ──────────────────────────────────────────────────────────────────────────────
TIME_MODES = [
    {"name":"1+0",   "cat":"Bullet",    "min":1,  "inc":0},
    {"name":"2+1",   "cat":"Bullet",    "min":2,  "inc":1},
    {"name":"3+0",   "cat":"Blitz",     "min":3,  "inc":0},
    {"name":"3+2",   "cat":"Blitz",     "min":3,  "inc":2},
    {"name":"5+0",   "cat":"Blitz",     "min":5,  "inc":0},
    {"name":"5+3",   "cat":"Blitz",     "min":5,  "inc":3},
    {"name":"10+0",  "cat":"Rapid",     "min":10, "inc":0},
    {"name":"15+10", "cat":"Rapid",     "min":15, "inc":10},
    {"name":"30+0",  "cat":"Rapid",     "min":30, "inc":0},
    {"name":"INF",   "cat":"Unlimited", "min":0,  "inc":0},
]
TIME_CATS = ["Bullet", "Blitz", "Rapid", "Unlimited"]

# ──────────────────────────────────────────────────────────────────────────────
# ADAPTIVE AI — parameters computed from player ELO at runtime
# ──────────────────────────────────────────────────────────────────────────────
def compute_ai_params(player_elo: int) -> dict:
    """Return AI engine parameters calibrated to be a small step above player_elo.

    The challenge offset shrinks as the player improves (matching chess.com behaviour).
    At every rating band the AI is slightly stronger, so there is always something
    to strive for — but it never feels impossibly hard.
    """
    # Challenge offset: decreases as player improves
    if   player_elo <  500: offset = 175
    elif player_elo <  800: offset = 150
    elif player_elo < 1100: offset = 125
    elif player_elo < 1400: offset = 100
    elif player_elo < 1700: offset = 75
    elif player_elo < 2000: offset = 50
    elif player_elo < 2400: offset = 30
    else:                   offset = 15

    ai_elo = clamp(player_elo + offset, 400, 3200)

    # Stockfish Skill Level 0-20
    skill = clamp(int((ai_elo - 400) / 115), 0, 20)

    # Think time scales with strength
    if   ai_elo <  700: think = 0.05
    elif ai_elo < 1000: think = 0.15
    elif ai_elo < 1400: think = 0.35
    elif ai_elo < 1800: think = 0.80
    elif ai_elo < 2200: think = 1.50
    elif ai_elo < 2600: think = 2.50
    else:               think = 4.00

    # Adaptive search depth constraint for both Stockfish and fallback minimax
    if   ai_elo <  700: depth = 1
    elif ai_elo < 1000: depth = 2
    elif ai_elo < 1300: depth = 3
    elif ai_elo < 1600: depth = 4
    elif ai_elo < 1900: depth = 5
    elif ai_elo < 2200: depth = 6
    elif ai_elo < 2600: depth = 8
    else:               depth = 12

    # Human-readable name
    if   ai_elo <  700: name = "Beginner"
    elif ai_elo < 1000: name = "Novice"
    elif ai_elo < 1400: name = "Intermediate"
    elif ai_elo < 1800: name = "Advanced"
    elif ai_elo < 2200: name = "Expert"
    elif ai_elo < 2600: name = "Master"
    else:               name = "Super-GM"

    return {"elo": ai_elo, "skill": skill, "think": think,
            "depth": depth, "name": name}

# ──────────────────────────────────────────────────────────────────────────────
# OPENING BOOK
# ──────────────────────────────────────────────────────────────────────────────
OPENINGS = {
    "e4":"King's Pawn", "d4":"Queen's Pawn", "c4":"English Opening",
    "Nf3":"Réti Opening", "e4 e5":"Open Game",
    "e4 e5 Nf3 Nc6 Bc4":"Italian Game", "e4 e5 Nf3 Nc6 Bb5":"Ruy López",
    "e4 e5 Nf3 Nc6 d4":"Scotch Game", "e4 e5 f4":"King's Gambit",
    "e4 c5":"Sicilian Defense", "e4 e6":"French Defense",
    "e4 c6":"Caro-Kann Defense", "e4 d5":"Scandinavian Defense",
    "e4 Nf6":"Alekhine's Defense", "e4 g6":"Modern Defense",
    "d4 d5":"Closed Game", "d4 d5 c4":"Queen's Gambit",
    "d4 d5 c4 e6":"QGD", "d4 d5 c4 c6":"Slav Defense",
    "d4 Nf6 c4 g6":"King's Indian", "d4 Nf6 c4 e6":"Queen's Indian",
    "d4 Nf6 c4 c5":"Benoni Defense", "d4 f5":"Dutch Defense",
}

def clamp(v, lo, hi): return max(lo, min(hi, v))

# ══════════════════════════════════════════════════════════════════════════════
# PLAYER DATA
# ══════════════════════════════════════════════════════════════════════════════
IntDataKey = Literal["elo", "peak_elo", "games_played", "wins", "losses", "draws"]
BoolDataKey = Literal["sound_on"]
StrDataKey = Literal["username", "board_theme"]


class PlayerData:
    DEFAULTS: ClassVar[dict[str, object]] = {"username":"Player","elo":400,"peak_elo":400,
                "games_played":0,"wins":0,"losses":0,"draws":0,
                "board_theme":"Green","sound_on":True}
    def __init__(self, path: str):
        self.path = path
        self.data: dict[str, object] = dict(self.DEFAULTS)
        self._load()
    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path,"r",encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data.update(loaded)
            except Exception: pass
    def save(self) -> None:
        try:
            with open(self.path,"w",encoding="utf-8") as f:
                json.dump(self.data,f,indent=2)
        except Exception: pass
    @overload
    def __getitem__(self, k: IntDataKey) -> int: ...
    @overload
    def __getitem__(self, k: BoolDataKey) -> bool: ...
    @overload
    def __getitem__(self, k: StrDataKey) -> str: ...
    @overload
    def __getitem__(self, k: str) -> object: ...
    def __getitem__(self, k: str) -> object:
        v = self.data.get(k, self.DEFAULTS.get(k))
        if k in ("elo", "peak_elo", "games_played", "wins", "losses", "draws"):
            try: return int(cast(Any, v))
            except (TypeError, ValueError): return int(cast(Any, self.DEFAULTS[k]))
        if k == "sound_on":
            return bool(v)
        if k == "board_theme":
            return str(v)
        return v
    def __setitem__(self, k: str, v: object) -> None:
        if k in ("elo", "peak_elo", "games_played", "wins", "losses", "draws"):
            try: self.data[k]=int(cast(Any, v))
            except (TypeError, ValueError): self.data[k]=v
        elif k == "sound_on":
            self.data[k]=bool(v)
        else:
            self.data[k]=v

# ══════════════════════════════════════════════════════════════════════════════
# ELO SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
class EloSystem:
    @staticmethod
    def k(elo, games):
        if games < 30 or elo < 1000: return 40
        if elo < 2000: return 20
        return 10
    @staticmethod
    def expected(p, o): return 1/(1+10**((o-p)/400))
    @staticmethod
    def compute(p, o, score, games):
        k=EloSystem.k(p,games); e=EloSystem.expected(p,o)
        nw=max(100,int(round(p+k*(score-e)))); return nw-p, nw

# ══════════════════════════════════════════════════════════════════════════════
# SOUND MANAGER  — chess.com-like wooden piece sounds
# ══════════════════════════════════════════════════════════════════════════════
class SoundManager:
    SR = 44100

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sounds: dict = {}
        self._init()

    # Pseudo-random noise (deterministic, no numpy needed)
    _lcg_state = 1

    def _noise(self):
        self._lcg_state = (self._lcg_state * 1664525 + 1013904223) & 0xFFFFFFFF
        return self._lcg_state / 0x80000000 - 1.0

    def _make(self, samples_fn, duration, vol=0.55):
        """Build a stereo Sound from a sample function."""
        n   = int(self.SR * duration)
        buf = bytearray(n * 4)
        for i in range(n):
            t    = i / self.SR
            samp = int(32767 * vol * clamp(samples_fn(t, i), -1.0, 1.0))
            lo, hi = samp & 0xFF, (samp >> 8) & 0xFF
            b = i * 4
            buf[b]=buf[b+2]=lo; buf[b+1]=buf[b+3]=hi
        try:    return pygame.mixer.Sound(buffer=bytes(buf))
        except: return None

    def _wood(self, freq=240, vol=0.55, dur=0.10):
        """Wood-piece-on-board thock — fast attack, exponential decay, noise burst."""
        def fn(t, i):
            env   = math.exp(-t * 35)
            wave  = (math.sin(2*math.pi*freq*t)*0.65
                   + math.sin(2*math.pi*freq*1.6*t)*0.20
                   + math.sin(2*math.pi*freq*0.5*t)*0.15)
            # impact noise burst
            noise = self._noise() * math.exp(-t * 180) * 0.4
            return (wave + noise) * env
        return self._make(fn, dur, vol)

    def _tone_env(self, freqs, dur, vol=0.45, decay=28):
        def fn(t, i):
            env = math.exp(-t*decay)
            return sum(math.sin(2*math.pi*f*t) for f in freqs)/len(freqs)*env
        return self._make(fn, dur, vol)

    def _chord(self, freqs, dur, vol=0.40):
        def fn(t, i):
            atk = min(0.01, dur*0.1)
            rel = dur * 0.35
            if t < atk:      env = t/atk
            elif t > dur-rel: env = max(0,(dur-t)/rel)
            else:             env = 1.0
            return sum(math.sin(2*math.pi*f*t) for f in freqs)/len(freqs)*env
        return self._make(fn, dur, vol)

    def _init(self):
        try:
            pygame.mixer.init(self.SR, -16, 2, 512)
        except Exception:
            self.enabled = False; return
        # Move — soft wooden thock
        self.sounds["move"]     = self._wood(240, 0.52, 0.090)
        # Capture — heavier thock
        self.sounds["capture"]  = self._wood(200, 0.60, 0.115)
        # Castle — two quick tones
        self.sounds["castle"]   = self._tone_env([350, 500], 0.14, 0.45, 22)
        # Promote — bright rising tone
        self.sounds["promote"]  = self._tone_env([660, 880], 0.18, 0.48, 16)
        # Check — two sharp alerts
        self.sounds["check"]    = self._tone_env([1100, 1320], 0.10, 0.50, 30)
        # Game end (Win)
        self.sounds["game_win"] = self._chord([523, 659, 784, 1047], 0.55, 0.40)
        # Game end (Loss)
        self.sounds["game_los"] = self._chord([392, 349, 294], 0.55, 0.38)
        # Draw
        self.sounds["game_drw"] = self._chord([523, 659, 784], 0.40, 0.35)
        # Illegal
        self.sounds["illegal"]  = self._tone_env([180], 0.08, 0.30, 50)

    def play(self, name):
        if not self.enabled: return
        s = self.sounds.get(name)
        if s:
            try: s.play()
            except Exception: pass

# ══════════════════════════════════════════════════════════════════════════════
# CHESS ENGINE — Stockfish + fallback minimax
# ══════════════════════════════════════════════════════════════════════════════
class ChessEngine:
    def __init__(self, sf_path):
        self.sf_path  = sf_path
        self.engine   = None
        self.use_sf   = False
        self._lock    = threading.Lock()
        self._move    = None
        self._thinking= False
        self._eval_cp = 0
        self._eval_mt = None
        self._eval_bsy= False
        self._open()

    def _open(self):
        if not os.path.exists(self.sf_path): return
        try:
            self.engine = chess_engine_mod.SimpleEngine.popen_uci(self.sf_path)
            self.use_sf = True
        except Exception: pass

    def configure(self, params: dict):
        """Configure Stockfish strength from an adaptive-params dict."""
        if not self.use_sf or not self.engine: return
        try:
            if params["elo"] < 1350:
                self.engine.configure({"UCI_LimitStrength": False,
                                        "Skill Level": params["skill"]})
            elif params["elo"] < 2600:
                self.engine.configure({"UCI_LimitStrength": True,
                                        "UCI_Elo": params["elo"],
                                        "Skill Level": 20})
            else:
                self.engine.configure({"UCI_LimitStrength": False, "Skill Level": 20})
        except Exception: pass

    # ── Async move ────────────────────────────────────────────────────────────
    def request_move(self, board, params: dict):
        if self._thinking: return
        self._thinking = True; self._move = None
        threading.Thread(target=self._think, args=(board.copy(), params), daemon=True).start()

    def _think(self, board, params: dict):
        try:
            if self.use_sf and self.engine:
                # Jitter think time for human feel
                t = params["think"] * random.uniform(0.75, 1.35)
                # Enforce both calculation time and physical search depth limits to match rating
                res = self.engine.play(board, chess_engine_mod.Limit(time=t, depth=params.get("depth", 1)))
                move = res.move
            else:
                move = self._fb_move(board, params["depth"])
        except Exception:
            move = self._fb_move(board, 1)
        with self._lock:
            self._move = move; self._thinking = False

    def get_move(self):
        with self._lock:
            if not self._thinking and self._move is not None:
                m, self._move = self._move, None; return m
        return None

    @property
    def thinking(self): return self._thinking

    # ── Async eval ────────────────────────────────────────────────────────────
    def request_eval(self, board):
        if self._eval_bsy: return
        self._eval_bsy = True
        threading.Thread(target=self._eval_thread, args=(board.copy(),), daemon=True).start()

    def _eval_thread(self, board):
        try:
            if self.use_sf and self.engine:
                info  = self.engine.analyse(board, chess_engine_mod.Limit(depth=10))
                score = info["score"].white()
                if score.is_mate():
                    self._eval_mt = score.mate()
                    self._eval_cp = 10000*(1 if score.mate()>0 else -1)
                else:
                    self._eval_cp = score.score(mate_score=10000) or 0
                    self._eval_mt = None
            else:
                self._eval_cp = self._fb_eval(board); self._eval_mt = None
        except Exception: pass
        finally: self._eval_bsy = False

    def get_eval(self): return self._eval_cp, self._eval_mt

    # ── Fallback minimax ──────────────────────────────────────────────────────
    def _fb_eval(self, board):
        if board.is_checkmate(): return -100000 if board.turn==chess.WHITE else 100000
        if board.is_game_over(): return 0
        s=0
        for sq,p in board.piece_map().items():
            v=PVAL_CP[p.piece_type]; idx=sq if p.color==chess.WHITE else chess.square_mirror(sq)
            pst=PST[p.piece_type][idx]
            if p.color==chess.WHITE: s+=v+pst
            else: s-=v+pst
        return s

    def _order(self, board, moves):
        def sc(m):
            s=0
            if board.is_capture(m):
                v=board.piece_at(m.to_square); a=board.piece_at(m.from_square)
                if v and a: s+=10*PVAL.get(v.piece_type,0)-PVAL.get(a.piece_type,0)
            if m.promotion: s+=PVAL.get(m.promotion,0)+9
            if board.gives_check(m): s+=2
            return s
        return sorted(list(moves),key=sc,reverse=True)

    def _minimax(self, board, depth, alpha, beta):
        if board.is_checkmate(): return -100000 if board.turn==chess.WHITE else 100000
        if board.is_game_over(): return 0
        if depth==0: return self._fb_eval(board)
        moves=self._order(board, board.legal_moves)
        if board.turn==chess.WHITE:
            val=-math.inf
            for m in moves:
                board.push(m); val=max(val,self._minimax(board,depth-1,alpha,beta)); board.pop()
                alpha=max(alpha,val)
                if beta<=alpha: break
            return val
        else:
            val=math.inf
            for m in moves:
                board.push(m); val=min(val,self._minimax(board,depth-1,alpha,beta)); board.pop()
                beta=min(beta,val)
                if beta<=alpha: break
            return val

    def _fb_move(self, board, depth):
        moves=self._order(board, board.legal_moves)
        if not moves: return None
        top=moves[:3] if len(moves)>=3 else moves[:]
        random.shuffle(top); moves=top+moves[3:]
        best=moves[0]; bs=-math.inf if board.turn==chess.WHITE else math.inf
        for m in moves:
            board.push(m); s=self._minimax(board,depth-1,-math.inf,math.inf); board.pop()
            if board.turn==chess.WHITE and s>bs: bs,best=s,m
            elif board.turn==chess.BLACK and s<bs: bs,best=s,m
        return best

    def close(self):
        if self.engine:
            try: self.engine.quit()
            except Exception: pass

# ══════════════════════════════════════════════════════════════════════════════
# CHESS APP
# ══════════════════════════════════════════════════════════════════════════════
class ChessApp:
    S_HOME  = "home"
    S_SETUP = "setup"
    S_GAME  = "game"
    S_OVER  = "over"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Chess Master")
        self.clock  = pygame.time.Clock()

        self.pdata  = PlayerData(DATA_FILE)
        self.engine = ChessEngine(SF_PATH)
        self.sound  = SoundManager(self.pdata["sound_on"])

        self.state  = self.S_HOME
        self.show_settings = False

        # Game options (shown on setup screen)
        self.setup_color  = "white"
        self.player_color = chess.WHITE
        # NOTE: no manual diff_idx — difficulty adapts to player ELO automatically
        self.timing_idx   = 6           # 10+0
        self.theme_name   = self.pdata["board_theme"]
        self.theme        = THEMES.get(self.theme_name, THEMES["Green"])
        self.setup_tab    = TIME_MODES[self.timing_idx]["cat"]
        self.flipped      = False

        # Board state
        self.board           = chess.Board()
        self.ai_color        = chess.BLACK
        self.sel_sq          = None
        self.legal_tgts: list= []
        self.san_moves: list = []
        self.view_off        = 0
        self.pending_promo   = None   # (from_sq, to_sq)
        self.promo_rects: list=[]
        self.game_over       = False
        self.result_msg      = ""
        self.result_reason   = ""
        self.result_score    = None
        self.elo_change      = 0
        self.new_elo         = self.pdata["elo"]
        self.draw_offered    = False
        self._draw_offer_t   = 0

        # Clocks
        self.times     = {chess.WHITE:0.0, chess.BLACK:0.0}
        self.last_tick = pygame.time.get_ticks()

        # Animation
        self.anim = None

        # AI scheduling — human-like variable delays
        self.ai_delay_ms   = 0
        self.ai_delay_start= None

        # Eval
        self.eval_cp   = 0
        self.eval_mate = None
        self._eval_fen = ""

        # Move-log scroll
        self.log_scroll = 0

        # Opening
        self.opening = ""

        # ── DRAG SYSTEM ──────────────────────────────────────────────────────
        self.drag_sq        = None   # square piece was picked up from
        self.drag_piece     = None   # the piece being dragged
        self.drag_pos       = (0,0)  # current cursor position
        self.drag_confirmed = False  # True once mouse moved > threshold from pickup
        self._mdown_pos     = None   # position of last MOUSEBUTTONDOWN

        # Rect registries (rebuilt each frame)
        self._setup_rects:    dict = {}
        self._sb_btns:        dict = {}
        self._over_btns:      dict = {}
        self._settings_rects: dict = {}

        # Assets
        self.piece_imgs: dict = {}
        self._img_cache: dict = {}
        self._load_imgs()

        # Fonts & layout
        self._font_path = self._find_font()
        self.layout: dict = {}
        self._update_layout((WIN_W, WIN_H))

        # Home-screen animation timer
        self.home_t = 0.0
        self.premove = None

    # ─────────────────────────────────────────────────────────────────────────
    # ASSETS
    # ─────────────────────────────────────────────────────────────────────────
    def _find_font(self):
        for n in ("segoeuisymbol","segoeui","dejavusans","arialunicodems","arial"):
            p = pygame.font.match_font(n)
            if p: return p
        return None

    def _load_imgs(self):
        if not os.path.isdir(NEO_DIR): return
        cm={chess.WHITE:"w",chess.BLACK:"b"}
        pm={chess.PAWN:"p",chess.KNIGHT:"n",chess.BISHOP:"b",
            chess.ROOK:"r",chess.QUEEN:"q",chess.KING:"k"}
        for col,cp in cm.items():
            for pt,pp in pm.items():
                path=os.path.join(NEO_DIR,f"{cp}{pp}.png")
                if os.path.exists(path):
                    try: self.piece_imgs[chess.Piece(pt,col)]=pygame.image.load(path).convert_alpha()
                    except Exception: pass

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT & FONTS
    # ─────────────────────────────────────────────────────────────────────────
    def _update_layout(self, size):
        w=max(size[0],MIN_W); h=max(size[1],MIN_H)
        aw=w-SB_W-EVAL_W-PAD*5; ah=h-NAV_H-STRIP_H*2-PAD*3
        sq=max(44,min(aw//8, ah//8)); bsz=sq*8
        by=NAV_H+PAD+STRIP_H
        # Center the active components horizontally
        active_w = EVAL_W + bsz + SB_W + PAD * 2
        start_x = max(PAD, (w - active_w) // 2)
        bx = start_x + EVAL_W + PAD
        self.layout={
            "w":w,"h":h,"sq":sq,
            "board":   pygame.Rect(bx,by,bsz,bsz),
            "eval_bar":pygame.Rect(start_x,by,EVAL_W,bsz),
            "top_strip":pygame.Rect(bx,NAV_H+PAD,bsz,STRIP_H),
            "bot_strip":pygame.Rect(bx,by+bsz,bsz,STRIP_H),
            "sidebar": pygame.Rect(bx+bsz+PAD,NAV_H+PAD,SB_W,h-NAV_H-PAD*2),
            "nav":     pygame.Rect(0,0,w,NAV_H),
        }
        self._build_fonts(sq); self._img_cache.clear()

    def _build_fonts(self, sq=80):
        def sf(sz,b=False): return pygame.font.SysFont("arial",sz,bold=b)
        def uf(sz):
            if self._font_path: return pygame.font.Font(self._font_path,sz)
            return sf(sz)
        self.f_title   =sf(34,True); self.f_head=sf(22,True); self.f_sub=sf(18,True)
        self.f_body    =sf(16);      self.f_sm  =sf(13);      self.f_xs =sf(11)
        self.f_clock   =sf(28,True); self.f_elo =sf(22,True); self.f_btn=sf(13,True)
        self.f_coord   =sf(11);      self.f_huge=sf(48,True)
        self.f_piece   =uf(max(24,sq-6))
        self.f_piece_sm=uf(20);  self.f_piece_xs=uf(14)

    # ─────────────────────────────────────────────────────────────────────────
    # BOARD PERSPECTIVE
    # ─────────────────────────────────────────────────────────────────────────
    def _black_bot(self):
        if self.flipped: return self.player_color==chess.WHITE
        return self.player_color==chess.BLACK

    def sq_to_rect(self, sq):
        br=self.layout["board"]; s=self.layout["sq"]
        f=chess.square_file(sq); r=chess.square_rank(sq)
        if self._black_bot(): col,row=7-f,r
        else: col,row=f,7-r
        return pygame.Rect(br.x+col*s, br.y+row*s, s, s)

    def px_to_sq(self, pos):
        br=self.layout["board"]; s=self.layout["sq"]
        if not br.collidepoint(pos): return None
        col=(pos[0]-br.x)//s; row=(pos[1]-br.y)//s
        if not(0<=col<8 and 0<=row<8): return None
        if self._black_bot(): return chess.square(7-col, row)
        return chess.square(col, 7-row)

    def disp_board(self):
        if self.view_off==0: return self.board
        b=self.board.copy()
        for _ in range(abs(self.view_off)):
            if b.move_stack: b.pop()
        return b

    # ─────────────────────────────────────────────────────────────────────────
    # ADAPTIVE AI PARAMS
    # ─────────────────────────────────────────────────────────────────────────
    def _ai_params(self) -> dict:
        """Return AI parameters computed from the player's current ELO."""
        return compute_ai_params(self.pdata["elo"])

    # ─────────────────────────────────────────────────────────────────────────
    # GAME MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────
    def new_game(self):
        self.board=chess.Board()
        self.ai_color=chess.BLACK if self.player_color==chess.WHITE else chess.WHITE
        self.sel_sq=None; self.legal_tgts=[]
        self.san_moves=[]; self.view_off=0
        self.pending_promo=None; self.promo_rects=[]
        self.game_over=False; self.result_msg=""; self.result_reason=""
        self.result_score=None; self.elo_change=0; self.new_elo=self.pdata["elo"]
        self.anim=None; self.ai_delay_start=None; self.draw_offered=False
        self.premove=None
        self.log_scroll=0; self.opening=""; self.eval_cp=0; self.eval_mate=None
        self._eval_fen=""; self._img_cache.clear(); self.flipped=False
        # Drag reset
        self.drag_sq=None; self.drag_piece=None; self.drag_confirmed=False
        mode=TIME_MODES[self.timing_idx]
        t=mode["min"]*60.0 if mode["min"]>0 else float("inf")
        self.times={chess.WHITE:t, chess.BLACK:t}
        self.last_tick=pygame.time.get_ticks()
        self.engine.configure(self._ai_params())

    def clear_sel(self):
        self.sel_sq=None; self.legal_tgts=[]

    # ─────────────────────────────────────────────────────────────────────────
    # PUSH MOVE
    # ─────────────────────────────────────────────────────────────────────────
    def push_move(self, move):
        self.view_off=0
        board=self.board; piece=board.piece_at(move.from_square)
        if piece is None: return
        is_cap=board.is_capture(move); is_cas=board.is_castling(move)
        is_pro=move.promotion is not None; chk=board.gives_check(move)
        san=board.san(move)
        # Increment
        mode=TIME_MODES[self.timing_idx]
        if len(board.move_stack)>=2 and self.times[board.turn]!=float("inf"):
            self.times[board.turn]+=mode["inc"]
        # Build anim
        ap=[{"piece":piece,"from":move.from_square,"to":move.to_square}]
        if is_cas:
            rm={chess.G1:(chess.ROOK,chess.WHITE,chess.H1,chess.F1),
                chess.C1:(chess.ROOK,chess.WHITE,chess.A1,chess.D1),
                chess.G8:(chess.ROOK,chess.BLACK,chess.H8,chess.F8),
                chess.C8:(chess.ROOK,chess.BLACK,chess.A8,chess.D8)}
            if move.to_square in rm:
                pt,co,fr,to=rm[move.to_square]
                ap.append({"piece":chess.Piece(pt,co),"from":fr,"to":to})
        # Sound
        if is_pro:       self.sound.play("promote")
        elif is_cas:     self.sound.play("castle")
        elif is_cap:     self.sound.play("capture")
        else:            self.sound.play("move")
        self.anim={"pieces":ap,"start":pygame.time.get_ticks(),"dur":120,
                   "move":move,"san":san,"chk":chk}
        self.clear_sel()
        self.drag_sq=None; self.drag_piece=None; self.drag_confirmed=False

    def finalize_move(self):
        a=self.anim
        if a is None: return
        self.board.push(a["move"]); self.san_moves.append(a["san"])
        self.anim=None; self.log_scroll=0
        self.opening=self._detect_opening()
        self._check_over()
        if not self.game_over and a["chk"] and self.board.is_check():
            self.sound.play("check")
        self._eval_fen=""

        # Premove instant execution check
        if not self.game_over and self.board.turn == self.player_color and self.premove is not None:
            m = self.premove; self.premove = None
            if m in self.board.legal_moves:
                self.push_move(m)
            else:
                self.sound.play("illegal")

    def _detect_opening(self):
        for L in range(min(len(self.san_moves),8),0,-1):
            k=" ".join(self.san_moves[:L])
            if k in OPENINGS: return OPENINGS[k]
        return ""

    def _check_over(self):
        b=self.board
        if b.is_checkmate():
            if b.turn!=self.player_color:
                self.result_msg,self.result_reason,self.result_score="You Win!","by Checkmate",1.0
            else:
                self.result_msg,self.result_reason,self.result_score="You Lose","by Checkmate",0.0
        elif b.is_stalemate():
            self.result_msg,self.result_reason,self.result_score="Draw","by Stalemate",0.5
        elif b.is_repetition(3):
            self.result_msg,self.result_reason,self.result_score="Draw","by Repetition",0.5
        elif b.is_insufficient_material():
            self.result_msg,self.result_reason,self.result_score="Draw","Insufficient Material",0.5
        elif b.can_claim_fifty_moves():
            self.result_msg,self.result_reason,self.result_score="Draw","by 50-Move Rule",0.5
        else: return
        self._end_game()

    def _end_game(self):
        self.game_over=True
        if self.result_score==1.0:   self.sound.play("game_win")
        elif self.result_score==0.0: self.sound.play("game_los")
        else:                        self.sound.play("game_drw")
        if self.result_score is not None:
            elo=self.pdata["elo"]
            opp=self._ai_params()["elo"]   # adaptive opponent ELO
            chg,nw=EloSystem.compute(elo,opp,self.result_score,self.pdata["games_played"])
            self.elo_change=chg; self.new_elo=nw
            self.pdata["elo"]=nw
            self.pdata["peak_elo"]=max(self.pdata["peak_elo"],nw)
            self.pdata["games_played"]=self.pdata["games_played"]+1
            if   self.result_score==1.0: self.pdata["wins"]=self.pdata["wins"]+1
            elif self.result_score==0.0: self.pdata["losses"]=self.pdata["losses"]+1
            else:                        self.pdata["draws"]=self.pdata["draws"]+1
            self.pdata.save()
        self.state=self.S_OVER

    def _captures(self):
        start=chess.Board(); b=self.board; wl,bl=[],[]
        for pt in [chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT,chess.PAWN]:
            for _ in range(len(start.pieces(pt,chess.WHITE))-len(b.pieces(pt,chess.WHITE))): wl.append(pt)
            for _ in range(len(start.pieces(pt,chess.BLACK))-len(b.pieces(pt,chess.BLACK))): bl.append(pt)
        return wl,bl

    def _mat_bal(self, board=None):
        if board is None: board=self.board
        s=0
        for p in board.piece_map().values():
            v=PVAL[p.piece_type]
            if p.color==self.player_color: s+=v
            else: s-=v
        return s

    # ─────────────────────────────────────────────────────────────────────────
    # HUMAN-LIKE AI DELAY
    # ─────────────────────────────────────────────────────────────────────────
    def _human_delay_ms(self):
        """Compute a highly realistic human-like thinking delay based on the time control and game state."""
        mode = TIME_MODES[self.timing_idx]
        cat = mode["cat"] # "Bullet", "Blitz", "Rapid", "Unlimited"
        
        # Base delays in milliseconds
        if cat == "Bullet":
            lo, hi = 300, 1500
        elif cat == "Blitz":
            lo, hi = 1200, 4800
        elif cat == "Rapid":
            lo, hi = 3200, 12000
        else: # "Unlimited"
            lo, hi = 4500, 15000

        mn = len(self.board.move_stack) // 2 + 1
        
        # 1. Opening theory speedups
        if mn <= 4:
            lo = int(lo * 0.4)
            hi = int(hi * 0.4)
        elif mn <= 8:
            lo = int(lo * 0.7)
            hi = int(hi * 0.7)

        # 2. Obvious recapture speedups (70% chance)
        if self.board.move_stack:
            last_move = self.board.peek()
            if self.board.is_capture(last_move) and random.random() < 0.7:
                lo = int(lo * 0.3)
                hi = int(hi * 0.5)

        # 3. Check delay increases
        if self.board.is_check():
            lo = int(lo * 1.3)
            hi = int(hi * 1.6)

        # 4. Time pressure speedups
        at = self.times[self.ai_color]
        if at != float("inf"):
            if at < 15:
                lo, hi = 200, 800
            elif at < 45:
                lo = int(lo * 0.4)
                hi = int(hi * 0.5)

        # Ensure minimum delay based on category to maintain human feel, scaling down under time pressure
        if at != float("inf") and at < 15:
            min_lo = 180
        elif at != float("inf") and at < 45:
            min_lo = 400
        else:
            if cat == "Bullet":
                min_lo = 300
            elif cat == "Blitz":
                min_lo = 800
            elif cat == "Rapid":
                min_lo = 1500
            else: # "Unlimited"
                min_lo = 2000

        lo = max(min_lo, lo)
        hi = max(lo + 150, hi)
        return random.triangular(lo, hi, lo + (hi - lo) * 0.3)

    # ─────────────────────────────────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        running=True
        while running:
            dt_ms=self.clock.tick(60); dt=dt_ms/1000.0
            now=pygame.time.get_ticks(); self.home_t+=dt
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: running=False
                elif ev.type==pygame.VIDEORESIZE: self._update_layout(ev.size)
                else: self._handle_event(ev)
            if self.state in (self.S_GAME, self.S_OVER): self._update(dt,now)
            self.draw(); pygame.display.flip()
        self.engine.close(); pygame.quit(); sys.exit()

    # ─────────────────────────────────────────────────────────────────────────
    # EVENT DISPATCH
    # ─────────────────────────────────────────────────────────────────────────
    def _handle_event(self, ev):
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_ESCAPE and self.show_settings: self.show_settings=False
            elif ev.key==pygame.K_LEFT  and self.state in (self.S_GAME,self.S_OVER): self._nav(-1)
            elif ev.key==pygame.K_RIGHT and self.state in (self.S_GAME,self.S_OVER): self._nav(1)
            return
        if ev.type==pygame.MOUSEWHEEL:
            if self.state in (self.S_GAME,self.S_OVER): self.log_scroll=max(0,self.log_scroll-ev.y)
            return
        # ── DRAG: motion ─────────────────────────────────────────────────────
        if ev.type==pygame.MOUSEMOTION:
            self.drag_pos=ev.pos
            if self.drag_sq is not None and self._mdown_pos is not None:
                dx=ev.pos[0]-self._mdown_pos[0]; dy=ev.pos[1]-self._mdown_pos[1]
                if abs(dx)>6 or abs(dy)>6: self.drag_confirmed=True
            return
        # ── DRAG: release ─────────────────────────────────────────────────────
        if ev.type==pygame.MOUSEBUTTONUP:
            if ev.button==1:
                self._mdown_pos=None
                if self.state==self.S_GAME and not self.show_settings:
                    self._game_mouseup(ev.pos)
            return
        if ev.type!=pygame.MOUSEBUTTONDOWN: return
        pos=ev.pos; btn=ev.button
        if self.show_settings: self._click_settings(pos); return
        if btn==1:
            self._mdown_pos=pos
            if self.state==self.S_HOME:   self._click_home(pos)
            elif self.state==self.S_SETUP:self._click_setup(pos)
            elif self.state==self.S_GAME: self._game_mousedown(pos)
            elif self.state==self.S_OVER: self._click_over(pos)
        elif btn==3 and self.state==self.S_GAME:
            self.clear_sel()
            self.drag_sq=None; self.drag_piece=None; self.drag_confirmed=False
            self.premove=None

    def _nav(self, d):
        if self.anim: return
        self.view_off=clamp(self.view_off+d,-len(self.board.move_stack),0); self.clear_sel()

    # ─────────────────────────────────────────────────────────────────────────
    # GAME MOUSE DOWN — select or click-to-move (also primes drag)
    # ─────────────────────────────────────────────────────────────────────────
    def _game_mousedown(self, pos):
        if self.game_over: return
        # Gear
        if self._gear_rect().collidepoint(pos): self.show_settings=True; return
        # Promotion
        if self.pending_promo: self._click_promo(pos); return
        # Sidebar buttons
        if self._click_sb_btn(pos): return
        # Snap back to live
        if self.view_off!=0: self.view_off=0; self.clear_sel(); return
        # We can select pieces during the AI's turn to prepare a premove
        if self.anim: return
        sq=self.px_to_sq(pos)
        if sq is None: self.clear_sel(); self.drag_sq=None; return
        is_ai_turn = (self.board.turn != self.player_color)
        
        # Click-to-move or premove
        if self.sel_sq is not None and sq in self.legal_tgts:
            if is_ai_turn:
                self._queue_premove(self.sel_sq, sq)
            else:
                self._make_move(sq)
            self.drag_sq=None; self.drag_confirmed=False; return
            
        # Select or deselect
        piece=self.board.piece_at(sq)
        if piece and piece.color==self.player_color:
            self.sel_sq=sq
            if is_ai_turn:
                self.legal_tgts=sorted({s for s in range(64) if s != sq and (self.board.piece_at(s) is None or self.board.piece_at(s).color != self.player_color)})
            else:
                self.legal_tgts=sorted({m.to_square for m in self.board.legal_moves if m.from_square==sq})
            # Prime drag
            self.drag_sq=sq; self.drag_piece=piece
            self.drag_pos=pos; self.drag_confirmed=False
        else:
            self.clear_sel(); self.drag_sq=None

    # ─────────────────────────────────────────────────────────────────────────
    # GAME MOUSE UP — complete drag move
    # ─────────────────────────────────────────────────────────────────────────
    def _game_mouseup(self, pos):
        if self.drag_confirmed and self.drag_sq is not None and not self.game_over:
            sq=self.px_to_sq(pos)
            if sq is not None and sq in self.legal_tgts:
                if self.board.turn != self.player_color:
                    self._queue_premove(self.drag_sq, sq)
                else:
                    self._make_move(sq)
            else:
                self.clear_sel()
        self.drag_sq=None; self.drag_piece=None; self.drag_confirmed=False

    # ─────────────────────────────────────────────────────────────────────────
    # MAKE PLAYER MOVE (handles promotion check)
    # ─────────────────────────────────────────────────────────────────────────
    def _make_move(self, target):
        if self.sel_sq is None: return
        p=self.board.piece_at(self.sel_sq)
        if p and p.piece_type==chess.PAWN:
            r=chess.square_rank(target)
            if (self.player_color==chess.WHITE and r==7) or (self.player_color==chess.BLACK and r==0):
                self.pending_promo=(self.sel_sq,target)
                self._build_promo(target); return
        move=chess.Move(self.sel_sq,target)
        if move in self.board.legal_moves: self.push_move(move)
        self.clear_sel()

    def _queue_premove(self, from_sq, to_sq):
        p = self.board.piece_at(from_sq)
        promo = None
        if p and p.piece_type==chess.PAWN:
            r = chess.square_rank(to_sq)
            if (self.player_color==chess.WHITE and r==7) or (self.player_color==chess.BLACK and r==0):
                promo = chess.QUEEN
        self.premove = chess.Move(from_sq, to_sq, promotion=promo)
        self.clear_sel()

    def _build_promo(self, sq):
        self.promo_rects=[]; r=self.sq_to_rect(sq)
        for i,pt in enumerate([chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT]):
            y=r.y+i*r.height if chess.square_rank(sq)==7 else r.y-i*r.height
            self.promo_rects.append((pygame.Rect(r.x,y,r.width,r.height),pt))

    def _click_promo(self, pos):
        if self.pending_promo is None:
            self.clear_sel()
            return
        for rect,pt in self.promo_rects:
            if rect.collidepoint(pos):
                fr,to=self.pending_promo
                m=chess.Move(fr,to,promotion=pt)
                if m in self.board.legal_moves:
                    self.pending_promo=None; self.promo_rects=[]
                    self.push_move(m); self.clear_sel(); return
        self.pending_promo=None; self.promo_rects=[]; self.clear_sel()

    def _click_sb_btn(self, pos):
        for name,rect in self._sb_btns.items():
            if not rect.collidepoint(pos): continue
            if name=="flip": self.flipped=not self.flipped; self._img_cache.clear()
            elif name=="resign":
                self.result_msg,self.result_reason,self.result_score="You Lose","by Resignation",0.0
                self._end_game()
            elif name=="new": self.state=self.S_SETUP
            return True
        return False


    def _click_setup(self, pos):
        if self._gear_rect().collidepoint(pos): self.show_settings=True; return
        for name,rect in self._setup_rects.items():
            if not rect.collidepoint(pos): continue
            if name.startswith("cat_"):  self.setup_tab=name[4:]
            elif name.startswith("t_"): self.timing_idx=int(name[2:])
            elif name=="c_white":
                self.setup_color="white"
                self.player_color=chess.WHITE
            elif name=="c_black":
                self.setup_color="black"
                self.player_color=chess.BLACK
            elif name=="c_random":
                self.setup_color="random"
            elif name=="play":
                if self.setup_color == "random":
                    self.player_color = random.choice([chess.WHITE, chess.BLACK])
                elif self.setup_color == "white":
                    self.player_color = chess.WHITE
                else:
                    self.player_color = chess.BLACK
                self.new_game()
                self.state=self.S_GAME
            elif name=="back":          self.state=self.S_HOME
            break

    def _click_over(self, pos):
        for name,rect in self._over_btns.items():
            if not rect.collidepoint(pos): continue
            if name=="new":  self.state=self.S_SETUP
            elif name=="home": self.state=self.S_HOME; self.board=chess.Board(); self.san_moves=[]

    def _click_settings(self, pos):
        for name,rect in self._settings_rects.items():
            if not rect.collidepoint(pos): continue
            if name=="close": self.show_settings=False
            elif name.startswith("theme_"):
                t=name[6:]; self.theme_name=t; self.theme=THEMES.get(t,THEMES["Green"])
                self.pdata["board_theme"]=t; self.pdata.save(); self._img_cache.clear()
            elif name=="sound":
                self.sound.enabled=not self.sound.enabled
                self.pdata["sound_on"]=self.sound.enabled; self.pdata.save()
            elif name=="reset":
                for k in ("elo","peak_elo","games_played","wins","losses","draws"):
                    self.pdata[k]=400 if "elo" in k else 0
                self.pdata.save()
            break

    # ─────────────────────────────────────────────────────────────────────────
    # GAME UPDATE
    # ─────────────────────────────────────────────────────────────────────────
    def _update(self, dt, now):
        # Clock tick
        if not self.game_over and self.anim is None:
            ac=self.board.turn
            if len(self.board.move_stack)>0 and self.times[ac]!=float("inf"):
                self.times[ac]-=dt
                if self.times[ac]<=0:
                    self.times[ac]=0.0
                    if ac==self.player_color:
                        self.result_msg,self.result_reason,self.result_score="You Lose","on Time",0.0
                    else:
                        self.result_msg,self.result_reason,self.result_score="You Win!","on Time",1.0
                    self._end_game(); return
        # Finalize anim
        if self.anim and now-self.anim["start"]>=self.anim["dur"]:
            self.finalize_move(); return
        if self.anim: return
        # AI move with human-like delay
        if (not self.game_over and self.pending_promo is None
                and self.board.turn==self.ai_color and self.view_off==0):
            if not self.engine.thinking:
                move=self.engine.get_move()
                if move is not None:
                    if move in self.board.legal_moves: self.push_move(move)
                    else:
                        lg=list(self.board.legal_moves)
                        if lg: self.push_move(random.choice(lg))
                elif self.ai_delay_start is None:
                    self.ai_delay_ms   = self._human_delay_ms()
                    self.ai_delay_start= now
                elif now-self.ai_delay_start >= self.ai_delay_ms:
                    self.ai_delay_start=None
                    self.engine.request_move(self.board, self._ai_params())
        # Eval
        if not self.game_over and self.view_off==0:
            fen=self.board.fen()
            if fen!=self._eval_fen and not self.engine._eval_bsy:
                self._eval_fen=fen; self.engine.request_eval(self.board)
            if not self.engine._eval_bsy:
                self.eval_cp,self.eval_mate=self.engine.get_eval()

    # ─────────────────────────────────────────────────────────────────────────
    # DRAW DISPATCH
    # ─────────────────────────────────────────────────────────────────────────
    def draw(self):
        if   self.state==self.S_HOME:  self._draw_home()
        elif self.state==self.S_SETUP: self._draw_setup()
        elif self.state in (self.S_GAME,self.S_OVER):
            self._draw_game()
            if self.state==self.S_OVER: self._draw_over()
        if self.show_settings: self._draw_settings()

    # ═════════════════════════════════════════════════════════════════════════
    # HOME SCREEN  — chess.com style
    # ═════════════════════════════════════════════════════════════════════════
    def _draw_home(self):
        w,h=self.layout["w"],self.layout["h"]
        self.screen.fill(pygame.Color(C_BG))
        self._chess_bg()
        self._nav_bar("Chess Master")

        cx,cy=w//2, h//2

        # ── Left decorative panel ─────────────────────────────────────────────
        lp_w,lp_h=340,380
        lp=pygame.Rect(cx-lp_w//2-200, cy-lp_h//2, lp_w, lp_h)
        self._rr(C_CARD, lp, 20); self._rb(C_BORDER, lp, 20, 1)
        # Top accent
        self._rr(C_GREEN_D, pygame.Rect(lp.x,lp.y,lp.w,3), 2)

        # Large piece logo
        queen=chess.Piece(chess.QUEEN,chess.WHITE)
        qs=110; qx=lp.centerx-qs//2; qy=lp.y+44
        self._piece(queen,qx,qy,qs,qs)

        # Title
        ts=self.f_title.render("Chess Master", True, pygame.Color(C_WHITE))
        self.screen.blit(ts, ts.get_rect(centerx=lp.centerx, y=lp.y+176))
        sub=self.f_sm.render("Adaptive ELO Edition", True, pygame.Color(C_MUTED))
        self.screen.blit(sub, sub.get_rect(centerx=lp.centerx, y=lp.y+214))

        # Divider line
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(lp.x+40,lp.y+240),(lp.right-40,lp.y+240))

        # SF badge
        sf_ok=self.engine.use_sf
        bg_col = "#1B2D17" if sf_ok else "#2C2615"
        border_col = C_GREEN if sf_ok else C_GOLD
        badge_r=pygame.Rect(lp.centerx-90,lp.y+264,180,34)
        self._rr(bg_col, badge_r, 10)
        self._rb(border_col, badge_r, 10, 1)
        bst=self.f_sm.render(("Stockfish Active" if sf_ok else "Local AI"), True, pygame.Color(border_col))
        self.screen.blit(bst, bst.get_rect(center=badge_r.center))

        # ── Right profile+play panel ─────────────────────────────────────────
        rp_w,rp_h=340,380
        rp=pygame.Rect(cx-rp_w//2+200, cy-rp_h//2, rp_w, rp_h)
        self._rr(C_CARD, rp, 20); self._rb(C_BORDER, rp, 20, 1)
        self._rr(C_GREEN_D, pygame.Rect(rp.x,rp.y,rp.w,3), 2)

        # Avatar
        avx,avy=rp.x+50, rp.y+64
        pygame.draw.circle(self.screen,"#2E2A26",(avx,avy),36)
        pygame.draw.circle(self.screen,C_BORDER,(avx,avy),36,2)
        king=chess.Piece(chess.KING,chess.WHITE)
        self._piece(king,avx-20,avy-20,40,40)

        # Name
        nx=avx+48
        ns=self.f_head.render(self.pdata["username"], True, pygame.Color(C_WHITE))
        self.screen.blit(ns,(nx, rp.y+32))

        # ELO
        els=self.f_huge.render(str(self.pdata["elo"]), True, pygame.Color(C_GOLD))
        self.screen.blit(els,(nx, rp.y+54))
        rat=self.f_xs.render("Rating", True, pygame.Color(C_MUTED))
        self.screen.blit(rat,(nx+els.get_width()+6, rp.y+82))
        pk=self.f_xs.render(f"Peak: {self.pdata['peak_elo']}", True, pygame.Color(C_MUTED))
        self.screen.blit(pk,(nx, rp.y+108))

        # Divider
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(rp.x+24,rp.y+130),(rp.right-24,rp.y+130))

        # Stats
        stats=[(str(self.pdata["wins"]),"Wins",C_GREEN),
               (str(self.pdata["draws"]),"Draws",C_GRAY),
               (str(self.pdata["losses"]),"Losses",C_RED)]
        sy=rp.y+146
        for i,(val,lbl,col) in enumerate(stats):
            sx=rp.x+46+i*98
            vs=self.f_head.render(val,True,pygame.Color(col))
            ls=self.f_xs.render(lbl,True,pygame.Color(C_MUTED))
            self.screen.blit(vs,vs.get_rect(centerx=sx,y=sy))
            self.screen.blit(ls,ls.get_rect(centerx=sx,y=sy+28))

        # PLAY button
        mouse=pygame.mouse.get_pos()
        play_r=pygame.Rect(cx-130, cy+60, 260, 56)  # aligned to center
        # Use rp-relative for actual button
        play_r=pygame.Rect(rp.x+24, rp.bottom-76, rp.w-48, 52)
        pc=C_GREEN_D if play_r.collidepoint(mouse) else C_GREEN
        self._rr(pc, play_r, 14)
        pt2=self.f_sub.render("PLAY COMPUTER", True, pygame.Color(C_WHITE))
        self.screen.blit(pt2, pt2.get_rect(center=play_r.center))

        # Store play rect for click handler (centered)
        # We override with correct one in click handler — use center
        self._home_play_rect=play_r

        # Footer
        ft=self.f_xs.render("Left / Right keys to review moves  |  Settings on top right", True, pygame.Color(C_MUTED))
        self.screen.blit(ft,(w//2-ft.get_width()//2, h-22))

    def _click_home(self, pos):
        if self._gear_rect().collidepoint(pos): self.show_settings=True; return
        if hasattr(self,"_home_play_rect") and self._home_play_rect.collidepoint(pos):
            self.state=self.S_SETUP

    # ═════════════════════════════════════════════════════════════════════════
    # SETUP SCREEN  — chess.com opponent setup style
    # ═════════════════════════════════════════════════════════════════════════
    def _draw_setup(self):
        w,h=self.layout["w"],self.layout["h"]
        self.screen.fill(pygame.Color(C_BG)); self._chess_bg()
        self._nav_bar("New Game"); self._setup_rects={}; mouse=pygame.mouse.get_pos()

        # Two-panel layout
        pw=min(760,w-80); ph=min(530,h-NAV_H-40)
        px=(w-pw)//2; py=NAV_H+16
        panel=pygame.Rect(px,py,pw,ph)
        self._rr(C_CARD,panel,20); self._rb(C_BORDER,panel,20,1)

        half=pw//2; lx=px+24; rx=px+half+12; ry=py+20; rw=half-36
        # Divider
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(px+half,py+20),(px+half,py+ph-20))

        # ── LEFT: Adaptive opponent card ─────────────────────────────────────
        ai = self._ai_params()   # computed from current player ELO
        y=py+24
        hd=self.f_sub.render("Your Opponent", True, pygame.Color(C_WHITE))
        self.screen.blit(hd,(lx,y)); y+=34

        # Stockfish avatar — icon tier reflects computed strength
        tier_icons=[chess.PAWN,chess.KNIGHT,chess.BISHOP,chess.ROOK,chess.QUEEN,chess.KING]
        tier_names=["Beginner","Novice","Intermediate","Advanced","Expert","Master"]
        tier_idx=tier_names.index(ai["name"]) if ai["name"] in tier_names else 5
        icon=chess.Piece(tier_icons[tier_idx], chess.WHITE)
        ics=72; icx=px+half//2-ics//2; icy=y
        pygame.draw.circle(self.screen,"#2A2720",(icx+ics//2,icy+ics//2),ics//2+8)
        pygame.draw.circle(self.screen,C_BORDER,(icx+ics//2,icy+ics//2),ics//2+8,2)
        self._piece(icon,icx,icy,ics,ics)
        y+=ics+14

        # Stockfish name + adaptive level
        ns2=self.f_head.render("Stockfish", True, pygame.Color(C_WHITE))
        self.screen.blit(ns2,ns2.get_rect(centerx=px+half//2,y=y)); y+=28
        dn=self.f_body.render(ai["name"], True, pygame.Color(C_GREEN))
        self.screen.blit(dn,dn.get_rect(centerx=px+half//2,y=y)); y+=22
        el2=self.f_sm.render(f"Elo {ai['elo']}", True, pygame.Color(C_MUTED))
        self.screen.blit(el2,el2.get_rect(centerx=px+half//2,y=y)); y+=26

        # ── Adaptive info card ────────────────────────────────────────────────
        info_r=pygame.Rect(lx, y, half-lx+(px+half//2)-half//2, 76)
        info_r=pygame.Rect(px+16, y, half-32, 76)
        self._rr(C_SURFACE, info_r, 10); self._rb(C_BORDER, info_r, 10, 1)
        # Small "adaptive" badge
        badge_r=pygame.Rect(info_r.x+8, info_r.y+8, 88, 20)
        self._rr("#1E3013", badge_r, 6); self._rb(C_GREEN, badge_r, 6, 1)
        bs2=self.f_xs.render("⚡ ADAPTIVE", True, pygame.Color(C_GREEN))
        self.screen.blit(bs2, bs2.get_rect(center=badge_r.center))
        # Description
        d1=self.f_xs.render(f"Matched to your {self.pdata['elo']} rating", True, pygame.Color(C_GRAY))
        d2=self.f_xs.render(f"AI is {ai['elo'] - self.pdata['elo']} points above you", True, pygame.Color(C_MUTED))
        self.screen.blit(d1,(info_r.x+8, info_r.y+32))
        self.screen.blit(d2,(info_r.x+8, info_r.y+50))
        y+=info_r.height+10

        # Strength bar (visual only, no click)
        bar_w=half-32; bar_h=8
        bar_r=pygame.Rect(px+16, y, bar_w, bar_h)
        self._rr(C_SURFACE, bar_r, 4)
        fill=clamp((ai["elo"]-400)/2800, 0.0, 1.0)
        self._rr(C_GREEN, pygame.Rect(bar_r.x, bar_r.y, int(bar_w*fill), bar_h), 4)
        sr=self.f_xs.render(f"400", True, pygame.Color(C_MUTED))
        er=self.f_xs.render(f"3200", True, pygame.Color(C_MUTED))
        self.screen.blit(sr,(bar_r.x, bar_r.bottom+3))
        self.screen.blit(er,(bar_r.right-er.get_width(), bar_r.bottom+3))

        # ── RIGHT: Game settings ────────────────────────────────────────────
        y2=ry
        hd2=self.f_sub.render("Game Settings", True, pygame.Color(C_WHITE))
        self.screen.blit(hd2,(rx,y2)); y2+=34

        # Time control category tabs
        tab_w=(rw-(len(TIME_CATS)-1)*6)//len(TIME_CATS)
        for i,cat in enumerate(TIME_CATS):
            tr=pygame.Rect(rx+i*(tab_w+6),y2,tab_w,28)
            self._setup_rects[f"cat_{cat}"]=tr
            sel=(self.setup_tab==cat); hov=tr.collidepoint(mouse)
            if sel: bg5="#2D2B28"; tc2=C_WHITE
            elif hov: bg5=C_CARD_HOV; tc2=C_WHITE
            else: bg5=C_SURFACE; tc2=C_MUTED
            self._rr(bg5,tr,6)
            if sel: self._rb(C_GREEN,tr,6,1.5)
            ts2=self.f_xs.render(cat,True,pygame.Color(tc2))
            self.screen.blit(ts2,ts2.get_rect(center=tr.center))
        y2+=36

        # Time buttons
        modes=[m for m in TIME_MODES if m["cat"]==self.setup_tab]
        tbw=56; tbh=36; tbg=6
        for i,mode in enumerate(modes):
            oi=TIME_MODES.index(mode)
            br3=pygame.Rect(rx+i*(tbw+tbg),y2,tbw,tbh)
            self._setup_rects[f"t_{oi}"]=br3
            sel=(self.timing_idx==oi); hov=br3.collidepoint(mouse)
            if sel: bg6="#2D2B28"; bc3=C_GREEN; tc3=C_WHITE
            elif hov: bg6=C_CARD_HOV; bc3=C_BORDER; tc3=C_WHITE
            else: bg6=C_SURFACE; bc3=C_BORDER; tc3=C_MUTED
            self._rr(bg6,br3,8); self._rb(bc3,br3,8,2 if sel else 1)
            ms=self.f_sm.render(mode["name"],True,pygame.Color(tc3))
            self.screen.blit(ms,ms.get_rect(center=br3.center))
        y2+=tbh+20

        # Color picker
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(rx,y2),(rx+rw,y2)); y2+=12
        cl=self.f_sm.render("Play as", True, pygame.Color(C_GRAY))
        self.screen.blit(cl,(rx,y2)); y2+=22
        cols=[("White","white","c_white"),("Random","random","c_random"),("Black","black","c_black")]
        cbw=(rw-(len(cols)-1)*8)//len(cols); cbh=52
        for i,(lbl,val,key) in enumerate(cols):
            cr=pygame.Rect(rx+i*(cbw+8),y2,cbw,cbh)
            self._setup_rects[key]=cr
            sel=(self.setup_color==val)
            hov=cr.collidepoint(mouse)
            if sel: bg7="#1E3013"; bc4=C_GREEN
            elif hov: bg7=C_CARD_HOV; bc4=C_BORDER
            else: bg7=C_SURFACE; bc4=C_BORDER
            self._rr(bg7,cr,10); self._rb(bc4,cr,10,2 if sel else 1)
            
            # Center the icon and text inside the button
            cs=self.f_sm.render(lbl,True,pygame.Color(C_WHITE if sel else C_GRAY))
            icon_sz = 20
            gap = 6
            total_w = icon_sz + gap + cs.get_width()
            start_x = cr.centerx - total_w // 2
            icon_y = cr.centery - icon_sz // 2
            text_y = cr.centery - cs.get_height() // 2
            
            # Render premium custom vector chess icons
            if val == "white":
                self._draw_vector_crown(start_x, icon_y, icon_sz, is_white=True, selected=sel)
            elif val == "black":
                self._draw_vector_crown(start_x, icon_y, icon_sz, is_white=False, selected=sel)
            else: # random
                self._draw_vector_random_icon(start_x, icon_y, icon_sz, selected=sel)
                
            self.screen.blit(cs,(start_x + icon_sz + gap, text_y))
        y2+=cbh+20

        # Your profile mini card
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(rx,y2),(rx+rw,y2)); y2+=12
        prof_r=pygame.Rect(rx,y2,rw,44)
        self._rr(C_SURFACE,prof_r,8); self._rb(C_BORDER,prof_r,8,1)
        avx2,avy2=prof_r.x+24,prof_r.centery
        pygame.draw.circle(self.screen,"#2E2A26",(avx2,avy2),16)
        pygame.draw.circle(self.screen,C_BORDER,(avx2,avy2),16,1)
        self._piece(chess.Piece(chess.KING,chess.WHITE),avx2-10,avy2-10,20,20)
        pn=self.f_sm.render(self.pdata["username"],True,pygame.Color(C_WHITE))
        pe=self.f_xs.render(f"Elo {self.pdata['elo']}",True,pygame.Color(C_MUTED))
        self.screen.blit(pn,(avx2+22,prof_r.y+8))
        self.screen.blit(pe,(avx2+22,prof_r.y+24))
        y2+=prof_r.height+16

        # PLAY button
        play_r=pygame.Rect(rx,y2,rw,48)
        self._setup_rects["play"]=play_r
        pc=C_GREEN_D if play_r.collidepoint(mouse) else C_GREEN
        self._rr(pc,play_r,12)
        ps=self.f_sub.render("Play", True, pygame.Color(C_WHITE))
        self.screen.blit(ps,ps.get_rect(center=play_r.center))

        # Back button
        back_r=pygame.Rect(px+24,py+ph-50,90,34)
        self._setup_rects["back"]=back_r
        bc5=C_CARD_HOV if back_r.collidepoint(mouse) else C_SURFACE
        self._rr(bc5,back_r,8); self._rb(C_BORDER,back_r,8,1)
        bs=self.f_sm.render("← Back",True,pygame.Color(C_GRAY))
        self.screen.blit(bs,bs.get_rect(center=back_r.center))

    # ═════════════════════════════════════════════════════════════════════════
    # GAME SCREEN
    # ═════════════════════════════════════════════════════════════════════════
    def _draw_game(self):
        w,h=self.layout["w"],self.layout["h"]
        self.screen.fill(pygame.Color(C_BG)); self._nav_bar(self.opening or "Chess Master")
        db=self.disp_board(); bb=self._black_bot()
        top_c=chess.BLACK if not bb else chess.WHITE
        bot_c=chess.WHITE if not bb else chess.BLACK
        self._draw_strip(self.layout["top_strip"],top_c,db,top=True)
        self._draw_strip(self.layout["bot_strip"],bot_c,db,top=False)
        self._draw_eval(self.layout["eval_bar"])
        self._draw_board(db)
        if self.pending_promo and self.promo_rects: self._draw_promo()
        self._draw_sidebar(db)

    # ── Player strip ──────────────────────────────────────────────────────────
    def _draw_strip(self, rect, color, db, top):
        is_player=(color==self.player_color)
        self._rr(C_CARD,rect,8)
        # Avatar
        avx,avy=rect.x+28,rect.centery
        ac=C_BORDER
        pygame.draw.circle(self.screen,"#2E2A26",(avx,avy),20)
        pygame.draw.circle(self.screen,ac,(avx,avy),20,1)
        self._piece(chess.Piece(chess.KING,color),avx-12,avy-12,24,24)
        # Name — AI always shows the adaptive level computed at game start
        if is_player:
            name = self.pdata["username"]
            elo  = self.pdata["elo"]
        else:
            ap   = self._ai_params()        # reflects pre-game rating
            name = f"Stockfish · {ap['name']}"
            elo  = ap["elo"]
        nx=avx+28
        name_surf = self.f_body.render(name,True,pygame.Color(C_WHITE))
        elo_surf = self.f_sm.render(f"Elo {elo}",True,pygame.Color(C_MUTED))
        name_w = name_surf.get_width()
        elo_w = elo_surf.get_width()
        text_max_w = max(name_w, elo_w)
        self.screen.blit(name_surf,(nx,avy-name_surf.get_height()-1))
        self.screen.blit(elo_surf,(nx,avy+2))
        # Captures strip starting dynamically after text
        self._draw_caps(rect,color,db,nx + text_max_w + 16)
        # Clock widget - cleanly rendered on the right for all modes
        tv=self.times[color]
        active=(db.turn==color and not self.game_over and self.anim is None and len(self.board.move_stack)>0)
        low=(tv!=float("inf") and tv<10)
        ck_bg=("#2A3D1A" if not low else "#3D1A1A") if active else C_SURFACE
        ck_c=(C_GREEN if not low else C_CLK_LOW) if active else C_MUTED
        ckr=pygame.Rect(rect.right-114,rect.y+8,102,rect.height-16)
        self._rr(ck_bg,ckr,6)
        if active: self._rb(ck_c,ckr,6,1)
        ts2 = self._fmt(tv) if tv != float("inf") else "∞"
        cks=self.f_clock.render(ts2,True,pygame.Color(ck_c))
        self.screen.blit(cks,cks.get_rect(center=ckr.center))

    def _draw_caps(self, strip, color, db, ox):
        wl,bl=self._captures()
        captured=bl if color==chess.WHITE else wl
        if not captured: return
        captured.sort(key=lambda pt:-PVAL.get(pt,0))
        ps,gap=15,1; opp=chess.BLACK if color==chess.WHITE else chess.WHITE
        drawn_count = 0
        for i,pt in enumerate(captured[:12]):
            px2=ox+i*(ps+gap)
            if px2+ps>strip.right-120: break
            self._piece(chess.Piece(pt,opp),px2,strip.centery-ps//2,ps,ps)
            drawn_count += 1
        bal=self._mat_bal(db)
        if bal!=0 and color==self.player_color:
            sign="+" if bal>0 else ""
            bs=self.f_xs.render(f"{sign}{bal}",True,pygame.Color(C_GREEN if bal>0 else C_MUTED))
            bx = ox + drawn_count * (ps + gap) + 4
            if bx + bs.get_width() < strip.right - 120:
                self.screen.blit(bs,(bx,strip.centery-bs.get_height()//2))

    # ── Eval bar ──────────────────────────────────────────────────────────────
    def _draw_eval(self, rect):
        self._rr(C_SURFACE,rect,6)
        cp=self.eval_cp
        if self.board.is_game_over():
            try:
                oc=self.board.outcome()
                if oc: cp=10000 if oc.winner==chess.WHITE else (-10000 if oc.winner==chess.BLACK else 0)
            except Exception: pass
        if self.eval_mate is not None:
            ratio=0.97 if self.eval_mate>0 else 0.03
        else:
            ratio=1/(1+math.exp(-cp/380)); ratio=clamp(ratio,0.04,0.96)
        bb=self._black_bot()
        if not bb:
            wh=int(rect.height*ratio); wr=pygame.Rect(rect.x,rect.bottom-wh,rect.width,wh)
            br2=pygame.Rect(rect.x,rect.y,rect.width,rect.height-wh)
        else:
            bh=int(rect.height*(1-ratio)); br2=pygame.Rect(rect.x,rect.bottom-bh,rect.width,bh)
            wr=pygame.Rect(rect.x,rect.y,rect.width,rect.height-bh)
        pygame.draw.rect(self.screen,(220,220,218),wr,border_radius=6)
        pygame.draw.rect(self.screen,(28,26,24),br2,border_radius=6)
        pygame.draw.rect(self.screen,pygame.Color(C_BORDER),rect,width=1,border_radius=6)
        if abs(cp)>25 or self.eval_mate is not None:
            txt=f"M{abs(self.eval_mate)}" if self.eval_mate is not None else f"{'+'if cp>0 else ''}{cp/100:.1f}"
            tc2="#222222" if ratio>0.6 else "#DDDDDD"
            ts4=self.f_xs.render(txt,True,pygame.Color(tc2))
            ty=clamp(wr.top-2 if not bb else br2.top-2,rect.y+2,rect.bottom-14)
            self.screen.blit(ts4,ts4.get_rect(centerx=rect.centerx,y=ty))

    # ── Board ─────────────────────────────────────────────────────────────────
    def _draw_board(self, db):
        br=self.layout["board"]; sq=self.layout["sq"]; th=self.theme; bb=self._black_bot()
        files="abcdefgh"
        # Border
        pygame.draw.rect(self.screen,pygame.Color(C_BORDER),br.inflate(6,6),border_radius=4)
        # Last-move highlights
        hl=set()
        if self.anim and self.view_off==0: hl.add(self.anim["move"].from_square); hl.add(self.anim["move"].to_square)
        elif db.move_stack: lm=db.peek(); hl.add(lm.from_square); hl.add(lm.to_square)
        pm_hl=set()
        if self.premove is not None:
            pm_hl.add(self.premove.from_square); pm_hl.add(self.premove.to_square)
        anim_from=set()
        if self.anim and self.view_off==0:
            for a in self.anim["pieces"]: anim_from.add(a["from"])

        for row in range(8):
            for col in range(8):
                f=(7-col) if bb else col; r=row if bb else (7-row)
                square=chess.square(f,r)
                rect=pygame.Rect(br.x+col*sq, br.y+row*sq, sq, sq)
                is_lt=(f+r)%2==1
                pygame.draw.rect(self.screen,pygame.Color(th["lt"] if is_lt else th["dk"]),rect)
                # Highlights
                if square in hl:
                    s=pygame.Surface((sq,sq),pygame.SRCALPHA); s.fill((244,211,94,85)); self.screen.blit(s,rect.topleft)
                if square in pm_hl:
                    s=pygame.Surface((sq,sq),pygame.SRCALPHA); s.fill((225,85,84,130)); self.screen.blit(s,rect.topleft)
                    pygame.draw.rect(self.screen,pygame.Color(C_RED),rect,width=2)
                if self.sel_sq==square:
                    s=pygame.Surface((sq,sq),pygame.SRCALPHA); s.fill((244,211,94,120)); self.screen.blit(s,rect.topleft)
                    pygame.draw.rect(self.screen,pygame.Color(th["hl"]),rect,width=3)
                if square in self.legal_tgts and db.turn == self.player_color:
                    ds=pygame.Surface((sq,sq),pygame.SRCALPHA)
                    if db.piece_at(square): pygame.draw.circle(ds,(20,20,20,100),(sq//2,sq//2),sq//2,6)
                    else:                   pygame.draw.circle(ds,(20,20,20,75),(sq//2,sq//2),sq//7)
                    self.screen.blit(ds,rect.topleft)
                # Check glow
                if db.is_check() and square==db.king(db.turn):
                    gs=pygame.Surface((sq,sq),pygame.SRCALPHA)
                    gs.fill((235,80,70,145)); pygame.draw.rect(gs,(180,30,20,200),gs.get_rect(),width=3)
                    self.screen.blit(gs,rect.topleft)
                # Coordinates
                cc=pygame.Color(th["dk"]) if is_lt else pygame.Color(th["lt"])
                if col==0: rs=self.f_coord.render(str(r+1),True,cc); self.screen.blit(rs,(rect.x+3,rect.y+2))
                if row==7: fs=self.f_coord.render(files[f],True,cc); self.screen.blit(fs,(rect.right-fs.get_width()-3,rect.bottom-fs.get_height()-2))

        # Static pieces (skip piece being dragged)
        for square,piece in db.piece_map().items():
            if self.view_off==0 and square in anim_from: continue
            # Skip the dragged piece's source square while dragging
            if self.drag_confirmed and square==self.drag_sq: continue
            r2=self.sq_to_rect(square); self._piece(piece,r2.x,r2.y,sq,sq)

        # Animated pieces
        if self.anim and self.view_off==0:
            now=pygame.time.get_ticks()
            prog=clamp((now-self.anim["start"])/self.anim["dur"],0,1)
            prog=1-(1-prog)**2
            for a in self.anim["pieces"]:
                sr=self.sq_to_rect(a["from"]); er=self.sq_to_rect(a["to"])
                cx=sr.x+(er.x-sr.x)*prog; cy=sr.y+(er.y-sr.y)*prog
                self._piece(a["piece"],cx,cy,sq,sq)

        # ── DRAG PIECE at cursor ──────────────────────────────────────────────
        if self.drag_confirmed and self.drag_piece is not None:
            hs=sq//2  # half square — center piece on cursor
            self._piece(self.drag_piece, self.drag_pos[0]-hs, self.drag_pos[1]-hs, sq, sq)

    # ── Promotion overlay ─────────────────────────────────────────────────────
    def _draw_promo(self):
        br=self.layout["board"]
        dim=pygame.Surface((br.width,br.height),pygame.SRCALPHA); dim.fill((0,0,0,155))
        self.screen.blit(dim,br.topleft)
        mouse=pygame.mouse.get_pos()
        for rect,pt in self.promo_rects:
            bg="white" if rect.collidepoint(mouse) else "#F0F0F0"
            self._rr(bg,rect,6); self._rb(C_BORDER,rect,6,2)
            self._piece(chess.Piece(pt,self.player_color),rect.x,rect.y,rect.width,rect.height)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _draw_sidebar(self, db):
        rect=self.layout["sidebar"]; self._rr(C_SURFACE,rect,16); self._sb_btns={}
        x=rect.x+14; y=rect.y+14; w=rect.width-28; mouse=pygame.mouse.get_pos()
        # Premium Opening Book Card - Always visible to keep layout consistent and show opening status from move 0
        banner_r = pygame.Rect(x, y, w, 46)
        if self.opening:
            self._rr("#2B2519", banner_r, 8)
            self._rb(C_GOLD, banner_r, 8, 1)
            # Small book label in gold
            lbl = self.f_xs.render("⚡ BOOK OPENING", True, pygame.Color(C_GOLD))
            self.screen.blit(lbl, (x + 8, y + 4))
            # Main opening name in white
            op = self.f_body.render(self.opening, True, pygame.Color(C_WHITE))
            self.screen.blit(op, (x + 8, y + 22))
        else:
            self._rr(C_CARD, banner_r, 8)
            self._rb(C_BORDER, banner_r, 8, 1)
            # Small book label in muted gray
            lbl = self.f_xs.render("⚡ BOOK OPENING", True, pygame.Color(C_MUTED))
            self.screen.blit(lbl, (x + 8, y + 4))
            # Default text in muted gray
            op = self.f_body.render("Standard Play", True, pygame.Color(C_MUTED))
            self.screen.blit(op, (x + 8, y + 22))
        y += banner_r.height + 10
        # Info line
        ai=self._ai_params(); tm=TIME_MODES[self.timing_idx]
        info=self.f_xs.render(f"vs Stockfish · {ai['name']} · Elo {ai['elo']} · {tm['name']}",True,pygame.Color(C_MUTED))
        self.screen.blit(info,(x,y)); y+=18
        # View offset
        if self.view_off<0:
            vo=self.f_xs.render(f"History ({-self.view_off} back)",True,pygame.Color(C_BLUE))
            self.screen.blit(vo,(x,y)); y+=16
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(x,y),(x+w,y)); y+=10
        # Status
        st=self._status(db)
        sc=C_GREEN if "Win" in st else (C_RED if "Lose" in st.lower() or "lose" in st.lower() else C_GRAY)
        self.screen.blit(self.f_sm.render(st,True,pygame.Color(sc)),(x,y)); y+=20
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(x,y),(x+w,y)); y+=10
        # Move log
        ml=self.f_sm.render("Moves",True,pygame.Color(C_GRAY)); self.screen.blit(ml,(x,y)); y+=20
        btn_h=32; btn_zone=btn_h+14
        log_h=rect.bottom-y-btn_zone-14
        log_r=pygame.Rect(x,y,w,max(60,log_h))
        self._draw_log(log_r,db); y=log_r.bottom+8
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(x,y),(x+w,y)); y+=8
        # Buttons (Draw removed, Flip and Resign scaled beautifully to 2 slots)
        bw=(w-6)//2
        btns=[("flip","Flip",C_GRAY,C_CARD),("resign","Resign",C_RED,"#3D1A1A")]
        for i,(key,lbl,tc,bg) in enumerate(btns):
            bx=x+i*(bw+6); br3=pygame.Rect(bx,y,bw,btn_h)
            self._sb_btns[key]=br3
            self._rr(C_CARD_HOV if br3.collidepoint(mouse) else bg,br3,6)
            self._rb(C_BORDER,br3,6,1)
            self.screen.blit(self.f_xs.render(lbl,True,pygame.Color(tc)),
                             self.f_xs.render(lbl,True,pygame.Color(tc)).get_rect(center=br3.center))
        # Tip
        tip=self.f_xs.render("",True,pygame.Color(C_MUTED))
        self.screen.blit(tip,tip.get_rect(centerx=rect.centerx,y=y+btn_h+4))

    def _status(self, db):
        if self.result_msg:      return f"{self.result_msg} {self.result_reason}"
        if self.view_off<0:      return "Reviewing history"
        if db.turn==self.ai_color:
            return "Stockfish is thinking…"
        if db.is_check():
            return "Your king is in check!"
        return "Your turn"

    def _draw_log(self, rect, db):
        self._rr(C_CARD,rect,8)
        pairs=[(i//2+1,self.san_moves[i],self.san_moves[i+1] if i+1<len(self.san_moves) else "")
               for i in range(0,len(self.san_moves),2)]
        lh=22; vis=max(1,(rect.height-8)//lh)
        ms=max(0,len(pairs)-vis); self.log_scroll=clamp(self.log_scroll,0,ms)
        start=max(0,len(pairs)-vis-self.log_scroll); shown=pairs[start:start+vis]
        cur=len(self.board.move_stack)-1+self.view_off; mouse=pygame.mouse.get_pos()
        clip=self.screen.get_clip(); self.screen.set_clip(rect.inflate(-4,-4))
        y=rect.y+6
        for num,wm,bm in shown:
            base=(num-1)*2
            ns=self.f_xs.render(f"{num}.",True,pygame.Color(C_MUTED)); self.screen.blit(ns,(rect.x+6,y+3))
            wr=pygame.Rect(rect.x+34,y,76,lh-2)
            if base==cur:
                self._rr("#363531",wr,4)
                self._rb(C_GREEN,wr,4,1)
                wc2=C_WHITE
            elif wr.collidepoint(mouse): self._rr(C_CARD_HOV,wr,4); wc2=C_WHITE
            else: wc2=C_GRAY
            self.screen.blit(self.f_sm.render(wm,True,pygame.Color(wc2)),(wr.x+4,y+3))
            if bm:
                br4=pygame.Rect(rect.x+116,y,76,lh-2)
                if base+1==cur:
                    self._rr("#363531",br4,4)
                    self._rb(C_GREEN,br4,4,1)
                    bc6=C_WHITE
                elif br4.collidepoint(mouse): self._rr(C_CARD_HOV,br4,4); bc6=C_WHITE
                else: bc6=C_GRAY
                self.screen.blit(self.f_sm.render(bm,True,pygame.Color(bc6)),(br4.x+4,y+3))
            y+=lh
        self.screen.set_clip(clip)
        if not pairs:
            e=self.f_sm.render("No moves yet",True,pygame.Color(C_MUTED)); self.screen.blit(e,e.get_rect(center=rect.center))

    # ═════════════════════════════════════════════════════════════════════════
    # GAME OVER
    # ═════════════════════════════════════════════════════════════════════════
    def _draw_over(self):
        w,h=self.layout["w"],self.layout["h"]
        ov=pygame.Surface((w,h),pygame.SRCALPHA); ov.fill((0,0,0,165)); self.screen.blit(ov,(0,0))
        pw,ph=440,340; px,py=w//2-pw//2,h//2-ph//2
        panel=pygame.Rect(px,py,pw,ph); self._over_btns={}
        self._rr(C_CARD,panel,22); self._rb(C_BORDER,panel,22,2)
        is_win=self.result_score==1.0; is_draw=self.result_score==0.5
        col_s=C_GREEN if is_win else (C_GOLD if is_draw else C_RED)
        self._rr(col_s,pygame.Rect(px,py,pw,6),3)
        pygame.draw.line(self.screen,pygame.Color(col_s),(px+20,py+64),(px+pw-20,py+64),2)
        rs=self.f_title.render(self.result_msg,True,pygame.Color(col_s))
        self.screen.blit(rs,rs.get_rect(centerx=panel.centerx,y=py+14))
        rrs=self.f_body.render(self.result_reason,True,pygame.Color(C_GRAY))
        self.screen.blit(rrs,rrs.get_rect(centerx=panel.centerx,y=py+68))
        # ELO change
        sign="+" if self.elo_change>=0 else ""
        ec=self.f_elo.render(f"{sign}{self.elo_change}",True,pygame.Color(C_GREEN if self.elo_change>=0 else C_RED))
        self.screen.blit(ec,ec.get_rect(centerx=panel.centerx-60,y=py+102))
        el=self.f_xs.render("Rating Change",True,pygame.Color(C_MUTED))
        self.screen.blit(el,el.get_rect(centerx=panel.centerx-60,y=py+132))
        ne=self.f_elo.render(str(self.new_elo),True,pygame.Color(C_GOLD))
        self.screen.blit(ne,ne.get_rect(centerx=panel.centerx+80,y=py+102))
        nl=self.f_xs.render("New Rating",True,pygame.Color(C_MUTED))
        self.screen.blit(nl,nl.get_rect(centerx=panel.centerx+80,y=py+132))
        # Stats
        stats=[(str(self.pdata["wins"]),"Wins",C_GREEN),(str(self.pdata["draws"]),"Draws",C_GRAY),(str(self.pdata["losses"]),"Losses",C_RED)]
        sy=py+170
        for i,(val,lbl,c) in enumerate(stats):
            sx=panel.centerx-80+i*80
            vs=self.f_head.render(val,True,pygame.Color(c)); ls=self.f_xs.render(lbl,True,pygame.Color(C_MUTED))
            self.screen.blit(vs,vs.get_rect(centerx=sx,y=sy)); self.screen.blit(ls,ls.get_rect(centerx=sx,y=sy+28))
        # Buttons
        mouse=pygame.mouse.get_pos(); btn_y=py+ph-56; bw2=120; bh2=40
        total2=2*bw2+8; bstart=panel.centerx-total2//2
        for i,(key,lbl,bg2) in enumerate([("home","Home",C_SURFACE),("new","New Game",C_GREEN)]):
            bx=bstart+i*(bw2+8); br5=pygame.Rect(bx,btn_y,bw2,bh2); self._over_btns[key]=br5
            hov=br5.collidepoint(mouse)
            c2=C_CARD_HOV if (hov and bg2!=C_GREEN) else ("#4A8A28" if hov else bg2)
            self._rr(c2,br5,8)
            if bg2!=C_GREEN: self._rb(C_BORDER,br5,8,1)
            ts5=self.f_btn.render(lbl,True,pygame.Color(C_WHITE if bg2==C_GREEN else C_GRAY))
            self.screen.blit(ts5,ts5.get_rect(center=br5.center))
        hn=self.f_xs.render("← → to review moves",True,pygame.Color(C_MUTED))
        self.screen.blit(hn,hn.get_rect(centerx=panel.centerx,y=py+ph-14))

    # ═════════════════════════════════════════════════════════════════════════
    # SETTINGS OVERLAY
    # ═════════════════════════════════════════════════════════════════════════
    def _draw_settings(self):
        w,h=self.layout["w"],self.layout["h"]
        ov=pygame.Surface((w,h),pygame.SRCALPHA); ov.fill((0,0,0,175)); self.screen.blit(ov,(0,0))
        pw,ph=480,430; px,py=w//2-pw//2,h//2-ph//2
        panel=pygame.Rect(px,py,pw,ph); self._settings_rects={}; mouse=pygame.mouse.get_pos()
        self._rr(C_CARD,panel,22); self._rb(C_BORDER,panel,22,2)
        self._rr(C_GREEN,pygame.Rect(px,py,pw,5),3)
        hs=self.f_head.render("Settings",True,pygame.Color(C_WHITE)); self.screen.blit(hs,(px+24,py+18))
        # Close
        cr=pygame.Rect(px+pw-46,py+14,30,30); self._settings_rects["close"]=cr
        self._rr(C_CARD_HOV if cr.collidepoint(mouse) else C_SURFACE,cr,6)
        xs=self.f_body.render("x",True,pygame.Color(C_GRAY)); self.screen.blit(xs,xs.get_rect(center=cr.center))
        y=py+60; pad=24
        # Board themes
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(px+pad,y),(px+pw-pad,y)); y+=14
        self.screen.blit(self.f_sub.render("Board Theme",True,pygame.Color(C_WHITE)),(px+pad,y)); y+=32
        tw,th2,tg=74,52,10
        for i,tname in enumerate(THEMES):
            tr=pygame.Rect(px+pad+i*(tw+tg),y,tw,th2); self._settings_rects[f"theme_{tname}"]=tr
            sel=(self.theme_name==tname); bc7=C_GREEN if sel else (C_BORDER if tr.collidepoint(mouse) else "#2A2825")
            self._rr("#2A2825",tr,8); self._rb(bc7,tr,8,2)
            # 2x2 board preview sized to fit perfectly within 74x52 without overflow
            grid_sz = 36
            mq = grid_sz // 2
            bx = tr.x + (tw - grid_sz) // 2
            by = tr.y + (th2 - grid_sz) // 2
            for r2 in range(2):
                for c2 in range(2):
                    mc=THEMES[tname]["lt"] if (r2+c2)%2==1 else THEMES[tname]["dk"]
                    pygame.draw.rect(self.screen,pygame.Color(mc),(bx+c2*mq,by+r2*mq,mq,mq))
            nts=self.f_xs.render(tname,True,pygame.Color(C_GRAY)); self.screen.blit(nts,nts.get_rect(centerx=tr.centerx,y=tr.bottom+4))
        y+=th2+24
        # Sound
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(px+pad,y),(px+pw-pad,y)); y+=14
        self.screen.blit(self.f_sub.render("Sound",True,pygame.Color(C_WHITE)),(px+pad,y))
        tr2=pygame.Rect(px+pw-pad-54,y-2,50,26); self._settings_rects["sound"]=tr2
        self._rr(C_GREEN if self.sound.enabled else C_SURFACE,tr2,13)
        kx=tr2.right-14 if self.sound.enabled else tr2.x+4
        pygame.draw.circle(self.screen,(255,255,255),(kx,tr2.centery),9)
        y+=42
        # Stats
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(px+pad,y),(px+pw-pad,y)); y+=14
        self.screen.blit(self.f_sub.render("Stats",True,pygame.Color(C_WHITE)),(px+pad,y)); y+=28
        si=self.f_sm.render(f"Elo: {self.pdata['elo']}  Peak: {self.pdata['peak_elo']}  Games: {self.pdata['games_played']}",True,pygame.Color(C_MUTED))
        self.screen.blit(si,(px+pad,y)); y+=22
        si2=self.f_sm.render(f"W{self.pdata['wins']}  D{self.pdata['draws']}  L{self.pdata['losses']}",True,pygame.Color(C_MUTED))
        self.screen.blit(si2,(px+pad,y)); y+=28
        rr=pygame.Rect(px+pad,y,140,30); self._settings_rects["reset"]=rr
        self._rr(C_CARD_HOV if rr.collidepoint(mouse) else C_SURFACE,rr,6)
        self._rb(C_RED,rr,6,1)
        self.screen.blit(self.f_sm.render("Reset All Stats",True,pygame.Color(C_RED)),self.f_sm.render("Reset All Stats",True,pygame.Color(C_RED)).get_rect(center=rr.center))
        # SF status
        y+=44
        sf_s=self.f_sm.render(f"Stockfish: {'Active ✓' if self.engine.use_sf else 'Not found — built-in AI'}",True,pygame.Color(C_GREEN if self.engine.use_sf else C_GOLD))
        self.screen.blit(sf_s,(px+pad,y))
        esc_s=self.f_xs.render("ESC or x to close",True,pygame.Color(C_MUTED))
        self.screen.blit(esc_s,esc_s.get_rect(centerx=panel.centerx,y=panel.bottom-18))

    # ═════════════════════════════════════════════════════════════════════════
    # SHARED UI
    # ═════════════════════════════════════════════════════════════════════════
    def _nav_bar(self, title="Chess Master"):
        w=self.layout["w"]; nr=pygame.Rect(0,0,w,NAV_H)
        pygame.draw.rect(self.screen,pygame.Color(C_SURFACE),nr)
        pygame.draw.line(self.screen,pygame.Color(C_BORDER),(0,NAV_H-1),(w,NAV_H-1))
        # Logo dot
        pygame.draw.circle(self.screen,pygame.Color(C_GREEN),(PAD+12,NAV_H//2),8)
        ts=self.f_head.render(title,True,pygame.Color(C_WHITE))
        self.screen.blit(ts,(PAD+28,NAV_H//2-ts.get_height()//2))
        # Elo pill
        ep=self.f_sm.render(f"ELO {self.pdata['elo']}",True,pygame.Color(C_GOLD))
        self.screen.blit(ep,(self._gear_rect().x-ep.get_width()-12,NAV_H//2-ep.get_height()//2))
        # Gear
        gr=self._gear_rect(); mouse=pygame.mouse.get_pos()
        bg_col = C_CARD_HOV if gr.collidepoint(mouse) else C_SURFACE
        self._rr(bg_col,gr,6)
        self._draw_gear_icon(gr, C_GRAY, bg_col)

    def _draw_gear_icon(self, rect, color, active_bg):
        cx, cy = rect.center
        # Draw teeth spokes
        for i in range(8):
            angle = i * (math.pi / 4)
            x1 = cx + math.cos(angle) * 6
            y1 = cy + math.sin(angle) * 6
            x2 = cx + math.cos(angle) * 11
            y2 = cy + math.sin(angle) * 11
            pygame.draw.line(self.screen, pygame.Color(color), (int(x1), int(y1)), (int(x2), int(y2)), 3)
        # Hub
        pygame.draw.circle(self.screen, pygame.Color(color), (cx, cy), 7)
        # Cutout
        pygame.draw.circle(self.screen, pygame.Color(active_bg), (cx, cy), 3)

    def _gear_rect(self):
        return pygame.Rect(self.layout["w"]-52,(NAV_H-32)//2,32,32)

    def _chess_bg(self):
        w,h=self.layout["w"],self.layout["h"]; sq=50
        s=pygame.Surface((w,h),pygame.SRCALPHA)
        for r in range(h//sq+1):
            for c in range(w//sq+1):
                if(r+c)%2==0: pygame.draw.rect(s,(255,255,255,7),(c*sq,r*sq,sq,sq))
        self.screen.blit(s,(0,0))

    # ─────────────────────────────────────────────────────────────────────────
    # PIECE DRAWING
    # ─────────────────────────────────────────────────────────────────────────
    def _piece(self, piece, x, y, w, h):
        if piece in self.piece_imgs:
            key=(piece,int(w),int(h))
            if key not in self._img_cache:
                self._img_cache[key]=pygame.transform.smoothscale(self.piece_imgs[piece],(int(w),int(h)))
            img=self._img_cache[key]
            self.screen.blit(img,img.get_rect(center=(int(x+w/2),int(y+h/2)))); return
        glyph=UGLYPH.get(piece,"?"); mc="#F8F5F2" if piece.color==chess.WHITE else "#5A6270"
        oc="#C98D5B" if piece.color==chess.WHITE else "#303641"
        font=self.f_piece if w>30 else(self.f_piece_sm if w>20 else self.f_piece_xs)
        cx2,cy2=int(x+w/2),int(y+h/2)
        for ox,oy in((-1,0),(1,0),(0,-1),(0,1)):
            s=font.render(glyph,True,pygame.Color(oc)); self.screen.blit(s,s.get_rect(center=(cx2+ox,cy2+oy)))
        s=font.render(glyph,True,pygame.Color(mc)); self.screen.blit(s,s.get_rect(center=(cx2,cy2-1)))

    def _draw_vector_crown(self, x, y, sz, is_white, selected):
        fill_color = pygame.Color("#FFFFFF") if is_white else pygame.Color("#2A2621")
        stroke_color = pygame.Color("#81B64C" if selected else ("#A5A39F" if is_white else "#85837F"))
        
        pad = sz * 0.1
        cx = int(x + sz / 2)
        cy = int(y + sz / 2)
        w = sz - 2 * pad
        h = sz - 2 * pad
        rx = int(x + pad)
        ry = int(y + pad)
        
        pts = [
            (rx, int(ry + h)),
            (rx, int(ry + h * 0.35)),
            (int(rx + w * 0.25), int(ry + h * 0.6)),
            (cx, int(ry + h * 0.15)),
            (int(rx + w * 0.75), int(ry + h * 0.6)),
            (int(rx + w), int(ry + h * 0.35)),
            (int(rx + w), int(ry + h))
        ]
        
        pygame.draw.polygon(self.screen, fill_color, pts)
        
        # Base band
        base_r = pygame.Rect(rx - 1, int(ry + h - 2), int(w + 2), 3)
        pygame.draw.rect(self.screen, stroke_color, base_r)
        
        # Outline
        pygame.draw.polygon(self.screen, stroke_color, pts, 2)
        
        # Cross on center peak
        pygame.draw.line(self.screen, stroke_color, (cx, int(ry + h * 0.03)), (cx, int(ry + h * 0.15)), 2)
        pygame.draw.line(self.screen, stroke_color, (cx - 3, int(ry + h * 0.08)), (cx + 3, int(ry + h * 0.08)), 2)

    def _draw_vector_random_icon(self, x, y, sz, selected):
        cx = int(x + sz / 2)
        cy = int(y + sz / 2)
        r = sz / 2 - 2
        
        left_pts = []
        right_pts = []
        steps = 16
        for i in range(steps + 1):
            angle = math.pi / 2 + (i / steps) * math.pi
            px = int(cx + math.cos(angle) * r)
            py = int(cy + math.sin(angle) * r)
            left_pts.append((px, py))
        left_pts.append((cx, cy))
        
        for i in range(steps + 1):
            angle = -math.pi / 2 + (i / steps) * math.pi
            px = int(cx + math.cos(angle) * r)
            py = int(cy + math.sin(angle) * r)
            right_pts.append((px, py))
        right_pts.append((cx, cy))
        
        pygame.draw.polygon(self.screen, pygame.Color("#FFFFFF"), left_pts)
        pygame.draw.polygon(self.screen, pygame.Color("#2A2621"), right_pts)
        
        stroke_color = pygame.Color("#81B64C" if selected else "#A5A39F")
        pygame.draw.circle(self.screen, stroke_color, (cx, cy), int(r), 2)
        pygame.draw.line(self.screen, stroke_color, (cx, int(cy - r)), (cx, int(cy + r)), 1)
        
        qs_color = pygame.Color("#81B64C" if selected else "#FFFFFF")
        qs = self.f_xs.render("?", True, qs_color)
        self.screen.blit(qs, qs.get_rect(center=(cx, cy)))

    # ─────────────────────────────────────────────────────────────────────────
    # DRAW HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _rr(self, color, rect, radius):
        try: pygame.draw.rect(self.screen,pygame.Color(color) if isinstance(color,str) else color,rect,border_radius=radius)
        except Exception: pygame.draw.rect(self.screen,(40,40,40),rect)

    def _rb(self, color, rect, radius, width):
        try: pygame.draw.rect(self.screen,pygame.Color(color) if isinstance(color,str) else color,rect,width=width,border_radius=radius)
        except Exception: pass

    def _fmt(self, secs):
        if secs==float("inf") or secs>36000: return "INF"
        if secs<=0: return "0:00"
        if secs<20:  return f"{secs:.1f}"
        return f"{int(secs)//60}:{int(secs)%60:02d}"

# ──────────────────────────────────────────────────────────────────────────────
# Convenience constants for hover colour (used in _draw_setup)
C_CARD_HOV = "#302D29"

def main():
    import traceback
    try:
        ChessApp().run()
    except Exception as e:
        try:
            with open("crash_log.txt", "w", encoding="utf-8") as f:
                traceback.print_exc(file=f)
        except:
            pass
        raise e

if __name__=="__main__":
    main()
