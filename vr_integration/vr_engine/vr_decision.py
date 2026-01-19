"""
VR Decision Engine
Determines if VR should be activated based on model predictions and criteria
"""

from typing import Dict, Optional, Tuple
from enum import Enum


class VRMode(Enum):
    """VR interaction modes based on question type"""
    CLOSED = "closed"  # VR kapalı (Hesaplama)
    OPTIONAL = "optional"  # İsteğe bağlı (Hesaplama - göster butonu)
    GUIDED = "guided"  # Rehberli mod (Problem)
    FULL = "full"  # Tam açık (Yorum)


class VRSceneType(Enum):
    """Available VR scene types"""
    AREA_GEOMETRY = "area_geometry"  # Alan ve Geometri
    AREA_PERIMETER = "area_perimeter"  # Alan-Çevre
    NUMBER_LINE = "number_line"  # Sayı Doğrusu
    COMPARISON = "comparison"  # Karşılaştırma ve Sıralama
    NONE = "none"  # VR açılmaz


class VRDecisionEngine:
    """
    VR Decision Engine
    
    Decides:
    1. Should VR be activated?
    2. Which scene should be used?
    3. What mode should VR run in?
    """
    
    # VR açılacak alt_konu sınıfları
    VR_ENABLED_TOPICS = {
        "Alan ve Geometri",
        "Yaklaşık Değer",
        "Karşılaştırma ve Sıralama"
    }
    
    # VR açılacak soru_tipi sınıfları
    VR_ENABLED_TYPES = {
        "Problem",
        "Yorum"
    }
    
    # Alt konu -> VR Scene mapping
    # Note: Mapping based on actual label_map.json values
    TOPIC_TO_SCENE = {
        "Alan ve Geometri": VRSceneType.AREA_GEOMETRY,
        "Yaklaşık Değer": VRSceneType.NUMBER_LINE,
        "Karşılaştırma ve Sıralama": VRSceneType.COMPARISON,
        # Fallback mappings for similar topics
        "Üslü ve Köklü İfadeler": VRSceneType.NUMBER_LINE,  # Can use number line for visualization
    }
    
    # Soru tipi -> VR Mode mapping
    TYPE_TO_MODE = {
        "Hesaplama": VRMode.OPTIONAL,  # İsteğe bağlı göster butonu
        "Problem": VRMode.GUIDED,  # Rehberli mod
        "Yorum": VRMode.FULL  # Tam açık
    }
    
    def __init__(self):
        """Initialize VR Decision Engine"""
        pass
    
    def should_activate_vr(
        self,
        alt_konu: str,
        soru_tipi: str,
        gorsel_bagimli: Optional[str] = None
    ) -> bool:
        """
        Determine if VR should be activated
        
        Criteria:
        1. gorsel_bagimli = "bagimli" (if provided)
        2. alt_konu in VR_ENABLED_TOPICS
        3. soru_tipi in VR_ENABLED_TYPES
        
        Args:
            alt_konu: Predicted alt_konu label
            soru_tipi: Predicted soru_tipi label
            gorsel_bagimli: Visual dependency flag (optional)
            
        Returns:
            bool: True if VR should be activated
        """
        # Check visual dependency
        if gorsel_bagimli:
            gorsel_val = str(gorsel_bagimli).lower()
            if 'bagimli' in gorsel_val or 'var' in gorsel_val:
                # Visual dependent - check if topic/type also match
                topic_match = alt_konu in self.VR_ENABLED_TOPICS
                type_match = soru_tipi in self.VR_ENABLED_TYPES
                return topic_match or type_match
        
        # Check topic match
        topic_match = alt_konu in self.VR_ENABLED_TOPICS
        
        # Check type match
        type_match = soru_tipi in self.VR_ENABLED_TYPES
        
        # VR activates if topic OR type matches (OR logic)
        return topic_match or type_match
    
    def get_vr_config(
        self,
        alt_konu: str,
        soru_tipi: str,
        gorsel_bagimli: Optional[str] = None
    ) -> Dict:
        """
        Get complete VR configuration
        
        Args:
            alt_konu: Predicted alt_konu label
            soru_tipi: Predicted soru_tipi label
            gorsel_bagimli: Visual dependency flag (optional)
            
        Returns:
            Dict with:
                - activated: bool
                - scene_type: VRSceneType
                - mode: VRMode
                - config: scene-specific config
        """
        activated = self.should_activate_vr(alt_konu, soru_tipi, gorsel_bagimli)
        
        if not activated:
            return {
                "activated": False,
                "scene_type": VRSceneType.NONE.value,
                "mode": VRMode.CLOSED.value,
                "config": {}
            }
        
        # Get scene type
        scene_type = self.TOPIC_TO_SCENE.get(alt_konu, VRSceneType.NONE)
        
        # Get mode
        mode = self.TYPE_TO_MODE.get(soru_tipi, VRMode.OPTIONAL)
        
        # Scene-specific config
        config = self._get_scene_config(scene_type, alt_konu, soru_tipi)
        
        return {
            "activated": True,
            "scene_type": scene_type.value,
            "mode": mode.value,
            "config": config
        }
    
    def _get_scene_config(
        self,
        scene_type: VRSceneType,
        alt_konu: str,
        soru_tipi: str
    ) -> Dict:
        """
        Get scene-specific configuration
        
        Args:
            scene_type: Selected VR scene type
            alt_konu: Alt konu label
            soru_tipi: Soru tipi label
            
        Returns:
            Dict with scene-specific parameters
        """
        base_config = {
            "interactive": True,
            "show_labels": True,
            "animation_speed": 1.0
        }
        
        if scene_type == VRSceneType.AREA_GEOMETRY:
            return {
                **base_config,
                "shapes": ["kare", "dikdörtgen", "üçgen"],
                "draggable_edges": True,
                "live_area_calculation": True,
                "show_sqrt_simplification": True
            }
        
        elif scene_type == VRSceneType.AREA_PERIMETER:
            return {
                **base_config,
                "show_perimeter_path": True,
                "perimeter_color": "#00ff00",
                "show_area_fill": True,
                "area_color": "#0000ff",
                "sqrt_edge_labels": True
            }
        
        elif scene_type == VRSceneType.NUMBER_LINE:
            return {
                **base_config,
                "highlight_nearest_integers": True,
                "show_approximation": True,
                "interactive_point": True,
                "number_range": [-10, 10]  # Adjustable
            }
        
        elif scene_type == VRSceneType.COMPARISON:
            return {
                **base_config,
                "bar_chart_style": True,
                "height_represents_value": True,
                "interactive_bars": True,
                "show_comparison_lines": True
            }
        
        else:
            return base_config


# Singleton instance
_vr_engine = None

def get_vr_engine() -> VRDecisionEngine:
    """Get singleton VR engine instance"""
    global _vr_engine
    if _vr_engine is None:
        _vr_engine = VRDecisionEngine()
    return _vr_engine

