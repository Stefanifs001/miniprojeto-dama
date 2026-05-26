import streamlit as st
import random
import time
import base64

# =========================================
# CONFIG E TÍTULO
# =========================================
st.set_page_config(
    page_title="Damas Clássico",
    layout="centered"
)

# Imagens de textura (convertidas para Base64 para rodar em qualquer lugar)
# Você pode substituir por URLs reais ou caminhos locais se preferir.
MOLDURA_WWOOD = "https://i.imgur.com/8Qp4R7Z.jpg" # Textura de madeira escura da moldura
CASA_ESCURA_WOOD = "https://i.imgur.com/uR2N8e1.jpg" # Textura de madeira média para casas escuras
CASA_CLARA_WOOD = "https://i.imgur.com/Y3uA7L9.jpg" # Textura de madeira clara para casas claras

# =========================================
# CSS FOTOREALISTA DE DAMAS
# =========================================
st.markdown(f"""
<style>
/* Fundo do App simulando uma mesa de madeira muito escura */
html, body, [class*="css"] {{
    background: radial-gradient(circle, #20130c, #0f0a07);
    font-family: 'Garamond', serif;
}}

.title {{
    text-align: center;
    color: #f3e5ab;
    font-size: 55px;
    font-weight: bold;
    margin-bottom: 25px;
    text-shadow: 3px 3px 6px #000;
    letter-spacing: 2px;
}}

.turn {{
    text-align:center;
    color:#f3e5ab;
    font-size:22px;
    margin-bottom:25px;
    font-weight: bold;
    background-color: rgba(0,0,0,0.5);
    padding: 10px;
    border-radius: 10px;
}}

/* Força o espaçamento entre colunas do Streamlit a ser ZERO absoluto */
[data-testid="column"] {{
    padding: 0px !important;
    margin: 0px !important;
}}
div.stColumns {{
    gap: 0px !important;
    width: 600px; /* Largura fixa para manter proporção */
    margin: 0 auto; /* Centraliza o tabuleiro */
}}

/* Estilização geral dos botões do tabuleiro para virarem "Casas" */
.stButton > button {{
    width: 100% !important;
    aspect-ratio: 1 / 1 !important; /* Força os botões a serem perfeitamente quadrados */
    height: auto !important;
    margin: 0 !important;
    padding: 0 !important;
    border-radius: 0px !important; /* Tira o arredondamento padrão */
    border: none !important;
    font-size: 40px !important; /* Aumenta o tamanho da peça (emoji) dentro da casa */
    box-shadow: none !important;
    transition: none !important;
}}

/* Hover suave nas casas */
.stButton > button:hover {{
    opacity: 0.95;
    box-shadow: inset 0px 0px 10px rgba(255,255,255,0.2) !important;
}}

/* Centraliza o container principal */
.block-container {{
    max-width: 650px;
    padding-top: 30px;
}}
</style>
""", unsafe_allow_html=True)

# =========================================
# LÓGICA DO TABULEIRO
# =========================================
def criar_tabuleiro():
    tabuleiro = []
    for linha in range(8):
        row = []
        for coluna in range(8):
            if linha < 3 and (linha + coluna) % 2 == 1:
                row.append("red") # IA / Escuras
            elif linha > 4 and (linha + coluna) % 2 == 1:
                row.append("white") # Jogador / Claras
            else:
                row.append(None)
        tabuleiro.append(row)
    return tabuleiro

if "board" not in st.session_state:
    st.session_state.board = criar_tabuleiro()
if "turn" not in st.session_state:
    st.session_state.turn = "white"
if "selected" not in st.session_state:
    st.session_state.selected = None
if "mode" not in st.session_state:
    st.session_state.mode = None

