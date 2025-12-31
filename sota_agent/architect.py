"""
AI-Powered Architecture Advisor

Analyzes natural language use case briefs and recommends the optimal
SOTA Agent Framework architecture, including:
- Learning level (1-5)
- Schemas to use
- Features to enable
- Integrations needed
- Architecture patterns

Usage:
    sota-architect "I need a fraud detection system with memory and self-improvement"
    
    Or interactively:
    sota-architect --interactive
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ComplexityLevel(Enum):
    """Complexity levels mapping to learning levels."""
    SIMPLE = 1          # Simple chatbot
    CONTEXTUAL = 2      # Context-aware with memory
    PRODUCTION = 3      # Production API with monitoring
    ADVANCED = 4        # Complex workflows with planning
    EXPERT = 5          # Multi-agent with A2A


@dataclass
class ArchitectureRecommendation:
    """Complete architecture recommendation."""
    level: ComplexityLevel
    level_name: str
    confidence: float
    
    # Schemas
    input_schema: str
    output_schema: str
    
    # Core features
    features: List[str]
    
    # Optional integrations
    integrations: List[str]
    
    # Reasoning
    reasoning: str
    
    # Estimated effort
    estimated_hours: str
    
    # Code generation params
    generation_params: Dict[str, Any]


class ArchitectureAdvisor:
    """
    AI-powered architecture advisor that analyzes use case briefs
    and recommends optimal SOTA Agent Framework architecture.
    """
    
    def __init__(self):
        """Initialize the advisor with pattern matchers and rules."""
        
        # Complexity indicators (patterns that suggest higher complexity)
        self.complexity_patterns = {
            ComplexityLevel.SIMPLE: [
                r'\bsimple\b', r'\bbasic\b', r'\bquick\b', r'\bchatbot\b',
                r'\bfaq\b', r'\bquestion.?answer', r'\brespond\b'
            ],
            ComplexityLevel.CONTEXTUAL: [
                r'\bmemory\b', r'\bcontext\b', r'\bremember\b', r'\bhistory\b',
                r'\bconversation\b', r'\bmulti.?turn\b', r'\bpersonaliz'
            ],
            ComplexityLevel.PRODUCTION: [
                r'\bproduction\b', r'\bapi\b', r'\brest\b', r'\bmicroservice\b',
                r'\bmonitor', r'\bscale', r'\bhealth.?check\b', r'\bdeploy'
            ],
            ComplexityLevel.ADVANCED: [
                r'\bplan', r'\bworkflow\b', r'\bcomplex\b', r'\bmulti.?step\b',
                r'\boptimiz', r'\bself.?improv', r'\bfeedback\b', r'\bcritique'
            ],
            ComplexityLevel.EXPERT: [
                r'\bmulti.?agent\b', r'\bcollaborat', r'\bdistribut',
                r'\ba2a\b', r'\bcross.?framework\b', r'\bmarketplace\b',
                r'\benterprise\b', r'\bscale.?massiv'
            ]
        }
        
        # Feature indicators
        self.feature_patterns = {
            'memory': [
                r'\bmemory\b', r'\bremember\b', r'\brecall\b', r'\bforget\b',
                r'\bcontext\b', r'\bhistory\b'
            ],
            'langgraph': [
                r'\bplan\b', r'\bworkflow\b', r'\bgraph\b', r'\borch',
                r'\bmulti.?step\b', r'\bsequence\b'
            ],
            'mcp': [
                r'\btool\b', r'\bexternal\b', r'\bapi\b', r'\bintegrat',
                r'\bservice\b', r'\bmcp\b'
            ],
            'a2a': [
                r'\ba2a\b', r'\bmulti.?agent\b', r'\bcollaborat',
                r'\bcross.?framework\b', r'\binterop'
            ],
            'monitoring': [
                r'\bmonitor\b', r'\bobserv', r'\btelemetry\b', r'\btrace\b',
                r'\blog\b', r'\bmetric\b'
            ],
            'optimization': [
                r'\boptimiz\b', r'\bimprov\b', r'\btune\b', r'\bself.?learn',
                r'\bfeedback\b', r'\brl\b', r'\breinforce'
            ],
            'benchmarking': [
                r'\bbenchmark\b', r'\beval', r'\btest\b', r'\baccuracy\b',
                r'\bperformance\b', r'\bquality\b'
            ],
            'databricks': [
                r'\bdatabricks\b', r'\bunity.?catalog\b', r'\bmlflow\b',
                r'\bspark\b', r'\bdelta\b'
            ]
        }
        
        # Domain indicators
        self.domain_patterns = {
            'fraud': [r'\bfraud\b', r'\bscam\b', r'\brisk\b', r'\bsuspicious\b'],
            'customer_support': [r'\bsupport\b', r'\bticket\b', r'\bhelp.?desk\b', r'\bcustomer\b'],
            'analytics': [r'\banalytics\b', r'\binsight\b', r'\bdata\b', r'\breport\b'],
            'healthcare': [r'\bhealth', r'\bmedical\b', r'\bpatient\b', r'\bdiagnos'],
            'finance': [r'\bfinance\b', r'\bbanking\b', r'\btrade\b', r'\binvest'],
            'ecommerce': [r'\becommerce\b', r'\bshopping\b', r'\bproduct\b', r'\bcart\b'],
            'hr': [r'\bhr\b', r'\brecruit', r'\bhiring\b', r'\bemployee\b'],
            'legal': [r'\blegal\b', r'\bcontract\b', r'\bcompliance\b', r'\bregulatr']
        }
    
    def analyze_brief(self, brief: str) -> ArchitectureRecommendation:
        """
        Analyze a use case brief and recommend architecture.
        
        Args:
            brief: Natural language description of the use case
            
        Returns:
            ArchitectureRecommendation with all details
        """
        brief_lower = brief.lower()
        
        # Step 1: Determine complexity level
        level, level_confidence = self._determine_complexity(brief_lower)
        
        # Step 2: Identify required features
        features = self._identify_features(brief_lower, level)
        
        # Step 3: Identify integrations
        integrations = self._identify_integrations(brief_lower, level)
        
        # Step 4: Recommend schemas
        input_schema, output_schema = self._recommend_schemas(level)
        
        # Step 5: Detect domain
        domain = self._detect_domain(brief_lower)
        
        # Step 6: Generate reasoning
        reasoning = self._generate_reasoning(brief, level, features, integrations, domain)
        
        # Step 7: Estimate effort
        estimated_hours = self._estimate_effort(level, features)
        
        # Step 8: Create generation params
        generation_params = self._create_generation_params(
            level, domain, features, integrations
        )
        
        return ArchitectureRecommendation(
            level=level,
            level_name=self._get_level_name(level),
            confidence=level_confidence,
            input_schema=input_schema,
            output_schema=output_schema,
            features=features,
            integrations=integrations,
            reasoning=reasoning,
            estimated_hours=estimated_hours,
            generation_params=generation_params
        )
    
    def _determine_complexity(self, brief: str) -> Tuple[ComplexityLevel, float]:
        """Determine complexity level from brief."""
        scores = {}
        
        # Score each level based on pattern matches
        for level, patterns in self.complexity_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, brief))
            scores[level] = score
        
        # Get level with highest score
        if not any(scores.values()):
            # Default to SIMPLE if no patterns match
            return ComplexityLevel.SIMPLE, 0.5
        
        max_level = max(scores.items(), key=lambda x: x[1])
        
        # Calculate confidence (0-1)
        total_matches = sum(scores.values())
        confidence = min(max_level[1] / max(total_matches, 1), 1.0)
        
        # Boost confidence if multiple levels suggest same direction
        if max_level[1] > 0:
            confidence = min(confidence + 0.2, 1.0)
        
        return max_level[0], confidence
    
    def _identify_features(self, brief: str, level: ComplexityLevel) -> List[str]:
        """Identify required features from brief."""
        features = []
        
        for feature, patterns in self.feature_patterns.items():
            if any(re.search(pattern, brief) for pattern in patterns):
                features.append(feature)
        
        # Add default features based on level
        level_defaults = {
            ComplexityLevel.SIMPLE: [],
            ComplexityLevel.CONTEXTUAL: ['memory'],
            ComplexityLevel.PRODUCTION: ['memory', 'monitoring'],
            ComplexityLevel.ADVANCED: ['memory', 'monitoring', 'langgraph', 'optimization'],
            ComplexityLevel.EXPERT: ['memory', 'monitoring', 'langgraph', 'optimization', 'benchmarking']
        }
        
        # Add defaults if not already present
        for default in level_defaults.get(level, []):
            if default not in features:
                features.append(default)
        
        return features
    
    def _identify_integrations(self, brief: str, level: ComplexityLevel) -> List[str]:
        """Identify required integrations."""
        integrations = []
        
        # Check for explicit integration mentions
        if any(re.search(pattern, brief) for pattern in self.feature_patterns['mcp']):
            integrations.append('MCP')
        
        if any(re.search(pattern, brief) for pattern in self.feature_patterns['a2a']):
            integrations.append('A2A')
        
        if any(re.search(pattern, brief) for pattern in self.feature_patterns['databricks']):
            integrations.append('Databricks')
        
        # Add LangGraph for Advanced+ levels
        if level.value >= ComplexityLevel.ADVANCED.value:
            if 'LangGraph' not in integrations:
                integrations.append('LangGraph')
        
        return integrations
    
    def _recommend_schemas(self, level: ComplexityLevel) -> Tuple[str, str]:
        """Recommend input/output schemas based on level."""
        schema_map = {
            ComplexityLevel.SIMPLE: ('ChatInput', 'ChatOutput'),
            ComplexityLevel.CONTEXTUAL: ('ContextAwareInput', 'ContextAwareOutput'),
            ComplexityLevel.PRODUCTION: ('APIRequest', 'APIResponse'),
            ComplexityLevel.ADVANCED: ('WorkflowInput', 'WorkflowOutput'),
            ComplexityLevel.EXPERT: ('CollaborationRequest', 'CollaborationResponse')
        }
        return schema_map[level]
    
    def _detect_domain(self, brief: str) -> Optional[str]:
        """Detect the domain from the brief."""
        domain_scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, brief))
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return 'general'
    
    def _generate_reasoning(
        self,
        brief: str,
        level: ComplexityLevel,
        features: List[str],
        integrations: List[str],
        domain: str
    ) -> str:
        """Generate human-readable reasoning for the recommendation."""
        reasoning_parts = []
        
        # Level reasoning
        level_reasons = {
            ComplexityLevel.SIMPLE: "Based on your requirements, a simple chatbot architecture is sufficient.",
            ComplexityLevel.CONTEXTUAL: "Your use case requires context awareness and memory capabilities.",
            ComplexityLevel.PRODUCTION: "This is a production-grade system requiring robust API design and monitoring.",
            ComplexityLevel.ADVANCED: "This is a complex workflow requiring planning, execution, and self-improvement loops.",
            ComplexityLevel.EXPERT: "This is an expert-level multi-agent system requiring advanced collaboration."
        }
        reasoning_parts.append(level_reasons[level])
        
        # Domain reasoning
        if domain != 'general':
            reasoning_parts.append(f"Detected domain: {domain.replace('_', ' ').title()}")
        
        # Feature reasoning
        if features:
            feature_names = ', '.join(features)
            reasoning_parts.append(f"Required features: {feature_names}")
        
        # Integration reasoning
        if integrations:
            integration_names = ', '.join(integrations)
            reasoning_parts.append(f"Recommended integrations: {integration_names}")
        
        return ' '.join(reasoning_parts)
    
    def _estimate_effort(self, level: ComplexityLevel, features: List[str]) -> str:
        """Estimate development effort."""
        base_hours = {
            ComplexityLevel.SIMPLE: (2, 4),
            ComplexityLevel.CONTEXTUAL: (4, 8),
            ComplexityLevel.PRODUCTION: (8, 16),
            ComplexityLevel.ADVANCED: (16, 32),
            ComplexityLevel.EXPERT: (32, 64)
        }
        
        min_hours, max_hours = base_hours[level]
        
        # Add hours for additional features
        extra_hours = len(features) * 2
        max_hours += extra_hours
        
        return f"{min_hours}-{max_hours} hours"
    
    def _create_generation_params(
        self,
        level: ComplexityLevel,
        domain: str,
        features: List[str],
        integrations: List[str]
    ) -> Dict[str, Any]:
        """Create parameters for code generation."""
        return {
            'level': level.value,
            'domain': domain,
            'features': {
                'memory': 'memory' in features,
                'langgraph': 'langgraph' in features,
                'mcp': 'mcp' in features or 'MCP' in integrations,
                'a2a': 'a2a' in features or 'A2A' in integrations,
                'monitoring': 'monitoring' in features,
                'optimization': 'optimization' in features,
                'benchmarking': 'benchmarking' in features,
                'databricks': 'databricks' in features or 'Databricks' in integrations
            },
            'schemas': {
                'input': self._recommend_schemas(level)[0],
                'output': self._recommend_schemas(level)[1]
            }
        }
    
    def _get_level_name(self, level: ComplexityLevel) -> str:
        """Get human-readable level name."""
        names = {
            ComplexityLevel.SIMPLE: "Level 1: Simple Chatbot",
            ComplexityLevel.CONTEXTUAL: "Level 2: Context-Aware Agent",
            ComplexityLevel.PRODUCTION: "Level 3: Production API",
            ComplexityLevel.ADVANCED: "Level 4: Complex Workflow",
            ComplexityLevel.EXPERT: "Level 5: Multi-Agent System"
        }
        return names[level]
    
    def print_recommendation(self, rec: ArchitectureRecommendation):
        """Pretty print the recommendation."""
        print("\n" + "="*70)
        print("🏗️  SOTA Agent Framework - Architecture Recommendation")
        print("="*70)
        
        print(f"\n📊 Recommended Level: {rec.level_name}")
        print(f"   Confidence: {rec.confidence:.0%}")
        
        print(f"\n📋 Schemas:")
        print(f"   Input:  {rec.input_schema}")
        print(f"   Output: {rec.output_schema}")
        
        if rec.features:
            print(f"\n✨ Core Features:")
            for feature in rec.features:
                print(f"   • {feature}")
        
        if rec.integrations:
            print(f"\n🔌 Integrations:")
            for integration in rec.integrations:
                print(f"   • {integration}")
        
        print(f"\n💡 Reasoning:")
        print(f"   {rec.reasoning}")
        
        print(f"\n⏱️  Estimated Effort: {rec.estimated_hours}")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Run: sota-learn start {rec.level.value}")
        print(f"   2. Or: sota-generate <project_name> --level {rec.level.value}")
        print(f"   3. Enable features as needed")
        
        print("\n" + "="*70 + "\n")


def main():
    """CLI entry point for architecture advisor."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SOTA Agent Framework Architecture Advisor',
        epilog='Example: sota-architect "Build a fraud detection system with memory"'
    )
    parser.add_argument(
        'brief',
        nargs='*',
        help='Natural language description of your use case'
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Interactive mode with prompts'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    args = parser.parse_args()
    
    advisor = ArchitectureAdvisor()
    
    # Get brief
    if args.interactive:
        print("\n🏗️  SOTA Agent Framework - Architecture Advisor\n")
        print("Describe your use case in natural language, and I'll recommend")
        print("the optimal architecture from our framework.\n")
        brief = input("📝 Use case brief: ").strip()
    elif args.brief:
        brief = ' '.join(args.brief)
    else:
        parser.print_help()
        sys.exit(1)
    
    if not brief:
        print("❌ Error: Please provide a use case description")
        sys.exit(1)
    
    # Analyze and recommend
    recommendation = advisor.analyze_brief(brief)
    
    # Output
    if args.json:
        import json
        output = {
            'level': recommendation.level.value,
            'level_name': recommendation.level_name,
            'confidence': recommendation.confidence,
            'input_schema': recommendation.input_schema,
            'output_schema': recommendation.output_schema,
            'features': recommendation.features,
            'integrations': recommendation.integrations,
            'reasoning': recommendation.reasoning,
            'estimated_hours': recommendation.estimated_hours,
            'generation_params': recommendation.generation_params
        }
        print(json.dumps(output, indent=2))
    else:
        advisor.print_recommendation(recommendation)


if __name__ == '__main__':
    main()

