#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Anime ETL",
    page_icon="🎬",
    layout="wide"
)

# Título
st.title("🎌 Dashboard de Anime - ETL Jikan")
st.markdown("---")

# Verificar archivo
if not os.path.exists('data/anime.csv'):
    st.error("❌ No existe el archivo data/anime.csv. Ejecuta primero el extractor.")
    st.stop()

# Cargar datos
df = pd.read_csv('data/anime.csv')

# =========================
# 🔧 LIMPIEZA SEGURA
# =========================

# Verificar columnas existentes
columnas = df.columns

if 'score' not in columnas:
    st.error("❌ No existe la columna 'score' en el dataset")
    st.stop()

# Limpiar dependiendo de columnas disponibles
if 'popularity' in columnas:
    df = df.dropna(subset=['score', 'popularity'])
else:
    df = df.dropna(subset=['score'])

# =========================
# 🎛️ FILTROS
# =========================

st.sidebar.title("🔧 Filtros")

tipos = st.sidebar.multiselect(
    "Tipo de Anime:",
    options=df['tipo'].dropna().unique() if 'tipo' in columnas else [],
    default=df['tipo'].dropna().unique() if 'tipo' in columnas else []
)

score_min = st.sidebar.slider(
    "Score mínimo:",
    min_value=float(df['score'].min()),
    max_value=float(df['score'].max()),
    value=float(df['score'].min())
)

# Filtrar datos
df_filtrado = df[df['score'] >= score_min]

if 'tipo' in columnas:
    df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipos)]

# =========================
# 📊 MÉTRICAS
# =========================

st.subheader("📈 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("⭐ Score Promedio", f"{df_filtrado['score'].mean():.2f}")

with col2:
    st.metric("🎬 Total Animes", len(df_filtrado))

with col3:
    if 'popularity' in columnas:
        st.metric("🔥 Popularidad Promedio", int(df_filtrado['popularity'].mean()))
    else:
        st.metric("🔥 Popularidad Promedio", "N/A")

with col4:
    if not df_filtrado.empty:
        top_anime = df_filtrado.sort_values('score', ascending=False).iloc[0]['titulo']
        st.metric("🏆 Top Anime", top_anime)
    else:
        st.metric("🏆 Top Anime", "N/A")

st.markdown("---")

# =========================
# 📉 GRÁFICAS
# =========================

st.subheader("📊 Visualizaciones")

col1, col2 = st.columns(2)

# 🔹 Top animes
with col1:
    top10 = df_filtrado.sort_values(by='score', ascending=False).head(10)
    fig1 = px.bar(
        top10,
        x='score',
        y='titulo',
        orientation='h',
        title="Top 10 Animes por Score"
    )
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

# 🔹 Tipos de anime
with col2:
    if 'tipo' in columnas:
        tipos_count = df_filtrado['tipo'].value_counts().reset_index()
        tipos_count.columns = ['tipo', 'count']

        fig2 = px.pie(
            tipos_count,
            names='tipo',
            values='count',
            title="Distribución por Tipo"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos de tipo de anime")

# Segunda fila
col1, col2 = st.columns(2)

# 🔹 Scatter score vs popularidad
with col1:
    if 'popularity' in columnas and 'miembros' in columnas:
        fig3 = px.scatter(
            df_filtrado,
            x='score',
            y='popularity',
            size='miembros',
            color='tipo' if 'tipo' in columnas else None,
            hover_data=['titulo'],
            title="Score vs Popularidad"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos suficientes para scatter")

# 🔹 Episodios
with col2:
    if 'episodios' in columnas:
        episodios = df_filtrado.sort_values(by='episodios', ascending=False).head(10)

        fig4 = px.bar(
            episodios,
            x='titulo',
            y='episodios',
            title="Top 10 Animes por Episodios"
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos de episodios")

st.markdown("---")

# =========================
# 📋 TABLA
# =========================

st.subheader("📋 Datos Detallados")

st.dataframe(
    df_filtrado.sort_values('score', ascending=False),
    use_container_width=True
)