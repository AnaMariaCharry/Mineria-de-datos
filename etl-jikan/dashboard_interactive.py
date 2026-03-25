#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Dashboard Interactivo Anime",
    page_icon="🎛️",
    layout="wide"
)

st.title("🎛️ Dashboard Interactivo - Anime (Jikan)")

# =========================
# 📂 CARGA DE DATOS
# =========================

if not os.path.exists('data/anime.csv'):
    st.error("❌ No existe data/anime.csv")
    st.stop()

df = pd.read_csv('data/anime.csv')

# Limpieza básica
if 'score' in df.columns:
    df = df.dropna(subset=['score'])

# =========================
# 🎛️ SIDEBAR (FILTROS)
# =========================

st.sidebar.markdown("### 🔧 Controles")

# Tipos
tipos = df['tipo'].dropna().unique() if 'tipo' in df.columns else []
tipos_sel = st.sidebar.multiselect(
    "🎬 Tipo de Anime",
    options=tipos,
    default=list(tipos)
)

# Score
score_min, score_max = st.sidebar.slider(
    "⭐ Rango de Score",
    float(df['score'].min()),
    float(df['score'].max()),
    (float(df['score'].min()), float(df['score'].max()))
)

# Episodios
if 'episodios' in df.columns:
    ep_min, ep_max = st.sidebar.slider(
        "📺 Episodios",
        int(df['episodios'].min()),
        int(df['episodios'].max()),
        (int(df['episodios'].min()), int(df['episodios'].max()))
    )
else:
    ep_min, ep_max = None, None

# =========================
# 🔍 FILTRADO
# =========================

df_filtrado = df[
    (df['score'] >= score_min) &
    (df['score'] <= score_max)
]

if 'tipo' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipos_sel)]

if ep_min is not None:
    df_filtrado = df_filtrado[
        (df_filtrado['episodios'] >= ep_min) &
        (df_filtrado['episodios'] <= ep_max)
    ]

# =========================
# 📊 KPIs
# =========================

if not df_filtrado.empty:

    st.markdown("### 📊 Indicadores Clave")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("⭐ Score Max", f"{df_filtrado['score'].max():.2f}")

    with col2:
        st.metric("⭐ Score Min", f"{df_filtrado['score'].min():.2f}")

    with col3:
        st.metric("⭐ Score Prom", f"{df_filtrado['score'].mean():.2f}")

    with col4:
        if 'popularity' in df.columns:
            st.metric("🔥 Popularidad Prom", int(df_filtrado['popularity'].mean()))
        else:
            st.metric("🔥 Popularidad Prom", "N/A")

    with col5:
        st.metric("🎬 Total Animes", len(df_filtrado))

    st.markdown("---")

    # =========================
    # 📈 GRÁFICAS
    # =========================

    col1, col2 = st.columns(2)

    # Distribución de score
    with col1:
        st.markdown("#### Distribución de Scores")
        fig = px.box(
            df_filtrado,
            y='score',
            color='tipo' if 'tipo' in df.columns else None
        )
        st.plotly_chart(fig, use_container_width=True)

    # Episodios promedio
    with col2:
        if 'episodios' in df.columns:
            st.markdown("#### Episodios por Tipo")
            ep_tipo = df_filtrado.groupby('tipo')['episodios'].mean().reset_index()
            fig = px.bar(
                ep_tipo,
                x='tipo',
                y='episodios',
                color='episodios'
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Scatter
    st.markdown("#### 📈 Score vs Popularidad")

    if 'popularity' in df.columns:
        fig = px.scatter(
            df_filtrado,
            x='score',
            y='popularity',
            size='miembros' if 'miembros' in df.columns else None,
            color='tipo' if 'tipo' in df.columns else None,
            hover_data=['titulo']
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos de popularidad")

    st.markdown("---")

    # =========================
    # 📋 TABLA INTERACTIVA
    # =========================

    st.markdown("#### 📋 Datos Detallados")

    col1, col2 = st.columns(2)

    with col1:
        mostrar_todos = st.checkbox("Mostrar todos", value=False)

    with col2:
        columnas = st.multiselect(
            "Columnas",
            df_filtrado.columns.tolist(),
            default=['titulo', 'score', 'tipo']
        )

    if mostrar_todos:
        st.dataframe(df_filtrado[columnas], use_container_width=True)
    else:
        st.dataframe(df_filtrado[columnas].head(20), use_container_width=True)

    # =========================
    # ⬇️ DESCARGA
    # =========================

    st.markdown("---")

    csv = df_filtrado.to_csv(index=False)

    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv,
        file_name=f"anime_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ No hay datos con esos filtros")