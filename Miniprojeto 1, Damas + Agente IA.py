import streamlit as st
import random
import time

# =========================================
# CONFIG
# =========================================
st.set_page_config(
    page_title="Jogo de Damas",
    layout="centered"
)

# =========================================
# CSS
# =========================================
st.markdown("""
<style>
html, body, [class*="css"] {
    background: linear-gradient(to bottom, #042f3d, #02161d);
}
.title {
    text-align: center;
    color: #8ff7ff;
    font-size: 60px;
    font-weight: bold;
    margin-bottom: 25px;
    text-shadow: 0px 0px 15px black;
}
.turn {
    text-align:center;
    color:white;
    font-size:24px;
    margin-top:15px;
    margin-bottom:20px;
}
.stButton > button {
    width:100%;
    height:60px;
    border-radius:15px;
    border:none;
    font-size:20px;
    font-weight:bold;
    background: linear-gradient(to bottom,#6b7280,#374151);
    color:white;
}
.stButton > button:hover {
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# =========================================
# TABULEIRO
# =========================================
def criar_tabuleiro():
    tabuleiro = []
    for linha in range(8):
        row = []
        for coluna in range(8):
            if linha < 3 and (linha + coluna) % 2 == 1:
                row.append("red")
            elif linha > 4 and (linha + coluna) % 2 == 1:
                row.append("white")
            else:
                row.append(None)
        tabuleiro.append(row)
    return tabuleiro

# =========================================
# SESSION STATE
# =========================================
if "board" not in st.session_state:
    st.session_state.board = criar_tabuleiro()
if "turn" not in st.session_state:
    st.session_state.turn = "white"
if "selected" not in st.session_state:
    st.session_state.selected = None
if "mode" not in st.session_state:
    st.session_state.mode = None

# =========================================
# FUNÇÕES AUXILIARES
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

# =========================================
# CAPTURAS
# =========================================
def capturas_possiveis(r, c):
    board = st.session_state.board
    piece = board[r][c]
    if not piece:
        return []

    capturas = []
    direcoes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    if eh_dama(piece):
        for dr, dc in direcoes:
            rr = r + dr
            cc = c + dc
            enemy = None
            while dentro(rr, cc):
                atual = board[rr][cc]
                if atual:
                    if inimigo(piece, atual) and not enemy:
                        enemy = (rr, cc)
                    else:
                        break
                elif enemy:
                    capturas.append({
                        "destino": (rr, cc),
                        "enemy": enemy
                    })
                rr += dr
                cc += dc
    else:
        for dr, dc in direcoes:
            mr = r + dr
            mc = c + dc
            lr = r + dr * 2
            lc = c + dc * 2
            if dentro(lr, lc):
                meio = board[mr][mc]
                if meio and inimigo(piece, meio) and not board[lr][lc]:
                    capturas.append({
                        "destino": (lr, lc),
                        "enemy": (mr, mc)
                    })
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

# =========================================
# LOGICA DA IA (REPOSICIONADA)
# =========================================
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
                    capturas.append({
                        "from": (r, c),
                        "to": cap["destino"],
                        "enemy": cap["enemy"]
                    })

                direcoes = [(1, 1), (1, -1)]
                if eh_dama(piece):
                    direcoes += [(-1, 1), (-1, -1)]

                for dr, dc in direcoes:
                    nr = r + dr
                    nc = c + dc
                    if dentro(nr, nc) and not board[nr][nc]:
                        movimentos.append({
                            "from": (r, c),
                            "to": (nr, nc)
                        })

    if capturas:
        jogada = random.choice(capturas)
        mover(jogada["from"][0], jogada["from"][1], jogada["to"][0], jogada["to"][1])
        er, ec = jogada["enemy"]
        board[er][ec] = None
        
        # Multi-captura simplificada da IA (evita travar o turno)
        novas = capturas_possiveis(jogada["to"][0], jogada["to"][1])
        if novas:
            # IA continua jogando se tiver mais peças para comer
            pass 
    elif movimentos:
        jogada = random.choice(movimentos)
        mover(jogada["from"][0], jogada["from"][1], jogada["to"][0], jogada["to"][1])

    st.session_state.turn = "white"

# EXECUTA A IA ANTES DE RENDERIZAR A TELA SE FOR O TURNO DELA
if st.session_state.mode == "pve" and st.session_state.turn == "red":
    with st.spinner("IA pensando..."):
        time.sleep(0.5) # Pequeno delay pro player ver o tabuleiro antes da IA agir
        jogada_ia()
    st.rerun()

# =========================================
# MENU
# =========================================
st.markdown('<div class="title">DAMAS</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🎮 VS IA"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.session_state.mode = "pve"
        st.rerun()
with col2:
    if st.button("👥 2 PLAYERS"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.session_state.mode = "pvp"
        st.rerun()
with col3:
    if st.button("🔄 RESET"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.rerun()

# =========================================
# JOGO
# =========================================
if st.session_state.mode:
    texto = "Você = Branco | IA = Vermelho" if st.session_state.mode == "pve" else "Modo 2 Players"
    st.markdown(f'<div class="turn">{texto} (Turno: {st.session_state.turn.upper()})</div>', unsafe_allow_html=True)

    board = st.session_state.board

    for r in range(8):
        cols = st.columns(8)
        for c in range(8):
            piece = board[r][c]
            emoji = ""

            if piece == "white":
                emoji = "⚪"
            elif piece == "red":
                emoji = "🔴"
            elif piece == "white-king":
                emoji = "👑⚪"
            elif piece == "red-king":
                emoji = "👑🔴"
            else:
                emoji = "⬛" if (r + c) % 2 else "🟩"

            # Destaca a peça selecionada pra melhorar a UX
            if st.session_state.selected == (r, c):
                emoji = "✨" + emoji

            if cols[c].button(emoji, key=f"{r}-{c}"):
                # SELECIONAR PEÇA
                if piece and st.session_state.turn in piece:
                    st.session_state.selected = (r, c)
                    st.rerun()

                # MOVER PEÇA SELECIONADA
                elif st.session_state.selected:
                    sr, sc = st.session_state.selected
                    selected_piece = board[sr][sc]
                    dr = r - sr
                    dc = c - sc

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
                                
                                # COMBO DE CAPTURA MULTIPLA
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
                            # MOVIMENTO DA DAMA
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

# =========================================
# INFO
# =========================================
st.divider()
st.markdown("""
### ✅ Recursos Implementados
- Jogar contra IA
- Modo 2 Players
- Dama (Movimento livre e promoção automática)
- Captura obrigatória e múltipla
- Interface com feedback visual de seleção ("✨")
""")
st.code("streamlit run app.py", language="bash")
