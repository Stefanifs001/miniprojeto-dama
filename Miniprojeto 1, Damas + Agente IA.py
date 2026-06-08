import streamlit as st
from PIL import Image
import random
import time

st.set_page_config(
    page_title="Damas Clássico 3D",
    layout="wide"
)

# ==================================
# CSS
# ==================================

st.markdown("""
<style>

.stApp{
background:#120805;
}

.menu-container{
position:relative;
max-width:700px;
margin:auto;
}

.hotspot{
position:absolute;
left:23%;
width:54%;
height:7%;
cursor:pointer;
background:transparent;
border:none;
}

.hotspot:hover{
background:rgba(255,200,0,.15);
border-radius:12px;
}

.title{
text-align:center;
color:#F3E5AB;
font-size:55px;
font-weight:bold;
text-shadow:3px 3px 6px #000;
}

.turn{
text-align:center;
color:white;
font-size:22px;
margin-bottom:20px;
}

.square button{
width:100%;
aspect-ratio:1;
font-size:35px;
padding:0;
margin:0;
}

</style>
""", unsafe_allow_html=True)

# ==================================
# TABULEIRO
# ==================================

def criar_tabuleiro():
    board = []

    for r in range(8):
        row = []

        for c in range(8):

            if r < 3 and (r+c)%2:
                row.append("red")

            elif r > 4 and (r+c)%2:
                row.append("white")

            else:
                row.append(None)

        board.append(row)

    return board

# ==================================
# SESSION
# ==================================

if "screen" not in st.session_state:
    st.session_state.screen = "menu"

if "board" not in st.session_state:
    st.session_state.board = criar_tabuleiro()

if "turn" not in st.session_state:
    st.session_state.turn = "white"

if "mode" not in st.session_state:
    st.session_state.mode = None

if "selected" not in st.session_state:
    st.session_state.selected = None

# ==================================
# MENU
# ==================================

if st.session_state.screen == "menu":

    st.markdown("<div class='title'>DAMAS CLÁSSICO</div>", unsafe_allow_html=True)

    img = Image.open("menu.png")

    st.image(img, use_container_width=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        if st.button("🤖 PLAYER VS IA"):
            st.session_state.mode = "pve"
            st.session_state.screen = "game"
            st.rerun()

    with col2:
        if st.button("👥 2 PLAYERS"):
            st.session_state.mode = "pvp"
            st.session_state.screen = "game"
            st.rerun()

    with col3:
        st.stop()

# ==================================
# JOGO
# ==================================

board = st.session_state.board

st.markdown(
    f"<div class='turn'>Vez: {st.session_state.turn.upper()}</div>",
    unsafe_allow_html=True
)

top1,top2,top3 = st.columns(3)

with top1:
    if st.button("🏠 Menu"):
        st.session_state.screen = "menu"
        st.rerun()

with top2:
    if st.button("🔄 Reiniciar"):
        st.session_state.board = criar_tabuleiro()
        st.session_state.turn = "white"
        st.session_state.selected = None
        st.rerun()

with top3:
    st.write("")

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

        if cols[c].button(
            emoji if emoji else " ",
            key=f"{r}-{c}"
        ):
            st.session_state.selected = (r,c)

# ==================================
# IA SIMPLES
# ==================================

def jogada_ia():

    board = st.session_state.board

    movimentos = []

    for r in range(8):

        for c in range(8):

            if board[r][c] == "red":

                for dc in [-1,1]:

                    nr = r + 1
                    nc = c + dc

                    if 0 <= nr < 8 and 0 <= nc < 8:

                        if board[nr][nc] is None:

                            movimentos.append(
                                ((r,c),(nr,nc))
                            )

    if movimentos:

        origem,destino = random.choice(movimentos)

        board[destino[0]][destino[1]] = board[origem[0]][origem[1]]
        board[origem[0]][origem[1]] = None

if (
    st.session_state.mode=="pve"
    and st.session_state.turn=="red"
):

    with st.spinner("IA pensando..."):

        time.sleep(.7)

        jogada_ia()

        st.session_state.turn="white"

        st.rerun()
