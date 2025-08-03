"""
GPU Settings Utilities
======================

This module provides utilities for working with GPU settings data,
including analysis, optimization, and recommendations.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from database import DatabaseManager, GPUConfig, ModelConfig
from model_settings import ALL_MODELS, get_model_by_name, estimate_vram_requirement

@dataclass
class GPURecommendation:
    """GPU recommendation for a specific model."""
    model_name: str
    gpu_config: GPUConfig
    required_gpus: int
    total_cost_per_hour: float
    total_vram_gb: int
    efficiency_score: float
    reasoning: str

@dataclass
class CostAnalysis:
    """Cost analysis for GPU deployment."""
    gpu_config: GPUConfig
    gpu_count: int
    hourly_cost: float
    daily_cost: float
    monthly_cost: float
    yearly_cost: float
    cost_per_token: float
    roi_percentage: float

class GPUSettingsAnalyzer:
    """Analyzer for GPU settings and optimization."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_gpu_configs(self) -> List[GPUConfig]:
        """Get all active GPU configurations."""
        return self.db.get_gpu_configs(active_only=True)
    
    def analyze_model_gpu_compatibility(self, model_name: str) -> List[GPURecommendation]:
        """Analyze GPU compatibility for a specific model."""
        model = get_model_by_name(model_name)
        if not model:
            return []
        
        gpu_configs = self.get_gpu_configs()
        recommendations = []
        
        # Estimate VRAM requirement
        required_vram = estimate_vram_requirement(model.parameters_b, model.precision)
        
        for gpu in gpu_configs:
            # Check if GPU has sufficient VRAM
            if gpu.vram_gb >= required_vram:
                # Calculate efficiency score
                efficiency_score = self._calculate_efficiency_score(model, gpu)
                
                # Estimate required GPU count
                required_gpus = self._estimate_gpu_count(model, gpu)
                
                # Generate reasoning
                reasoning = self._generate_reasoning(model, gpu, required_gpus, required_vram)
                
                recommendation = GPURecommendation(
                    model_name=model_name,
                    gpu_config=gpu,
                    required_gpus=required_gpus,
                    total_cost_per_hour=gpu.cost_per_hour * required_gpus,
                    total_vram_gb=gpu.vram_gb * required_gpus,
                    efficiency_score=efficiency_score,
                    reasoning=reasoning
                )
                recommendations.append(recommendation)
        
        # Sort by efficiency score (higher is better)
        recommendations.sort(key=lambda r: r.efficiency_score, reverse=True)
        return recommendations
    
    def _calculate_efficiency_score(self, model: ModelConfig, gpu: GPUConfig) -> float:
        """Calculate efficiency score for GPU-model combination."""
        # Base score on cost per token
        cost_per_hour = gpu.cost_per_hour
        tokens_per_hour = model.tokens_per_gpu_tps * 3600
        cost_per_token = cost_per_hour / tokens_per_hour if tokens_per_hour > 0 else float('inf')
        
        # Normalize to 0-100 scale (lower cost per token = higher score)
        max_cost_per_token = 0.001  # $0.001 per token as baseline
        efficiency_score = max(0, 100 - (cost_per_token / max_cost_per_token) * 100)
        
        # Bonus for data center GPUs
        if gpu.gpu_type == "Data Center":
            efficiency_score += 10
        
        # Bonus for high VRAM efficiency
        vram_efficiency = gpu.vram_gb / gpu.cost_per_hour
        efficiency_score += min(20, vram_efficiency * 2)
        
        return min(100, efficiency_score)
    
    def _estimate_gpu_count(self, model: ModelConfig, gpu: GPUConfig) -> int:
        """Estimate required GPU count for a model."""
        # Base estimation on VRAM requirements
        required_vram = estimate_vram_requirement(model.parameters_b, model.precision)
        
        if gpu.vram_gb >= required_vram:
            return 1
        else:
            return max(1, int(required_vram / gpu.vram_gb) + 1)
    
    def _generate_reasoning(self, model: ModelConfig, gpu: GPUConfig, 
                           gpu_count: int, required_vram: int) -> str:
        """Generate reasoning for GPU recommendation."""
        reasoning_parts = []
        
        if gpu_count == 1:
            reasoning_parts.append(f"Single {gpu.name} sufficient for {model.name}")
        else:
            reasoning_parts.append(f"Requires {gpu_count}x {gpu.name} for {model.name}")
        
        reasoning_parts.append(f"VRAM: {gpu.vram_gb}GB available, {required_vram}GB required")
        reasoning_parts.append(f"Cost: ${gpu.cost_per_hour:.2f}/hour per GPU")
        
        if gpu.gpu_type == "Data Center":
            reasoning_parts.append("Data center GPU - optimized for inference")
        elif gpu.gpu_type == "Consumer":
            reasoning_parts.append("Consumer GPU - cost-effective option")
        
        return ". ".join(reasoning_parts)
    
    def analyze_cost_efficiency(self, gpu_config: GPUConfig, gpu_count: int, 
                              target_tps: int, input_price: float, output_price: float) -> CostAnalysis:
        """Analyze cost efficiency for a GPU deployment."""
        # Calculate costs
        hourly_cost = gpu_config.cost_per_hour * gpu_count
        daily_cost = hourly_cost * 24
        monthly_cost = daily_cost * 30
        yearly_cost = daily_cost * 365
        
        # Calculate revenue
        tokens_per_hour = target_tps * 3600
        input_tokens_per_hour = tokens_per_hour * 0.3  # Assume 30% input tokens
        output_tokens_per_hour = tokens_per_hour * 0.7  # Assume 70% output tokens
        
        input_revenue_per_hour = (input_tokens_per_hour / 1_000_000) * input_price
        output_revenue_per_hour = (output_tokens_per_hour / 1_000_000) * output_price
        total_revenue_per_hour = input_revenue_per_hour + output_revenue_per_hour
        
        # Calculate profit and ROI
        profit_per_hour = total_revenue_per_hour - hourly_cost
        roi_percentage = (profit_per_hour / hourly_cost) * 100 if hourly_cost > 0 else 0
        
        # Calculate cost per token
        cost_per_token = hourly_cost / tokens_per_hour if tokens_per_hour > 0 else 0
        
        return CostAnalysis(
            gpu_config=gpu_config,
            gpu_count=gpu_count,
            hourly_cost=hourly_cost,
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
            yearly_cost=yearly_cost,
            cost_per_token=cost_per_token,
            roi_percentage=roi_percentage
        )
    
    def get_best_gpu_for_budget(self, budget_per_hour: float, 
                               min_vram_gb: int = 0) -> Optional[GPUConfig]:
        """Get the best GPU configuration within budget constraints."""
        gpu_configs = self.get_gpu_configs()
        
        # Filter by budget and VRAM requirements
        affordable_gpus = [
            gpu for gpu in gpu_configs 
            if gpu.cost_per_hour <= budget_per_hour and gpu.vram_gb >= min_vram_gb
        ]
        
        if not affordable_gpus:
            return None
        
        # Sort by VRAM per dollar (efficiency metric)
        affordable_gpus.sort(key=lambda g: g.vram_gb / g.cost_per_hour, reverse=True)
        return affordable_gpus[0]
    
    def compare_gpu_configurations(self, model_name: str, target_tps: int) -> List[Dict[str, Any]]:
        """Compare different GPU configurations for a model."""
        model = get_model_by_name(model_name)
        if not model:
            return []
        
        gpu_configs = self.get_gpu_configs()
        comparisons = []
        
        for gpu in gpu_configs:
            # Check compatibility
            required_vram = estimate_vram_requirement(model.parameters_b, model.precision)
            if gpu.vram_gb < required_vram:
                continue
            
            # Calculate required GPU count
            required_gpus = max(1, int(target_tps / model.tokens_per_gpu_tps))
            
            # Analyze costs
            cost_analysis = self.analyze_cost_efficiency(
                gpu, required_gpus, target_tps, 
                float(model.input_price_per_m.replace('$', '') if model.input_price_per_m else 0),
                float(model.output_price_per_m.replace('$', '') if model.output_price_per_m else 0)
            )
            
            comparison = {
                "gpu_name": gpu.name,
                "gpu_type": gpu.gpu_type,
                "vram_gb": gpu.vram_gb,
                "cost_per_hour": gpu.cost_per_hour,
                "required_gpus": required_gpus,
                "total_cost_per_hour": cost_analysis.hourly_cost,
                "daily_cost": cost_analysis.daily_cost,
                "monthly_cost": cost_analysis.monthly_cost,
                "roi_percentage": cost_analysis.roi_percentage,
                "cost_per_token": cost_analysis.cost_per_token,
                "efficiency_score": self._calculate_efficiency_score(model, gpu)
            }
            comparisons.append(comparison)
        
        # Sort by ROI percentage
        comparisons.sort(key=lambda c: c["roi_percentage"], reverse=True)
        return comparisons

