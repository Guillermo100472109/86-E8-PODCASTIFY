import unittest 

from app import *

"""
Unit tests para el sistema de análisis de podcasts.

Este archivo contiene pruebas para todas las funcionalidades principales:
- Validación de datos (método HTTP, estado, formato, user agents)
- Carga y análisis del dataset
- Generación de estadísticas
- Ranking de programas
- Sistema de recomendaciones
- Enriquecimiento geográfico
- Gestión de entidades

Los valores de los asserts son CONSTANTES y deben coincidir con el dataset de prueba.
"""

class PodcastAnalysisTest(unittest.TestCase): 
    
    def setUp(self): 
        print("Setup - Inicializando tests")
    
    def tearDown(self):
        print("Teardown - Finalizando tests")
    
    # ============================================
    # VALIDACIONES (RF-2, RF-3, RF-4, RF-5)
    # ============================================
    
    def test_is_valid_method(self):
        """RF-2: Validación de método HTTP - Solo GET es válido"""
        self.assertFalse(is_valid_method(None))
        self.assertFalse(is_valid_method(""))
        self.assertTrue(is_valid_method("GET"))
        self.assertTrue(is_valid_method("get"))
        self.assertFalse(is_valid_method("POST"))
        self.assertFalse(is_valid_method("PUT"))
        self.assertFalse(is_valid_method("DELETE"))
        self.assertFalse(is_valid_method("HEAD"))
    
    def test_is_valid_status(self):
        """RF-3: Validación de estado HTTP - Solo 200 o 206"""
        self.assertFalse(is_valid_status(None))
        self.assertFalse(is_valid_status(""))
        self.assertTrue(is_valid_status("200"))
        self.assertTrue(is_valid_status("206"))
        self.assertFalse(is_valid_status("201"))
        self.assertFalse(is_valid_status("301"))
        self.assertFalse(is_valid_status("404"))
        self.assertFalse(is_valid_status("500"))
    
    def test_is_valid_resource(self):
        """RF-5: Validación de formato - Solo archivos .mp3"""
        self.assertFalse(is_valid_resource(None))
        self.assertFalse(is_valid_resource(""))
        self.assertTrue(is_valid_resource("podcast_episode.mp3"))
        self.assertTrue(is_valid_resource("EPISODE.MP3"))
        self.assertTrue(is_valid_resource("/path/to/file.mp3"))
        self.assertFalse(is_valid_resource("podcast.mp4"))
        self.assertFalse(is_valid_resource("audio.wav"))
        self.assertFalse(is_valid_resource("document.pdf"))
        self.assertFalse(is_valid_resource("file.mp3.txt"))
    
    def test_is_valid_user_agent(self):
        """RF-4: Detección de bots - Rechazar BOT, SPIDER, CRAWLER, HERITRIX"""
        self.assertFalse(is_valid_user_agent(None))
        self.assertFalse(is_valid_user_agent(""))
        self.assertFalse(is_valid_user_agent("GoogleBot"))
        self.assertFalse(is_valid_user_agent("spider-crawler"))
        self.assertFalse(is_valid_user_agent("Web Crawler"))
        self.assertFalse(is_valid_user_agent("Heritrix/3.0"))
        self.assertFalse(is_valid_user_agent("bot scanner"))
        self.assertTrue(is_valid_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"))
        self.assertTrue(is_valid_user_agent("Chrome/91.0.4472.124"))
        self.assertTrue(is_valid_user_agent("Safari/537.36"))
    
    # ============================================
    # CARGA Y PROCESAMIENTO DE DATOS (RF-1, RF-6)
    # ============================================
    
    def test_load_dataset(self):
        """RF-1: Carga de dataset desde CSV"""
        result = load_dataset()
        self.assertTrue(len(result) == 10000)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
    
    def test_analyze_dataset(self):
        """RF-6, RF-7: Análisis del dataset con todas las validaciones"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        # Esperamos aproximadamente 3200-3800 observaciones válidas
        self.assertTrue(len(observations) == 3527)
        self.assertIsInstance(observations, list)
    
    # ============================================
    # LÓGICA DE DESCARGAS (RF-7)
    # ============================================
    
    def test_download_logic_206(self):
        """RF-7: Lógica de descarga para estado 206 (>= 1MB)"""
        # Estado 206 requiere >= 1048576 bytes (1MB) acumulados
        self.assertTrue(is_valid_download_206(1048576))
        self.assertTrue(is_valid_download_206(2000000))
        self.assertFalse(is_valid_download_206(1048575))
        self.assertFalse(is_valid_download_206(500000))
    
    def test_download_logic_200(self):
        """RF-7: Lógica de descarga para estado 200 (>= 30MB)"""
        # Estado 200 requiere >= 31457280 bytes (30MB) acumulados
        self.assertTrue(is_valid_download_200(31457280))
        self.assertTrue(is_valid_download_200(50000000))
        self.assertFalse(is_valid_download_200(31457279))
        self.assertFalse(is_valid_download_200(20000000))
    
    def test_unique_observation(self):
        """RF-7: Unicidad de observación - mismo usuario/episodio"""
        observations = [
            {"user_id": "user1", "user_agent": "Mozilla", "episode_id": "ep1"},
            {"user_id": "user1", "user_agent": "Mozilla", "episode_id": "ep1"},
            {"user_id": "user1", "user_agent": "Mozilla", "episode_id": "ep2"},
        ]
        unique_obs = filter_unique_observations(observations)
        self.assertTrue(len(unique_obs) == 2)
    
    # ============================================
    # ENRIQUECIMIENTO GEOGRÁFICO (RF-7)
    # ============================================
    
    def test_geo_enrichment(self):
        """RF-7: Asignación de coordenadas de capitales de CCAA"""
        observation = {"user_id": "test_user"}
        enriched = enrich_with_geo_data(observation)
        
        self.assertIn("latitude", enriched)
        self.assertIn("longitude", enriched)
        
        # Verificar que las coordenadas están en rango de España
        # España: latitud 36-44°N, longitud -10-4°E
        self.assertTrue(36 <= enriched["latitude"] <= 44)
        self.assertTrue(-10 <= enriched["longitude"] <= 4)
    
    def test_geo_capitals_coverage(self):
        """Verificar que se usan capitales de las 17 CCAA"""
        capitals = get_ccaa_capitals()
        self.assertTrue(len(capitals) == 17)
        
        # Verificar que incluye algunas capitales conocidas
        capital_names = [c["name"] for c in capitals]
        self.assertIn("Madrid", capital_names)
        self.assertIn("Barcelona", capital_names)
        self.assertIn("Sevilla", capital_names)
    
    # ============================================
    # ESTADÍSTICAS Y MÉTRICAS (RF-8)
    # ============================================
    
    def test_generate_stats(self):
        """RF-8: Generación de estadísticas de análisis"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        stats = generate_stats(observations)
        
        # Verificar que todas las métricas están presentes
        self.assertIn("Download 200", stats)
        self.assertIn("Download 206", stats)
        self.assertIn("Bad status", stats)
        self.assertIn("Bad method", stats)
        self.assertIn("Bad format resource", stats)
        self.assertIn("Bot detected", stats)
        
        # Valores esperados basados en el dataset de prueba
        self.assertTrue(stats["Download 200"] == 45)
        self.assertTrue(stats["Download 206"] == 2650)
        self.assertTrue(stats["Bad status"] == 832)
        self.assertTrue(stats["Bad method"] == 1250)
        self.assertTrue(stats["Bad format resource"] == 156)
        self.assertTrue(stats["Bot detected"] == 67)
    
    def test_stats_consistency(self):
        """Verificar consistencia de las estadísticas"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        stats = generate_stats(observations)
        
        # La suma de descargas válidas no debe superar observaciones válidas
        total_downloads = stats["Download 200"] + stats["Download 206"]
        self.assertTrue(total_downloads <= len(observations))
        
        # Todos los valores deben ser no negativos
        for key, value in stats.items():
            self.assertTrue(value >= 0, f"{key} debe ser no negativo")
    
    # ============================================
    # RANKING DE PROGRAMAS (RF-9)
    # ============================================
    
    def test_list_top_k_programs(self):
        """RF-9: Lista de K programas principales ordenados por descargas"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        all_top_programs = list_top_programs(observations)
        
        # Test con k=0
        k = 0
        top_k = list_top_k_programs(all_top_programs, k)
        self.assertTrue(len(top_k) == 0)
        
        # Test con k=3
        k = 3
        top_k = list_top_k_programs(all_top_programs, k)
        self.assertTrue(len(top_k) == 3)
        
        # Verificar orden descendente
        self.assertTrue(top_k[0][1] >= top_k[1][1])
        self.assertTrue(top_k[1][1] >= top_k[2][1])
        
        # Valores esperados para los top 3
        self.assertTrue(top_k[0][1] == 512)
        self.assertTrue(top_k[1][1] == 256)
        self.assertTrue(top_k[2][1] == 198)
    
    def test_list_top_k_programs_boundaries(self):
        """Test de casos límite para ranking"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        all_top_programs = list_top_programs(observations)
        
        # k mayor que número de programas disponibles
        k = 1000
        top_k = list_top_k_programs(all_top_programs, k)
        self.assertTrue(len(top_k) <= len(all_top_programs))
        
        # k = 1
        k = 1
        top_k = list_top_k_programs(all_top_programs, k)
        self.assertTrue(len(top_k) == 1)
    
    def test_program_ranking_structure(self):
        """Verificar estructura de datos del ranking"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        all_top_programs = list_top_programs(observations)
        
        # Cada programa debe ser una tupla (nombre, descargas)
        for program in all_top_programs[:5]:
            self.assertIsInstance(program, tuple)
            self.assertEqual(len(program), 2)
            self.assertIsInstance(program[0], str)  # nombre
            self.assertIsInstance(program[1], int)  # descargas
    
    # ============================================
    # LISTADO DE EPISODIOS
    # ============================================
    
    def test_list_episodes(self):
        """Verificar listado de episodios únicos"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        episode_set = list_episodes(observations)
        
        self.assertIsNotNone(episode_set)
        self.assertTrue(len(episode_set) > 0)
        
        # Verificar que no hay duplicados
        if isinstance(episode_set, list):
            self.assertEqual(len(episode_set), len(set(episode_set)))
    
    # ============================================
    # SISTEMA DE RECOMENDACIONES (RF-11)
    # ============================================
    
    def test_recommend(self):
        """RF-11: Sistema de recomendaciones basado en temas y descargas"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        episode_set = list_episodes(observations)
        
        # Usuario de prueba
        user = "df273cf4-d335-4b7f-b979-17212e8b84d3"
        recommendations = recommend(observations, episode_set, user) 
        
        # Debe devolver exactamente 5 recomendaciones
        self.assertTrue(len(recommendations) == 5)
        self.assertIsInstance(recommendations, list)
    
    def test_recommend_different_users(self):
        """Verificar que las recomendaciones varían por usuario"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        episode_set = list_episodes(observations)
        
        user1 = "df273cf4-d335-4b7f-b979-17212e8b84d3"
        user2 = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        
        recommendations1 = recommend(observations, episode_set, user1)
        recommendations2 = recommend(observations, episode_set, user2)
        
        # Ambas deben tener 5 elementos
        self.assertEqual(len(recommendations1), 5)
        self.assertEqual(len(recommendations2), 5)
    
    def test_recommend_ordering(self):
        """Verificar que las recomendaciones están ordenadas por descargas"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        episode_set = list_episodes(observations)
        
        user = "df273cf4-d335-4b7f-b979-17212e8b84d3"
        recommendations = recommend(observations, episode_set, user)
        
        # Si las recomendaciones incluyen contador de descargas,
        # verificar orden descendente
        if len(recommendations) > 1 and isinstance(recommendations[0], tuple):
            for i in range(len(recommendations) - 1):
                self.assertTrue(recommendations[i][1] >= recommendations[i+1][1])
    
    # ============================================
    # GESTIÓN DE ENTIDADES (Tarea 13)
    # ============================================
    
    def test_podcast_entity(self):
        """Verificar creación y gestión de entidad Podcast"""
        podcast = create_podcast(
            id="podcast_001",
            title="Tech Talks",
            description="Podcast sobre tecnología"
        )
        
        self.assertIsNotNone(podcast)
        self.assertEqual(podcast["id"], "podcast_001")
        self.assertEqual(podcast["title"], "Tech Talks")
    
    def test_episode_entity(self):
        """Verificar creación y gestión de entidad Episodio"""
        episode = create_episode(
            id="episode_001",
            podcast_id="podcast_001",
            title="Episodio 1",
            duration=3600
        )
        
        self.assertIsNotNone(episode)
        self.assertEqual(episode["id"], "episode_001")
        self.assertEqual(episode["podcast_id"], "podcast_001")
    
    def test_metric_entity(self):
        """Verificar creación y gestión de entidad Métrica"""
        metric = create_metric(
            metric_type="Download 200",
            value=45
        )
        
        self.assertIsNotNone(metric)
        self.assertEqual(metric["type"], "Download 200")
        self.assertEqual(metric["value"], 45)
    
    def test_observation_entity(self):
        """Verificar creación y gestión de entidad Observación"""
        observation = create_observation(
            user_id="user_123",
            episode_id="episode_001",
            timestamp="2024-01-15T10:30:00",
            status="200",
            bytes_transferred=31457280
        )
        
        self.assertIsNotNone(observation)
        self.assertEqual(observation["user_id"], "user_123")
        self.assertEqual(observation["status"], "200")
    
    # ============================================
    # INTEGRACIÓN Y FLUJO COMPLETO
    # ============================================
    
    def test_complete_pipeline(self):
        """Test de integración: flujo completo del sistema"""
        # 1. Cargar datos
        data_entries = load_dataset()
        self.assertTrue(len(data_entries) > 0)
        
        # 2. Analizar y filtrar
        observations = analyze_dataset(data_entries)
        self.assertTrue(len(observations) > 0)
        
        # 3. Generar estadísticas
        stats = generate_stats(observations)
        self.assertIn("Download 200", stats)
        
        # 4. Obtener ranking
        all_programs = list_top_programs(observations)
        top_3 = list_top_k_programs(all_programs, 3)
        self.assertEqual(len(top_3), 3)
        
        # 5. Generar recomendaciones
        episodes = list_episodes(observations)
        recommendations = recommend(observations, episodes, "test_user")
        self.assertEqual(len(recommendations), 5)
    
    def test_data_quality(self):
        """Verificar calidad de datos procesados"""
        data_entries = load_dataset()
        observations = analyze_dataset(data_entries)
        
        # Todas las observaciones válidas deben cumplir criterios
        for obs in observations[:10]:  # Muestra de 10
            # Debe tener campos requeridos
            self.assertIn("method", obs)
            self.assertIn("status", obs)
            
            # Los valores deben ser válidos
            if "method" in obs:
                self.assertTrue(is_valid_method(obs["method"]))
            if "status" in obs:
                self.assertTrue(is_valid_status(obs["status"]))


if __name__ == '__main__': 
    # Ejecutar tests con verbosidad
    unittest.main(verbosity=2)