# =========================================
# FUNÇÕES AUXILIARES DE JOGO
# =========================================
def dentro(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def eh_dama(piece):
    return piece and "king" in piece

def inimigo(piece, target):
    if not piece or not target:
        return False
    if "white" in piece:
        return "red" in target
    return "white" in target

def promover(r, c):
    piece = st.session_state.board[r][c]
    if piece == "white" and r == 0:
        st.session_state.board[r][c] = "white-king"
    if piece == "red" and r == 7:
        st.session_state.board[r][c] = "red-king"

def mover(sr, sc, dr, dc):
    st.session_state.board[dr][dc] = st.session_state.board[sr][sc]
    st.session_state.board[sr][sc] = None
    promover(dr, dc)

def capturas_possiveis(r, c):
    board = st.session_state.board
    piece = board[r][c]
    if not piece:
        return []
    capturas = []
    direcoes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    if eh_dama(piece):
        for dr, dc in direcoes:
            rr, cc = r + dr, c + dc
            enemy = None
            while dentro(rr, cc):
                atual = board[rr][cc]
                if atual:
                    if inimigo(piece, atual) and not enemy:
                        enemy = (rr, cc)
                    else:
                        break
                elif enemy:
                    capturas.append({"destino": (rr, cc), "enemy": enemy})
                rr += dr
                cc += dc
    else:
        for dr, dc in direcoes:
            mr, mc = r + dr, c + dc
            lr, lc = r + dr * 2, c + dc * 2
            if dentro(lr, lc):
                meio = board[mr][mc]
                if meio and inimigo(piece, meio) and not board[lr][lc]:
                    capturas.append({"destino": (lr, lc), "enemy": (mr, mc)})
    return capturas

def jogador_tem_captura(color):
    board = st.session_state.board
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and color in piece:
                if capturas_possiveis(r, c):
                    return True
    return False

def jogada_ia():
    board = st.session_state.board
    capturas = []
    movimentos = []

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and "red" in piece:
                caps = capturas_possiveis(r, c)
                for cap in caps:
                    capturas.append({"from": (r, c), "to": cap["destino"], "enemy": cap["enemy"]})
                direcoes = [(1, 1), (1, -1)]
                if eh_dama(piece):
                    direcoes += [(-1, 1), (-1, -1)]
                for dr, dc in direcoes:
                    nr, nc = r + dr, c + dc
                    if dentro(nr, nc) and not board[nr][nc]:
                        movimentos.append({"from": (r, c), "to": (nr, nc)})

    if capturas:
        jogada = random.choice(capturas)
        mover(jogada["from"][0], jogada["from"][1], jogada["to"][0], jogada["to"][1])
        er, ec = jogada["enemy"]
        board[er][ec] = None
    elif movimentos:
        jogada = random.choice(movimentos)
        mover(jogada["from"][0], jogada["from"][1], jogada["to"][0], jogada["to"][1])
    st.session_state.turn = "white"

# Execução da IA antes de desenhar a tela
if st.session_state.mode == "pve" and st.session_state.turn == "red":
    with st.spinner("Vez da IA (Vermelhas)..."):
        time.sleep(0.6) # Pequeno delay pra "pensar"
        jogada_ia()
    st.rerun()

# =========================================
# MENU E TÍTULO
# =========================================
st.markdown('<div class="title">DAMAS CLÁSSICO</div>', unsafe_allow_html=True)

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    if st.button("🤖 VS IA"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.session_state.mode = "pve"
        st.rerun()
with col_m2:
    if st.button("👥 2 PLAYERS"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.session_state.mode = "pvp"
        st.rerun()
with col_m3:
    if st.button("🔄 REINICIAR"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.rerun()

# =========================================
# RENDERIZAÇÃO DO TABULEIRO FOTOREALISTA
# =========================================
if st.session_state.mode:
    texto = "Você: Brancas | IA: Vermelhas" if st.session_state.mode == "pve" else "Modo: Local (2 Jogadores)"
    st.markdown(f'<div class="turn">{texto} <br> Vez de jogar: <span style="color:{"#f3e5ab" if st.session_state.turn == "white" else "#cc0000"}">{"BRANCAS" if st.session_state.turn == "white" else "VERMELHAS"}</span></div>', unsafe_allow_html=True)

    board = st.session_state.board

    # Injeta a Moldura de Madeira ao redor do Tabuleiro
    st.markdown(f"""
        <style>
        div.stColumns {{
            background-image: url({MOLDURA_WWOOD});
            background-size: cover;
            border: 15px solid transparent; /* Cria o espaço da moldura */
            border-image: url({MOLDURA_WWOOD}) 30 round; /* Aplica a textura na borda */
            border-radius: 5px;
            box-shadow: 5px 5px 20px rgba(0,0,0,0.8);
        }}
        </style>
    """, unsafe_allow_html=True)

    # Renderiza as linhas e colunas (o tabuleiro em si)
    for r in range(8):
        cols = st.columns(8)
        for c in range(8):
            piece = board[r][c]
            
            # Definição das Peças em Emojis fotorealistas ( círculos 3D)
            # Brancas/Creme para o jogador, Vermelhas escuras para a IA
            if piece == "white":
                emoji = "⚪" # ⚪
            elif piece == "red":
                emoji = "🔴" # 🔴
            elif piece == "white-king":
                emoji = "👑⚪"
            elif piece == "red-king":
                emoji = "👑🔴"
            else:
                emoji = ""

            # Destaque para a peça selecionada (Brilho suave)
            if st.session_state.selected == (r, c):
                emoji = "✨" + (emoji if emoji else "")

            # Mágica do Design: Injeta a TEXTURA DE MADEIRA REAL nas casas
            textura_casa = CASA_ESCURA_WOOD if (r + c) % 2 == 1 else CASA_CLARA_WOOD
            
            # Injeta o estilo da casa específica usando a chave única do botão
            st.markdown(f"""
                <style>
                button[key="{r}-{c}"] {{
                    background-image: url({textura_casa}) !important;
                    background-size: cover !important;
                    color: white !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            if cols[c].button(emoji or " ", key=f"{r}-{c}"):
                # LÓGICA DE CLIQUE (SELECIONAR)
                if piece and st.session_state.turn in piece:
                    st.session_state.selected = (r, c)
                    st.rerun()

                # LÓGICA DE CLIQUE (MOVER)
                elif st.session_state.selected:
                    sr, sc = st.session_state.selected
                    selected_piece = board[sr][sc]
                    dr, dc = r - sr, c - sc
                    obrigatorio = jogador_tem_captura(st.session_state.turn)

                    # LOGICA DE CAPTURA
                    if obrigatorio:
                        caps = capturas_possiveis(sr, sc)
                        jogou = False
                        for cap in caps:
                            if cap["destino"] == (r, c):
                                mover(sr, sc, r, c)
                                er, ec = cap["enemy"]
                                board[er][ec] = None
                                jogou = True
                                novas = capturas_possiveis(r, c)
                                if novas:
                                    st.session_state.selected = (r, c)
                                else:
                                    st.session_state.selected = None
                                    st.session_state.turn = "red" if st.session_state.turn == "white" else "white"
                                break
                        if jogou:
                            st.rerun()

                    # MOVIMENTO NORMAL
                    else:
                        if not eh_dama(selected_piece):
                            # Movimento de peça normal (só para frente)
                            valido = (
                                "white" in selected_piece and dr == -1 and abs(dc) == 1
                            ) or (
                                "red" in selected_piece and dr == 1 and abs(dc) == 1
                            )
                            if valido and not board[r][c]:
                                mover(sr, sc, r, c)
                                st.session_state.selected = None
                                st.session_state.turn = "red" if st.session_state.turn == "white" else "white"
                                st.rerun()
                        else:
                            # Movimento livre da dama (diagonais livres)
                            if abs(dr) == abs(dc):
                                passo_r = 1 if dr > 0 else -1
                                passo_c = 1 if dc > 0 else -1
                                rr, cc = sr + passo_r, sc + passo_c
                                bloqueado = False
                                while rr != r and cc != c:
                                    if board[rr][cc]:
                                        bloqueado = True
                                        break
                                    rr += passo_r
                                    cc += passo_c
                                if not bloqueado and not board[r][c]:
                                    mover(sr, sc, r, c)
                                    st.session_state.selected = None
                                    st.session_state.turn = "red" if st.session_state.turn == "white" else "white"
                                    st.rerun()
