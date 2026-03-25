#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Dashboard Avanzado Anime",
    page_icon="🎌",
    layout="wide"
)

st.title("🎬 Dashboard Avanzado - Análisis de Anime (Jikan)")
st.markdown("---")

# Verificar archivo
if not os.path.exists('data/anime.csv'):
    st.error("❌ No existe data/anime.csv")
    st.stop()

# Cargar datos
df = pd.read_csv('data/anime.csv')

# Limpieza segura
if 'score' in df.columns:
    df = df.dropna(subset=['score'])

# =========================
# 📊 TABS
# =========================

tab1, tab2, tab3 = st.tabs([
    "📊 Vista General",
    "📈 Análisis",
    "🔍 Exploración"
])

# =========================
# 📊 TAB 1: GENERAL
# =========================

with tab1:
    st.subheader("Resumen General")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎬 Total Animes", len(df))

    with col2:
        st.metric("⭐ Score Promedio", f"{df['score'].mean():.2f}")

    with col3:
        if 'tipo' in df.columns:
            st.metric("📺 Tipos únicos", df['tipo'].nunique())
        else:
            st.metric("📺 Tipos únicos", "N/A")

    st.markdown("---")

    col1, col2 = st.columns(2)

    # Top animes
    with col1:
        top10 = df.sort_values('score', ascending=False).head(10)
        fig = px.bar(
            top10,
            x='score',
            y='titulo',
            orientation='h',
            title="Top 10 Animes"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Tipos
    with col2:
        if 'tipo' in df.columns:
            tipos = df['tipo'].value_counts().reset_index()
            tipos.columns = ['tipo', 'count']

            fig = px.pie(
                tipos,
                names='tipo',
                values='count',
                title="Distribución por Tipo"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.dataframe(df, use_container_width=True)


# =========================
# 📈 TAB 2: ANÁLISIS
# =========================

with tab2:
    st.subheader("Análisis de Datos")

    col1, col2 = st.columns(2)

    # Score vs Popularidad
    with col1:
        if 'popularity' in df.columns:
            fig = px.scatter(
                df,
                x='score',
                y='popularity',
                size='miembros' if 'miembros' in df.columns else None,
                color='tipo' if 'tipo' in df.columns else None,
                hover_data=['titulo'],
                title="Score vs Popularidad"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de popularidad")

    # Episodios
    with col2:
        if 'episodios' in df.columns:
            top_ep = df.sort_values('episodios', ascending=False).head(10)
            fig = px.bar(
                top_ep,
                x='titulo',
                y='episodios',
                title="Top Animes por Episodios"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de episodios")

    st.markdown("---")

    # Distribución de score
    fig = px.histogram(
        df,
        x='score',
        nbins=20,
        title="Distribución de Scores"
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================
# 🔍 TAB 3: EXPLORACIÓN
# =========================

with tab3:
    st.subheader("Exploración Avanzada")

    # Filtros dinámicos
    tipo_sel = None
    if 'tipo' in df.columns:
        tipo_sel = st.selectbox(
            "Filtrar por tipo:",
            options=["Todos"] + list(df['tipo'].dropna().unique())
        )

    score_min = st.slider(
        "Score mínimo",
        float(df['score'].min()),
        float(df['score'].max()),
        float(df['score'].min())
    )

    df_filtrado = df[df['score'] >= score_min]

    if tipo_sel and tipo_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_sel]

    st.markdown("---")

    # Tabla
    st.dataframe(df_filtrado, use_container_width=True)

    # Top 5 recomendados
    st.subheader("🏆 Recomendaciones (Top 5)")

    top5 = df_filtrado.sort_values('score', ascending=False).head(5)

    for _, row in top5.iterrows():
        st.write(f"⭐ **{row['titulo']}** - Score: {row['score']}")
