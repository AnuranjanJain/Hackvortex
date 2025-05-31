"""
OpenStreetMap data collector for sewage infrastructure and water features.
Collects geographic data about sewage treatment plants, waterways, and related infrastructure.
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple
import requests
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
import pandas as pd
from datetime import datetime

from .config import config

class OSMCollector:
    """Collector for OpenStreetMap sewage and water infrastructure data."""
    
    def __init__(self):
        self.config = config.osm
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SewageMapAI/1.0 (https://github.com/yourusername/SewageMapAI)'
        })
    
    def build_overpass_query(self, bbox: Tuple[float, float, float, float], 
                           tags: Optional[Dict[str, List[str]]] = None) -> str:
        """
        Build Overpass API query for sewage-related infrastructure.
        
        Args:
            bbox: Bounding box (min_lat, min_lon, max_lat, max_lon)
            tags: Dictionary of OSM tags to query
            
        Returns:
            Overpass query string
        """
        if tags is None:
            tags = self.config.relevant_tags
        
        min_lat, min_lon, max_lat, max_lon = bbox
        
        # Start query with bounding box (Overpass format: south,west,north,east)
        query_parts = [
            f'[out:json][timeout:{self.config.timeout}];',
            f'[bbox:{min_lat},{min_lon},{max_lat},{max_lon}];',
            '('
        ]
        
        # Add queries for each tag combination
        for key, values in tags.items():
            for value in values:
                # Nodes
                query_parts.append(f'  node["{key}"="{value}"];')
                # Ways
                query_parts.append(f'  way["{key}"="{value}"];')
                # Relations
                query_parts.append(f'  relation["{key}"="{value}"];')
        
        # Close query and output
        query_parts.extend([
            ');',
            'out geom;'
        ])
        
        return '\n'.join(query_parts)
    
    def query_osm_data(self, bbox: Tuple[float, float, float, float], 
                      custom_tags: Optional[Dict[str, List[str]]] = None) -> Dict:
        """
        Query OSM data for specified bounding box.
        
        Args:
            bbox: Bounding box (min_lat, min_lon, max_lat, max_lon)
            custom_tags: Custom tags to query (uses default if None)
            
        Returns:
            Raw OSM data as dictionary
        """
        query = self.build_overpass_query(bbox, custom_tags)
        self.logger.info(f"Querying OSM data for bbox: {bbox}")
        
        try:
            response = self.session.post(
                self.config.overpass_url,
                data=query,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Retrieved {len(data.get('elements', []))} OSM elements")
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error querying OSM data: {e}")
            raise

    def process_osm_elements(self, osm_data: Dict) -> gpd.GeoDataFrame:
        """
        Process OSM elements into a GeoDataFrame with features and categories.
        
        Args:
            osm_data: Raw OSM data from Overpass API
            
        Returns:
            GeoDataFrame with processed features
        """
        elements = osm_data.get('elements', [])
        if not elements:
            return gpd.GeoDataFrame()
        
        features = []
        
        for element in elements:
            try:
                feature_data = {
                    'osm_id': element.get('id'),
                    'element_type': element.get('type'),
                    'tags': element.get('tags', {}),
                    'feature_category': self._categorize_feature(element.get('tags', {}))
                }
                
                # Create geometry based on element type
                if element['type'] == 'node':
                    if 'lat' in element and 'lon' in element:
                        feature_data['geometry'] = Point(element['lon'], element['lat'])
                
                elif element['type'] == 'way':
                    if 'geometry' in element:
                        coords = [(node['lon'], node['lat']) for node in element['geometry']]
                        if len(coords) > 1:
                            # Create polygon if coordinates form a closed shape
                            if coords[0] == coords[-1] and len(coords) > 3:
                                feature_data['geometry'] = Polygon(coords)
                            else:
                                feature_data['geometry'] = LineString(coords)
                
                # Add additional tag information
                tags = element.get('tags', {})
                feature_data.update({
                    'name': tags.get('name', 'Unknown'),
                    'amenity': tags.get('amenity', ''),
                    'man_made': tags.get('man_made', ''),
                    'natural': tags.get('natural', ''),
                    'waterway': tags.get('waterway', ''),
                    'landuse': tags.get('landuse', '')
                })
                
                if 'geometry' in feature_data:
                    features.append(feature_data)
                    
            except Exception as e:
                self.logger.warning(f"Error processing OSM element {element.get('id', 'unknown')}: {e}")
                continue
        
        if not features:
            return gpd.GeoDataFrame()
        
        gdf = gpd.GeoDataFrame(features, crs='EPSG:4326')
        self.logger.info(f"Processed {len(gdf)} OSM features")
        
        return gdf
    
    def _categorize_feature(self, tags: Dict[str, str]) -> str:
        """
        Categorize OSM feature based on its tags.
        
        Args:
            tags: OSM tags dictionary
            
        Returns:
            Feature category string
        """
        # Check for sewage-related infrastructure
        if tags.get('amenity') == 'waste_disposal' or tags.get('man_made') in ['wastewater_plant', 'sewage_treatment']:
            return 'sewage_treatment'
        
        if tags.get('man_made') == 'pipeline' and 'sewage' in tags.get('substance', '').lower():
            return 'sewage_pipeline'
        
        # Water features
        if tags.get('natural') in ['water', 'wetland'] or tags.get('landuse') == 'reservoir':
            return 'water_body'
        
        if tags.get('waterway') in ['river', 'stream', 'canal', 'drain']:
            return 'waterway'
        
        # Industrial features
        if tags.get('landuse') == 'industrial' or tags.get('amenity') == 'fuel':
            return 'industrial'
        
        # Urban features
        if tags.get('landuse') in ['residential', 'commercial', 'retail']:
            return 'urban'
        
        return 'other'

    def collect_region_data(self, region_name: str, bbox: Tuple[float, float, float, float],
                          custom_tags: Optional[Dict[str, List[str]]] = None) -> Optional[str]:
        """
        Collect OSM data for a specific region and save to file.
        
        Args:
            region_name: Name of the region (for file naming)
            bbox: Bounding box (min_lat, min_lon, max_lat, max_lon)
            custom_tags: Custom tags to query
            
        Returns:
            Path to saved data file, or None if no data found
        """
        self.logger.info(f"Collecting OSM data for region: {region_name}")
        
        # Query data
        osm_data = self.query_osm_data(bbox, custom_tags)
        
        # Process to GeoDataFrame
        gdf = self.process_osm_elements(osm_data)
        
        if gdf.empty:
            self.logger.warning(f"No OSM data found for region: {region_name}")
            return None
        
        # Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"osm_{region_name}_{timestamp}.geojson"
        filepath = os.path.join(config.raw_data_dir, 'osm', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        gdf.to_file(filepath, driver='GeoJSON')
        
        # Save metadata
        metadata = {
            'region_name': region_name,
            'bbox': bbox,
            'collection_date': datetime.now().isoformat(),
            'feature_count': len(gdf),
            'categories': gdf['feature_category'].value_counts().to_dict(),
            'file_path': filepath
        }
        
        metadata_path = filepath.replace('.geojson', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Saved {len(gdf)} OSM features to: {filepath}")
        return filepath

    def collect_cities_data(self, cities: List[Dict]) -> List[str]:
        """
        Collect OSM data for multiple cities.
        
        Args:
            cities: List of city dictionaries with 'name' and 'bbox' keys
            
        Returns:
            List of file paths for collected data
        """
        collected_files = []
        
        for city in cities:
            try:
                filepath = self.collect_region_data(
                    region_name=city['name'].lower().replace(' ', '_'),
                    bbox=city['bbox']
                )
                
                if filepath:
                    collected_files.append(filepath)
                    
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error collecting data for {city['name']}: {e}")
                continue
        
        return collected_files

# Major cities with bounding boxes for data collection
MAJOR_CITIES = [
    {
        'name': 'New York',
        'bbox': (40.4774, -74.2591, 40.9176, -73.7004)
    },
    {
        'name': 'Los Angeles', 
        'bbox': (33.7037, -118.6681, 34.3373, -118.1553)
    },
    {
        'name': 'Chicago',
        'bbox': (41.6444, -87.9073, 42.0230, -87.5244)
    },
    {
        'name': 'Houston',
        'bbox': (29.5234, -95.8189, 30.1103, -95.0696)
    },
    {
        'name': 'San Francisco',
        'bbox': (37.7049, -122.5267, 37.8367, -122.3503)
    }
]
