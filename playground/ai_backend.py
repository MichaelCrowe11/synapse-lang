"""
AI Backend for Quantum Trinity IDE
Provides intelligent code assistance, error explanations, and learning features
"""

from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit
import openai
import anthropic
import json
import re
from typing import Dict, List, Any
import asyncio
from datetime import datetime
import numpy as np
from dataclasses import dataclass
import os

# Create Blueprint for AI routes
ai_bp = Blueprint('ai', __name__)

@dataclass
class CodeContext:
    """Context for code analysis"""
    code: str
    language: str
    position: Dict[str, int]
    history: List[Dict]
    user_profile: Dict

class QuantumAIEngine:
    """AI engine for quantum programming assistance"""
    
    def __init__(self):
        # Initialize AI clients (use environment variables for API keys)
        self.openai_client = None
        self.anthropic_client = None
        
        # Try to initialize AI providers if keys are available
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
        
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        
        # Knowledge base for each language
        self.knowledge_base = self._load_knowledge_base()
        
        # Pattern matchers for code analysis
        self.patterns = self._compile_patterns()
        
        # Cache for frequent requests
        self.cache = {}
        
    def _load_knowledge_base(self):
        """Load quantum programming knowledge base"""
        return {
            'synapse': {
                'concepts': {
                    'uncertainty': {
                        'description': 'Propagation of measurement uncertainties',
                        'syntax': 'uncertain var = value ± error',
                        'operations': ['addition', 'multiplication', 'monte_carlo']
                    },
                    'parallel': {
                        'description': 'Parallel computation blocks',
                        'syntax': 'parallel { task1; task2; }',
                        'use_cases': ['independent calculations', 'parameter sweeps']
                    }
                },
                'common_errors': {
                    'uncertainty_syntax': 'Use ± symbol for uncertainty',
                    'correlation_missing': 'Specify correlations between variables'
                }
            },
            'qubit-flow': {
                'concepts': {
                    'superposition': {
                        'description': 'Quantum state in multiple states simultaneously',
                        'gates': ['H', 'Ry'],
                        'notation': 'α|0⟩ + β|1⟩'
                    },
                    'entanglement': {
                        'description': 'Quantum correlation between qubits',
                        'gates': ['CNOT', 'CZ'],
                        'states': ['Bell states', 'GHZ states']
                    }
                },
                'gate_properties': {
                    'H': {'matrix': [[1, 1], [1, -1]], 'scale': 1/np.sqrt(2)},
                    'X': {'matrix': [[0, 1], [1, 0]]},
                    'CNOT': {'control': True, 'target': True}
                }
            },
            'quantum-net': {
                'concepts': {
                    'topology': {
                        'description': 'Network structure and connections',
                        'types': ['star', 'ring', 'mesh', 'tree']
                    },
                    'protocols': {
                        'description': 'Communication protocols',
                        'examples': ['teleportation', 'QKD', 'entanglement_swapping']
                    }
                }
            }
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for code analysis"""
        return {
            'synapse': {
                'uncertain': re.compile(r'uncertain\s+(\w+)\s*=\s*([\d.]+)\s*±\s*([\d.]+)'),
                'parallel': re.compile(r'parallel\s*\{([^}]*)\}'),
                'monte_carlo': re.compile(r'monte_carlo\s*\([^)]*\)'),
                'correlation': re.compile(r'correlation\s*\(([^)]+)\)')
            },
            'qubit-flow': {
                'qubit': re.compile(r'qubit\s+(\w+)\s*=\s*\|([01])\⟩'),
                'gate': re.compile(r'([HXYZRx-z]+)\[([^\]]+)\]'),
                'measure': re.compile(r'measure\s*\(([^)]+)\)'),
                'circuit': re.compile(r'circuit\s+(\w+)\s*\{([^}]*)\}')
            },
            'quantum-net': {
                'network': re.compile(r'network\s+(\w+)\s*\{([^}]*)\}'),
                'node': re.compile(r'node\s+(\w+)'),
                'protocol': re.compile(r'protocol\s+(\w+)\s*\{([^}]*)\}')
            }
        }
    
    async def get_completions(self, context: CodeContext) -> List[Dict]:
        """Generate intelligent code completions"""
        
        # Quick pattern-based suggestions
        local_suggestions = self._get_pattern_suggestions(context)
        
        # AI-powered suggestions if available
        ai_suggestions = []
        if self.openai_client or self.anthropic_client:
            ai_suggestions = await self._get_ai_suggestions(context)
        
        # Merge and rank suggestions
        return self._rank_suggestions(local_suggestions + ai_suggestions, context)
    
    def _get_pattern_suggestions(self, context: CodeContext) -> List[Dict]:
        """Get pattern-based code suggestions"""
        suggestions = []
        patterns = self.patterns.get(context.language, {})
        
        # Extract current line and position
        lines = context.code.split('\n')
        current_line = lines[context.position['line'] - 1] if context.position['line'] <= len(lines) else ''
        
        # Check patterns
        for pattern_name, pattern in patterns.items():
            if pattern_name in current_line.lower():
                suggestions.extend(self._generate_pattern_suggestions(
                    pattern_name, context.language
                ))
        
        return suggestions
    
    def _generate_pattern_suggestions(self, pattern: str, language: str) -> List[Dict]:
        """Generate suggestions for specific patterns"""
        suggestions = []
        
        if language == 'synapse':
            if pattern == 'uncertain':
                suggestions.append({
                    'label': 'uncertain variable',
                    'insertText': 'uncertain ${1:var} = ${2:value} ± ${3:error}',
                    'kind': 'Snippet',
                    'documentation': 'Declare variable with uncertainty',
                    'priority': 0
                })
            elif pattern == 'parallel':
                suggestions.append({
                    'label': 'parallel block',
                    'insertText': 'parallel {\n    ${1:task1}\n    ${2:task2}\n}',
                    'kind': 'Snippet',
                    'documentation': 'Execute tasks in parallel',
                    'priority': 0
                })
        
        elif language == 'qubit-flow':
            if pattern == 'qubit':
                suggestions.append({
                    'label': 'qubit initialization',
                    'insertText': 'qubit ${1:q} = |${2:0}⟩',
                    'kind': 'Snippet',
                    'documentation': 'Initialize a qubit',
                    'priority': 0
                })
            elif pattern == 'gate':
                for gate in ['H', 'X', 'Y', 'Z', 'CNOT']:
                    suggestions.append({
                        'label': f'{gate} gate',
                        'insertText': f'{gate}[${{1:qubit}}]',
                        'kind': 'Function',
                        'documentation': self._get_gate_documentation(gate),
                        'priority': 1
                    })
        
        return suggestions
    
    async def _get_ai_suggestions(self, context: CodeContext) -> List[Dict]:
        """Get AI-powered suggestions"""
        if not (self.openai_client or self.anthropic_client):
            return []
        
        prompt = self._build_completion_prompt(context)
        
        try:
            if self.openai_client:
                response = await self._query_openai(prompt)
            elif self.anthropic_client:
                response = await self._query_anthropic(prompt)
            
            return self._parse_ai_suggestions(response)
        except Exception as e:
            print(f"AI suggestion error: {e}")
            return []
    
    def _build_completion_prompt(self, context: CodeContext) -> str:
        """Build prompt for AI completion"""
        return f"""
        Language: {context.language}
        Current code:
        {context.code}
        
        Position: Line {context.position['line']}, Column {context.position['column']}
        
        Provide code completion suggestions for the current position.
        Focus on {context.language}-specific patterns and best practices.
        Return as JSON array of suggestions with: label, insertText, documentation.
        """
    
    async def explain_error(self, error: Dict, code: str, language: str) -> Dict:
        """Explain errors with AI assistance"""
        
        # Pattern-based error explanation
        explanation = self._get_pattern_error_explanation(error, language)
        
        # Enhanced AI explanation if available
        if self.openai_client or self.anthropic_client:
            ai_explanation = await self._get_ai_error_explanation(error, code, language)
            explanation.update(ai_explanation)
        
        return explanation
    
    def _get_pattern_error_explanation(self, error: Dict, language: str) -> Dict:
        """Get pattern-based error explanation"""
        common_errors = self.knowledge_base[language].get('common_errors', {})
        
        for error_pattern, explanation in common_errors.items():
            if error_pattern in error.get('message', '').lower():
                return {
                    'explanation': explanation,
                    'suggestions': [f"Check {error_pattern}"],
                    'examples': []
                }
        
        return {
            'explanation': 'Error in code',
            'suggestions': ['Check syntax', 'Verify language rules'],
            'examples': []
        }
    
    async def optimize_code(self, code: str, language: str) -> Dict:
        """Provide optimization suggestions"""
        
        optimizations = []
        
        # Pattern-based optimizations
        if language == 'synapse':
            # Check for vectorization opportunities
            if 'for' in code and 'uncertain' in code:
                optimizations.append({
                    'type': 'vectorization',
                    'description': 'Consider vectorizing uncertainty calculations',
                    'example': 'Use numpy arrays for batch processing'
                })
            
            # Check for parallel opportunities
            if code.count('\n') > 10 and 'parallel' not in code:
                optimizations.append({
                    'type': 'parallelization',
                    'description': 'Consider parallel execution for independent tasks',
                    'example': 'Wrap independent calculations in parallel block'
                })
        
        elif language == 'qubit-flow':
            # Check for gate optimization
            if 'H[' in code and code.count('H[') > 2:
                optimizations.append({
                    'type': 'gate_reduction',
                    'description': 'Multiple Hadamard gates can be optimized',
                    'example': 'H[q]; H[q] = I (identity)'
                })
        
        return {
            'optimizations': optimizations,
            'performance': self._estimate_performance(code, language),
            'alternatives': []
        }
    
    def _estimate_performance(self, code: str, language: str) -> Dict:
        """Estimate code performance metrics"""
        lines = code.split('\n')
        
        return {
            'complexity': 'O(n)' if 'for' in code else 'O(1)',
            'memory': f'{len(lines) * 50} bytes (estimated)',
            'quantum_resources': self._count_quantum_resources(code, language)
        }
    
    def _count_quantum_resources(self, code: str, language: str) -> Dict:
        """Count quantum resources used"""
        resources = {'qubits': 0, 'gates': 0, 'measurements': 0}
        
        if language == 'qubit-flow':
            resources['qubits'] = len(re.findall(r'qubit\s+\w+', code))
            resources['gates'] = len(re.findall(r'\w+\[[^\]]+\]', code))
            resources['measurements'] = len(re.findall(r'measure', code))
        
        return resources
    
    async def generate_practice(self, topic: str, difficulty: str, language: str) -> Dict:
        """Generate practice problems"""
        
        # Select problem template based on topic and difficulty
        problem = self._select_problem_template(topic, difficulty, language)
        
        # Generate with AI if available
        if self.openai_client or self.anthropic_client:
            problem = await self._generate_ai_problem(topic, difficulty, language)
        
        return problem
    
    def _select_problem_template(self, topic: str, difficulty: str, language: str) -> Dict:
        """Select a practice problem template"""
        
        templates = {
            'synapse': {
                'uncertainty': {
                    'beginner': {
                        'problem': 'Calculate the total resistance with uncertainties',
                        'template': '# Calculate total resistance\nuncertain R1 = 100 ± 5  # ohms\nuncertain R2 = 200 ± 10  # ohms\n# TODO: Calculate total resistance',
                        'hints': ['Use series resistance formula', 'Propagate uncertainties'],
                        'solution': 'total = R1 + R2'
                    }
                }
            },
            'qubit-flow': {
                'superposition': {
                    'beginner': {
                        'problem': 'Create an equal superposition state',
                        'template': 'qubit q = |0⟩\n# TODO: Apply gate to create |+⟩ state',
                        'hints': ['Use Hadamard gate', '|+⟩ = (|0⟩ + |1⟩)/√2'],
                        'solution': 'H[q]'
                    }
                }
            }
        }
        
        return templates.get(language, {}).get(topic, {}).get(difficulty, {
            'problem': f'Practice {topic} in {language}',
            'template': f'// Write {language} code for {topic}',
            'hints': [],
            'solution': '// Solution'
        })
    
    def _get_gate_documentation(self, gate: str) -> str:
        """Get documentation for quantum gates"""
        docs = {
            'H': 'Hadamard gate: Creates equal superposition (|0⟩ + |1⟩)/√2',
            'X': 'Pauli-X gate: Bit flip operation |0⟩ ↔ |1⟩',
            'Y': 'Pauli-Y gate: Bit and phase flip',
            'Z': 'Pauli-Z gate: Phase flip |1⟩ → -|1⟩',
            'CNOT': 'Controlled-NOT: Creates entanglement between qubits'
        }
        return docs.get(gate, f'{gate} gate operation')
    
    def _rank_suggestions(self, suggestions: List[Dict], context: CodeContext) -> List[Dict]:
        """Rank suggestions by relevance"""
        
        # Add relevance scores
        for suggestion in suggestions:
            score = suggestion.get('priority', 5)
            
            # Boost if matches current typing
            current_word = context.code.split()[-1] if context.code else ''
            if current_word and suggestion['label'].lower().startswith(current_word.lower()):
                score -= 2
            
            # Boost based on user profile
            if context.user_profile.get('level') == 'beginner':
                if 'basic' in suggestion.get('documentation', '').lower():
                    score -= 1
            
            suggestion['score'] = score
        
        # Sort by score
        return sorted(suggestions, key=lambda x: x['score'])

# Initialize AI engine
ai_engine = QuantumAIEngine()

# API Routes
@ai_bp.route('/api/ai/complete', methods=['POST'])
async def get_completions():
    """Get code completions"""
    data = request.json
    context = CodeContext(
        code=data.get('code', ''),
        language=data.get('language', 'synapse'),
        position=data.get('position', {'line': 1, 'column': 1}),
        history=data.get('context', []),
        user_profile=data.get('profile', {})
    )
    
    suggestions = await ai_engine.get_completions(context)
    return jsonify({'suggestions': suggestions})

@ai_bp.route('/api/ai/explain', methods=['POST'])
async def explain_error():
    """Explain code errors"""
    data = request.json
    explanation = await ai_engine.explain_error(
        error=data.get('error', {}),
        code=data.get('code', ''),
        language=data.get('language', 'synapse')
    )
    return jsonify(explanation)

@ai_bp.route('/api/ai/optimize', methods=['POST'])
async def optimize_code():
    """Get optimization suggestions"""
    data = request.json
    optimizations = await ai_engine.optimize_code(
        code=data.get('code', ''),
        language=data.get('language', 'synapse')
    )
    return jsonify(optimizations)

@ai_bp.route('/api/ai/practice', methods=['POST'])
async def generate_practice():
    """Generate practice problems"""
    data = request.json
    problem = await ai_engine.generate_practice(
        topic=data.get('topic', 'basics'),
        difficulty=data.get('difficulty', 'beginner'),
        language=data.get('language', 'synapse')
    )
    return jsonify(problem)

# WebSocket support for real-time AI
def setup_socketio(app, socketio):
    """Setup WebSocket for real-time AI responses"""
    
    @socketio.on('ai_request')
    def handle_ai_request(data):
        """Handle real-time AI requests"""
        request_id = data.get('id')
        action = data.get('action')
        
        # Process based on action
        if action == 'complete':
            # Real-time completion
            emit('ai_response', {
                'id': request_id,
                'suggestions': []  # Quick response
            })
        elif action == 'hint':
            # Progressive hints
            emit('ai_response', {
                'id': request_id,
                'hint': 'Consider the quantum properties...'
            })