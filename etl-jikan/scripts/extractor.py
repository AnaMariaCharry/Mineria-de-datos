#!/usr/bin/env python3
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Crear carpetas necesarias antes del logging
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JikanExtractor:
    def __init__(self):
        self.base_url = os.getenv('JIKAN_BASE_URL')
        self.limit = int(os.getenv('ANIME_LIMIT', 25))
        self.page = int(os.getenv('ANIME_PAGE', 1))

        if not self.base_url:
            raise ValueError("JIKAN_BASE_URL no configurado en .env")

    def extraer_animes(self):
        """Extrae datos de anime TOP desde la API de Jikan"""
        try:
            url = f"{self.base_url}/top/anime"
            params = {
                'page': self.page,
                'limit': self.limit
            }

            logger.info(f"🌐 Consultando API: {url} (page={self.page}, limit={self.limit})")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data:
                logger.error("❌ Respuesta inválida de la API")
                return None

            logger.info(f"✅ {len(data['data'])} animes extraídos correctamente")
            return data['data']

        except Exception as e:
            logger.error(f"❌ Error extrayendo animes: {str(e)}")
            return None

    def procesar_anime(self, anime):
        """Procesa un anime individual"""
        try:
            return {
                'id': anime.get('mal_id'),
                'titulo': anime.get('title'),
                'titulo_ingles': anime.get('title_english'),
                'score': anime.get('score'),
                'episodios': anime.get('episodes'),
                'estado': anime.get('status'),
                'tipo': anime.get('type'),
                'fecha_inicio': anime.get('aired', {}).get('from'),
                'fecha_fin': anime.get('aired', {}).get('to'),
                'rating': anime.get('rating'),
                'popularidad': anime.get('popularity'),
                'miembros': anime.get('members'),
                'generos': [g['name'] for g in anime.get('genres', [])],
                'fecha_extraccion': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Error procesando anime: {str(e)}")
            return None

    def ejecutar_extraccion(self):
        """Ejecuta la extracción completa"""
        datos_procesados = []

        logger.info("🚀 Iniciando extracción de animes TOP...")

        animes = self.extraer_animes()

        if not animes:
            logger.error("❌ No se obtuvieron datos")
            return []

        for anime in animes:
            procesado = self.procesar_anime(anime)
            if procesado:
                datos_procesados.append(procesado)

        logger.info(f"📊 Total de animes procesados: {len(datos_procesados)}")
        return datos_procesados


if __name__ == "__main__":
    try:
        extractor = JikanExtractor()
        datos = extractor.ejecutar_extraccion()

        if not datos:
            logger.error("❌ No hay datos para guardar")
            exit()

        # Guardar JSON
        with open('data/anime_raw.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.info("📁 Datos guardados en data/anime_raw.json")

        # Guardar CSV
        df = pd.DataFrame(datos)
        df.to_csv('data/anime.csv', index=False)
        logger.info("📁 Datos guardados en data/anime.csv")

        # Mostrar resumen
        print("\n" + "="*50)
        print("RESUMEN DE EXTRACCIÓN")
        print("="*50)
        print(df.head().to_string())
        print("="*50)

    except Exception as e:
        logger.error(f"❌ Error en ejecución: {str(e)}")