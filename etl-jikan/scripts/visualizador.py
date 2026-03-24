#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar que exista el archivo
if not os.path.exists('data/anime.csv'):
    logger.error("❌ No existe data/anime.csv. Ejecuta primero el extractor.")
    exit()

# Cargar datos
df = pd.read_csv('data/anime.csv')

# Limpiar datos básicos
df = df.dropna(subset=['score', 'popularity'])

# Crear figura con múltiples gráficas
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Análisis de Anime', fontsize=16, fontweight='bold')

# 🔹 Gráfica 1: Top 10 animes por score
ax1 = axes[0, 0]
top_anime = df.sort_values(by='score', ascending=False).head(10)
ax1.barh(top_anime['titulo'], top_anime['score'])
ax1.set_title('Top 10 Animes por Score')
ax1.set_xlabel('Score')
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# 🔹 Gráfica 2: Tipos de anime
ax2 = axes[0, 1]
tipos = df['tipo'].value_counts()
ax2.pie(tipos, labels=tipos.index, autopct='%1.1f%%')
ax2.set_title('Distribución por Tipo de Anime')

# 🔹 Gráfica 3: Popularidad vs Score
ax3 = axes[1, 0]
ax3.scatter(df['score'], df['popularity'], s=100)
ax3.set_title('Score vs Popularidad')
ax3.set_xlabel('Score')
ax3.set_ylabel('Popularidad')
ax3.grid(alpha=0.3)

# 🔹 Gráfica 4: Episodios por anime (Top 10)
ax4 = axes[1, 1]
episodios = df.sort_values(by='episodios', ascending=False).head(10)
x = np.arange(len(episodios))
ax4.bar(x, episodios['episodios'])
ax4.set_title('Top 10 Animes por Número de Episodios')
ax4.set_xticks(x)
ax4.set_xticklabels(episodios['titulo'], rotation=45)
ax4.set_ylabel('Episodios')
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()

# Crear carpeta si no existe
os.makedirs('data', exist_ok=True)

# Guardar imagen
plt.savefig('data/anime_analysis.png', dpi=300, bbox_inches='tight')
logger.info("✅ Gráficas guardadas en data/anime_analysis.png")

plt.show()