#!/usr/bin/env python3
"""
Human-AI Handoff Protocol - Task Complexity Assessor

Analyzes task descriptions to determine complexity and recommend
appropriate handoff strategies between human developers and AI tools.
"""

import json
import re
import yaml
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class HandoffStrategy(Enum):
    """Available handoff strategies based on task complexity."""
    AI_FIRST = "ai_first"
    AI_WITH_REVIEW = "ai_with_review"
    HUMAN_FIRST = "human_first"
    HUMAN_ONLY = "human_only"
    COLLABORATIVE = "collaborative"


@dataclass
class ComplexityFactors:
    """Individual complexity assessment factors."""
    security_sensitive: float
    creative_problem_solving: float
    integration_complexity: float
    domain_expertise: float
    time_constraints: float
    business_criticality: float


@dataclass
class HandoffRecommendation:
    """Handoff strategy recommendation with reasoning."""
    strategy: HandoffStrategy
    confidence: float
    complexity_score: float
    reasoning: str
    factors: ComplexityFactors
    estimated_effort: Optional[str] = None
    risk_level: Optional[str] = None


class TaskComplexityAssessor:
    """Analyzes tasks and recommends optimal human-AI handoff strategies."""
    
    def __init__(self, config_path: str = "handoff_config.yaml"):
        """Initialize assessor with configuration."""
        self.config = self._load_config(config_path)
        self.security_keywords = self._load_security_keywords()
        self.creativity_keywords = self._load_creativity_keywords()
        self.integration_keywords = self._load_integration_keywords()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                'complexity_thresholds': {
                    'ai_first': 0.3,
                    'ai_with_review': 0.7,
                    'human_first': 0.9,
                    'human_only': 1.0
                },
                'assessment_criteria': {
                    'security_weight': 0.25,
                    'creativity_weight': 0.20,
                    'integration_weight': 0.20,
                    'domain_weight': 0.15,
                    'time_weight': 0.10,
                    'business_weight': 0.10
                }
            }
    
    def _load_security_keywords(self) -> List[str]:
        """Load security-sensitive keywords."""
        return [
            'authentication', 'authorization', 'jwt', 'oauth', 'token',
            'password', 'encrypt', 'decrypt', 'ssl', 'tls', 'certificate',
            'security', 'vulnerability', 'audit', 'compliance', 'gdpr',
            'permissions', 'roles', 'access control', 'firewall', 'cors',
            'xss', 'csrf', 'sql injection', 'sanitize', 'validate input'
        ]
    
    def _load_creativity_keywords(self) -> List[str]:
        """Load creative problem-solving keywords."""
        return [
            'design', 'architecture', 'algorithm', 'optimize', 'performance',
            'user experience', 'ui', 'ux', 'innovative', 'creative',
            'brainstorm', 'solution', 'approach', 'strategy', 'novel',
            'research', 'experiment', 'prototype', 'proof of concept'
        ]
    
    def _load_integration_keywords(self) -> List[str]:
        """Load system integration complexity keywords."""
        return [
            'integration', 'api', 'microservice', 'database', 'migration',
            'deployment', 'ci/cd', 'pipeline', 'orchestration', 'kubernetes',
            'docker', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
            'monitoring', 'logging', 'distributed', 'scalability'
        ]
    
    def assess_task(self, task_description: str, context: Optional[Dict] = None) -> HandoffRecommendation:
        """
        Analyze task complexity and recommend handoff strategy.
        
        Args:
            task_description: Description of the task to be completed
            context: Optional context including priority, deadline, team info
            
        Returns:
            HandoffRecommendation with strategy and reasoning
        """
        # Calculate complexity factors
        factors = self._calculate_complexity_factors(task_description, context or {})
        
        # Calculate overall complexity score
        complexity_score = self._calculate_complexity_score(factors)
        
        # Determine handoff strategy
        strategy = self._recommend_handoff_strategy(complexity_score, factors)
        
        # Calculate confidence based on factor clarity
        confidence = self._calculate_confidence(factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(strategy, factors, complexity_score)
        
        # Estimate effort and risk
        effort = self._estimate_effort(complexity_score, strategy)
        risk = self._assess_risk_level(factors, strategy)
        
        return HandoffRecommendation(
            strategy=strategy,
            confidence=confidence,
            complexity_score=complexity_score,
            reasoning=reasoning,
            factors=factors,
            estimated_effort=effort,
            risk_level=risk
        )
    
    def _calculate_complexity_factors(self, task_description: str, context: Dict) -> ComplexityFactors:
        """Calculate individual complexity factors from task analysis."""
        text = task_description.lower()
        
        return ComplexityFactors(
            security_sensitive=self._check_security_sensitivity(text),
            creative_problem_solving=self._assess_creativity_needed(text),
            integration_complexity=self._analyze_integration_scope(text),
            domain_expertise=self._evaluate_domain_knowledge(text),
            time_constraints=self._assess_time_pressure(text, context),
            business_criticality=self._assess_business_impact(text, context)
        )
    
    def _check_security_sensitivity(self, text: str) -> float:
        """Check for security-sensitive keywords and patterns."""
        security_score = 0.0
        keyword_matches = 0
        
        for keyword in self.security_keywords:
            if keyword in text:
                keyword_matches += 1
                # Weight certain keywords higher
                if keyword in ['authentication', 'authorization', 'encryption', 'vulnerability']:
                    security_score += 0.3
                else:
                    security_score += 0.1
        
        # Check for security-related patterns
        if re.search(r'password|credential|secret|key', text):
            security_score += 0.4
        if re.search(r'user.*data|personal.*information|sensitive.*data', text):
            security_score += 0.3
        if re.search(r'production|live|customer', text):
            security_score += 0.2
            
        return min(security_score, 1.0)
    
    def _assess_creativity_needed(self, text: str) -> float:
        """Assess need for creative problem-solving."""
        creativity_score = 0.0
        
        for keyword in self.creativity_keywords:
            if keyword in text:
                creativity_score += 0.15
        
        # Check for creative thinking patterns
        if re.search(r'new|novel|innovative|creative|design|architect', text):
            creativity_score += 0.3
        if re.search(r'improve|optimize|enhance|better', text):
            creativity_score += 0.2
        if re.search(r'problem|solution|approach|strategy', text):
            creativity_score += 0.2
        if re.search(r'user.*experience|ui|ux|interface', text):
            creativity_score += 0.4
            
        return min(creativity_score, 1.0)
    
    def _analyze_integration_scope(self, text: str) -> float:
        """Analyze system integration complexity."""
        integration_score = 0.0
        
        for keyword in self.integration_keywords:
            if keyword in text:
                integration_score += 0.1
        
        # Check for integration complexity patterns
        if re.search(r'multiple.*service|microservice|distributed', text):
            integration_score += 0.4
        if re.search(r'database|migration|schema', text):
            integration_score += 0.3
        if re.search(r'api|endpoint|integration', text):
            integration_score += 0.3
        if re.search(r'deploy|pipeline|ci/cd', text):
            integration_score += 0.3
            
        return min(integration_score, 1.0)
    
    def _evaluate_domain_knowledge(self, text: str) -> float:
        """Evaluate domain expertise requirements."""
        domain_score = 0.0
        
        # Check for domain-specific terminology
        domain_indicators = [
            'machine learning', 'ai', 'blockchain', 'cryptocurrency',
            'financial', 'healthcare', 'compliance', 'regulatory',
            'real-time', 'embedded', 'iot', 'mobile', 'game',
            'graphics', 'video', 'audio', 'networking', 'protocol'
        ]
        
        for indicator in domain_indicators:
            if indicator in text:
                domain_score += 0.2
        
        # Check for specialized technology mentions
        if re.search(r'tensorflow|pytorch|react native|kubernetes|elasticsearch', text):
            domain_score += 0.3
            
        return min(domain_score, 1.0)
    
    def _assess_time_pressure(self, text: str, context: Dict) -> float:
        """Assess time constraints and urgency."""
        time_score = 0.0
        
        # Check for urgency keywords
        urgency_keywords = ['urgent', 'asap', 'immediately', 'critical', 'hotfix', 'emergency']
        for keyword in urgency_keywords:
            if keyword in text:
                time_score += 0.3
        
        # Check context for deadline information
        if context.get('priority') == 'high':
            time_score += 0.4
        elif context.get('priority') == 'critical':
            time_score += 0.6
            
        if context.get('deadline'):
            # Simple heuristic: shorter deadlines increase complexity
            deadline_days = context.get('deadline_days', 7)
            if deadline_days <= 1:
                time_score += 0.6
            elif deadline_days <= 3:
                time_score += 0.4
            elif deadline_days <= 7:
                time_score += 0.2
                
        return min(time_score, 1.0)
    
    def _assess_business_impact(self, text: str, context: Dict) -> float:
        """Assess business criticality and impact."""
        business_score = 0.0
        
        # Check for business impact keywords
        impact_keywords = ['revenue', 'customer', 'user', 'production', 'critical', 'business']
        for keyword in impact_keywords:
            if keyword in text:
                business_score += 0.15
        
        # Check context for business criticality
        if context.get('business_critical', False):
            business_score += 0.5
        if context.get('customer_facing', False):
            business_score += 0.3
            
        return min(business_score, 1.0)
    
    def _calculate_complexity_score(self, factors: ComplexityFactors) -> float:
        """Calculate weighted complexity score from individual factors."""
        weights = self.config['assessment_criteria']
        
        score = (
            factors.security_sensitive * weights['security_weight'] +
            factors.creative_problem_solving * weights['creativity_weight'] +
            factors.integration_complexity * weights['integration_weight'] +
            factors.domain_expertise * weights['domain_weight'] +
            factors.time_constraints * weights['time_weight'] +
            factors.business_criticality * weights['business_weight']
        )
        
        return min(score, 1.0)
    
    def _recommend_handoff_strategy(self, complexity_score: float, factors: ComplexityFactors) -> HandoffStrategy:
        """Recommend handoff strategy based on complexity analysis."""
        thresholds = self.config['complexity_thresholds']
        
        # Special cases override threshold-based decisions
        if factors.security_sensitive > 0.7 and factors.business_criticality > 0.5:
            return HandoffStrategy.HUMAN_ONLY
        
        if factors.creative_problem_solving > 0.8:
            return HandoffStrategy.COLLABORATIVE
        
        # Threshold-based decisions
        if complexity_score >= thresholds['human_only']:
            return HandoffStrategy.HUMAN_ONLY
        elif complexity_score >= thresholds['human_first']:
            return HandoffStrategy.HUMAN_FIRST
        elif complexity_score >= thresholds['ai_with_review']:
            return HandoffStrategy.AI_WITH_REVIEW
        else:
            return HandoffStrategy.AI_FIRST
    
    def _calculate_confidence(self, factors: ComplexityFactors) -> float:
        """Calculate confidence in the assessment based on factor clarity."""
        # Higher confidence when factors are clearly high or low
        factor_values = [
            factors.security_sensitive,
            factors.creative_problem_solving,
            factors.integration_complexity,
            factors.domain_expertise,
            factors.time_constraints,
            factors.business_criticality
        ]
        
        # Confidence is higher when factors are not ambiguous (close to 0.5)
        clarity_scores = [abs(f - 0.5) * 2 for f in factor_values]
        average_clarity = sum(clarity_scores) / len(clarity_scores)
        
        # Base confidence + clarity bonus
        return min(0.6 + (average_clarity * 0.4), 1.0)
    
    def _generate_reasoning(self, strategy: HandoffStrategy, factors: ComplexityFactors, score: float) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasons = []
        
        if factors.security_sensitive > 0.5:
            reasons.append(f"Security sensitivity ({factors.security_sensitive:.1f}) requires careful human oversight")
        
        if factors.creative_problem_solving > 0.6:
            reasons.append(f"Creative problem-solving needs ({factors.creative_problem_solving:.1f}) benefit from human insight")
        
        if factors.integration_complexity > 0.6:
            reasons.append(f"High integration complexity ({factors.integration_complexity:.1f}) needs experienced coordination")
        
        if factors.domain_expertise > 0.6:
            reasons.append(f"Domain expertise requirements ({factors.domain_expertise:.1f}) favor human knowledge")
        
        if factors.time_constraints > 0.7:
            reasons.append(f"Time pressure ({factors.time_constraints:.1f}) may require human judgment for trade-offs")
        
        if factors.business_criticality > 0.6:
            reasons.append(f"Business criticality ({factors.business_criticality:.1f}) warrants human validation")
        
        if not reasons:
            if score < 0.3:
                reasons.append("Low complexity task suitable for AI automation with quality gates")
            else:
                reasons.append("Moderate complexity suggests balanced human-AI collaboration")
        
        return "; ".join(reasons)
    
    def _estimate_effort(self, complexity_score: float, strategy: HandoffStrategy) -> str:
        """Estimate implementation effort based on complexity and strategy."""
        base_hours = complexity_score * 8  # 0-8 hour base range
        
        strategy_multipliers = {
            HandoffStrategy.AI_FIRST: 0.5,
            HandoffStrategy.AI_WITH_REVIEW: 0.7,
            HandoffStrategy.COLLABORATIVE: 1.2,
            HandoffStrategy.HUMAN_FIRST: 1.5,
            HandoffStrategy.HUMAN_ONLY: 2.0
        }
        
        estimated_hours = base_hours * strategy_multipliers[strategy]
        
        if estimated_hours < 2:
            return "1-2 hours"
        elif estimated_hours < 4:
            return "2-4 hours"
        elif estimated_hours < 8:
            return "4-8 hours"
        elif estimated_hours < 16:
            return "1-2 days"
        else:
            return "2+ days"
    
    def _assess_risk_level(self, factors: ComplexityFactors, strategy: HandoffStrategy) -> str:
        """Assess implementation risk level."""
        risk_factors = [
            factors.security_sensitive * 2,  # Security issues are high risk
            factors.business_criticality * 1.5,  # Business impact amplifies risk
            factors.integration_complexity,
            factors.time_constraints * 0.5  # Time pressure can increase risk
        ]
        
        max_risk = max(risk_factors)
        
        if max_risk > 1.5:
            return "High"
        elif max_risk > 0.8:
            return "Medium"
        else:
            return "Low"


def main():
    """CLI interface for task complexity assessment."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Assess task complexity for human-AI handoff")
    parser.add_argument("--task", required=True, help="Task description to analyze")
    parser.add_argument("--config", default="handoff_config.yaml", help="Configuration file path")
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], help="Task priority")
    parser.add_argument("--deadline-days", type=int, help="Days until deadline")
    parser.add_argument("--business-critical", action="store_true", help="Mark as business critical")
    parser.add_argument("--customer-facing", action="store_true", help="Mark as customer facing")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--debug", action="store_true", help="Show detailed factor analysis")
    
    args = parser.parse_args()
    
    # Build context from CLI arguments
    context = {}
    if args.priority:
        context['priority'] = args.priority
    if args.deadline_days:
        context['deadline_days'] = args.deadline_days
    if args.business_critical:
        context['business_critical'] = True
    if args.customer_facing:
        context['customer_facing'] = True
    
    # Perform assessment
    assessor = TaskComplexityAssessor(args.config)
    recommendation = assessor.assess_task(args.task, context)
    
    # Output results
    if args.output == "json":
        result = {
            'strategy': recommendation.strategy.value,
            'confidence': recommendation.confidence,
            'complexity_score': recommendation.complexity_score,
            'reasoning': recommendation.reasoning,
            'estimated_effort': recommendation.estimated_effort,
            'risk_level': recommendation.risk_level
        }
        if args.debug:
            result['factors'] = {
                'security_sensitive': recommendation.factors.security_sensitive,
                'creative_problem_solving': recommendation.factors.creative_problem_solving,
                'integration_complexity': recommendation.factors.integration_complexity,
                'domain_expertise': recommendation.factors.domain_expertise,
                'time_constraints': recommendation.factors.time_constraints,
                'business_criticality': recommendation.factors.business_criticality
            }
        print(json.dumps(result, indent=2))
    else:
        print(f"Task Complexity Assessment")
        print(f"========================")
        print(f"Strategy: {recommendation.strategy.value.replace('_', ' ').title()}")
        print(f"Confidence: {recommendation.confidence:.0%}")
        print(f"Complexity Score: {recommendation.complexity_score:.2f}")
        print(f"Estimated Effort: {recommendation.estimated_effort}")
        print(f"Risk Level: {recommendation.risk_level}")
        print(f"Reasoning: {recommendation.reasoning}")
        
        if args.debug:
            print(f"\nDetailed Factor Analysis:")
            print(f"  Security Sensitive: {recommendation.factors.security_sensitive:.2f}")
            print(f"  Creative Problem Solving: {recommendation.factors.creative_problem_solving:.2f}")
            print(f"  Integration Complexity: {recommendation.factors.integration_complexity:.2f}")
            print(f"  Domain Expertise: {recommendation.factors.domain_expertise:.2f}")
            print(f"  Time Constraints: {recommendation.factors.time_constraints:.2f}")
            print(f"  Business Criticality: {recommendation.factors.business_criticality:.2f}")


if __name__ == "__main__":
    main()