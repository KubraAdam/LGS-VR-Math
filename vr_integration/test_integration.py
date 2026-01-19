"""
Integration Test Script
Tests the VR integration system end-to-end
"""

import os
import sys
import json

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vr_integration.vr_engine.vr_decision import get_vr_engine
from vr_integration.model_inference.predictor import get_predictor


def test_vr_engine():
    """Test VR decision engine"""
    print("=" * 50)
    print("Testing VR Decision Engine")
    print("=" * 50)
    
    engine = get_vr_engine()
    
    # Test cases
    test_cases = [
        {
            "alt_konu": "Alan ve Geometri",
            "soru_tipi": "Problem",
            "gorsel_bagimli": "bagimli",
            "expected": True
        },
        {
            "alt_konu": "Sayı Doğrusu",
            "soru_tipi": "Yorum",
            "gorsel_bagimli": None,
            "expected": True
        },
        {
            "alt_konu": "Denklemler",
            "soru_tipi": "Hesaplama",
            "gorsel_bagimli": None,
            "expected": False
        },
        {
            "alt_konu": "Karşılaştırma ve Sıralama",
            "soru_tipi": "Problem",
            "gorsel_bagimli": None,
            "expected": True
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = engine.should_activate_vr(
            test["alt_konu"],
            test["soru_tipi"],
            test["gorsel_bagimli"]
        )
        
        status = "✅" if result == test["expected"] else "❌"
        print(f"\nTest {i}: {status}")
        print(f"  Input: {test['alt_konu']} + {test['soru_tipi']}")
        print(f"  Expected: {test['expected']}, Got: {result}")
        
        if result:
            config = engine.get_vr_config(
                test["alt_konu"],
                test["soru_tipi"],
                test["gorsel_bagimli"]
            )
            print(f"  VR Config: {config['scene_type']} ({config['mode']})")


def test_model_predictor():
    """Test model predictor"""
    print("\n" + "=" * 50)
    print("Testing Model Predictor")
    print("=" * 50)
    
    try:
        predictor = get_predictor()
        
        # Test question
        test_question = """[SORU] Alanı 144 cm² olan karenin çevresi kaç cm'dir?
[A] 24
[B] 48
[C] 36
[D] 12
[GÖRSEL] Bu soru görsele bağlıdır."""
        
        print("\nTest Question:")
        print(test_question)
        print("\nRunning prediction...")
        
        result = predictor.predict(test_question, return_probs=False)
        
        print("\n✅ Prediction Result:")
        print(f"  Alt Konu: {result['alt_konu']}")
        print(f"  Soru Tipi: {result['soru_tipi']}")
        print(f"  Confidence: {result['confidence']}")
        
        # Test VR integration
        engine = get_vr_engine()
        vr_config = engine.get_vr_config(
            result['alt_konu'],
            result['soru_tipi'],
            "bagimli"
        )
        
        print("\n✅ VR Configuration:")
        print(json.dumps(vr_config, indent=2, ensure_ascii=False))
        
    except FileNotFoundError as e:
        print(f"\n❌ Model not found: {e}")
        print("   Please train the model first or check model_checkpoint directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("VR Integration Test Suite")
    print("=" * 50)
    
    # Test VR engine (no dependencies)
    test_vr_engine()
    
    # Test model predictor (requires trained model)
    test_model_predictor()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()