def main():
    """Example usage of GPU settings utilities."""
    db = DatabaseManager()
    analyzer = GPUSettingsAnalyzer(db)
    
    print("=== GPU Settings Analysis ===\n")
    
    # Get all GPU configurations
    gpu_configs = analyzer.get_gpu_configs()
    print(f"Available GPU Configurations ({len(gpu_configs)}):")
    for gpu in gpu_configs:
        print(f"  - {gpu.name}: ${gpu.cost_per_hour:.2f}/hour, {gpu.vram_gb}GB VRAM ({gpu.gpu_type})")
    
    print("\n" + "="*50 + "\n")
    
    # Analyze model compatibility
    model_name = "DeepSeek V3 671B"
    recommendations = analyzer.analyze_model_gpu_compatibility(model_name)
    
    print(f"GPU Recommendations for {model_name}:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n{i}. {rec.gpu_config.name}")
        print(f"   Efficiency Score: {rec.efficiency_score:.1f}/100")
        print(f"   Required GPUs: {rec.required_gpus}")
        print(f"   Total Cost/Hour: ${rec.total_cost_per_hour:.2f}")
        print(f"   Reasoning: {rec.reasoning}")
    
    print("\n" + "="*50 + "\n")
    
    # Compare GPU configurations
    comparisons = analyzer.compare_gpu_configurations(model_name, target_tps=1000)
    
    print(f"GPU Configuration Comparison for {model_name} (1000 TPS):")
    for i, comp in enumerate(comparisons[:3], 1):
        print(f"\n{i}. {comp['gpu_name']}")
        print(f"   ROI: {comp['roi_percentage']:.1f}%")
        print(f"   Monthly Cost: ${comp['monthly_cost']:.2f}")
        print(f"   Required GPUs: {comp['required_gpus']}")
        print(f"   Cost per Token: ${comp['cost_per_token']:.6f}")

if __name__ == "__main__":
    main() 