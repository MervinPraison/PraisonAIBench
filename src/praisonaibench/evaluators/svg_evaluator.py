"""
SVG Evaluator for PraisonAI Bench

Multi-metric evaluation system for SVG generation benchmarks.
Based on research from:
- SVGenius (arXiv 2506.03139): SVG Understanding, Editing and Generation
- Tom Gally's LLM SVG Generation Benchmark
- StarVector: Foundation model for SVG generation

Evaluation Metrics:
1. SVG Validity (15%) - Structural correctness
2. Visual Quality (35%) - Rendered image quality (SSIM, perceptual)
3. Semantic Alignment (25%) - CLIP score with prompt
4. Code Quality (10%) - SVG code structure and optimization
5. LLM Judge (15%) - Semantic quality assessment
"""

import os
import re
import tempfile
import logging
from typing import Dict, Any, Optional, Tuple
from xml.etree import ElementTree as ET

from ..base_evaluator import BaseEvaluator


class SVGValidator:
    """
    SVG structure validation (15% weight)
    Validates SVG syntax and structure
    """
    
    def validate(self, svg_content: str) -> Dict[str, Any]:
        """
        Validate SVG structure
        
        Args:
            svg_content: The SVG code to validate
            
        Returns:
            Validation results with score and issues
        """
        score = 0
        issues = []
        details = {}
        
        # Clean SVG content (extract from markdown if needed)
        svg_content = self._extract_svg(svg_content)
        
        if not svg_content:
            return {
                'score': 0,
                'valid_structure': False,
                'has_svg_tag': False,
                'has_viewbox': False,
                'issues': ['No SVG content found'],
                'weight': 0.15
            }
        
        # 1. SVG tag check (25 points)
        has_svg_tag = '<svg' in svg_content.lower()
        if has_svg_tag:
            score += 25
        else:
            issues.append("Missing <svg> tag")
        
        # 2. ViewBox attribute (15 points)
        has_viewbox = 'viewbox' in svg_content.lower() or 'viewBox' in svg_content
        if has_viewbox:
            score += 15
        else:
            issues.append("Missing viewBox attribute (recommended for scalability)")
        
        # 3. Valid XML structure (30 points)
        valid_xml = False
        try:
            # Try to parse as XML
            ET.fromstring(svg_content)
            score += 30
            valid_xml = True
        except ET.ParseError as e:
            issues.append(f"Invalid XML structure: {str(e)}")
        
        # 4. Has visual elements (20 points)
        visual_elements = ['<path', '<rect', '<circle', '<ellipse', '<line', 
                          '<polygon', '<polyline', '<text', '<image', '<g']
        found_elements = [el for el in visual_elements if el in svg_content.lower()]
        if found_elements:
            score += 20
            details['visual_elements'] = found_elements
        else:
            issues.append("No visual elements found (path, rect, circle, etc.)")
        
        # 5. Proper closing (10 points)
        if '</svg>' in svg_content.lower():
            score += 10
        else:
            issues.append("Missing closing </svg> tag")
        
        return {
            'score': min(100, score),
            'valid_structure': valid_xml,
            'has_svg_tag': has_svg_tag,
            'has_viewbox': has_viewbox,
            'visual_elements': details.get('visual_elements', []),
            'issues': issues,
            'weight': 0.15
        }
    
    def _extract_svg(self, content: str) -> Optional[str]:
        """Extract SVG content from markdown or raw text"""
        # Try to find SVG in code blocks
        svg_block_pattern = r'```(?:svg|xml)?\s*\n(.*?)\n```'
        matches = re.findall(svg_block_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            for match in matches:
                if '<svg' in match.lower():
                    return match.strip()
        
        # Try to find raw SVG
        svg_pattern = r'(<svg[^>]*>.*?</svg>)'
        matches = re.findall(svg_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Check if entire content is SVG
        if '<svg' in content.lower() and '</svg>' in content.lower():
            start = content.lower().find('<svg')
            end = content.lower().rfind('</svg>') + 6
            return content[start:end]
        
        return None


class SVGVisualEvaluator:
    """
    Visual quality evaluation (35% weight)
    Renders SVG and evaluates visual quality
    """
    
    def __init__(self, output_dir: str = "output/svg"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check for optional dependencies
        self._has_cairosvg = False
        self._has_pillow = False
        self._has_skimage = False
        
        try:
            import cairosvg
            self._has_cairosvg = True
        except ImportError:
            logging.debug("cairosvg not available - SVG rendering disabled")
        
        try:
            from PIL import Image
            self._has_pillow = True
        except ImportError:
            logging.debug("Pillow not available - image processing disabled")
        
        try:
            from skimage.metrics import structural_similarity
            self._has_skimage = True
        except ImportError:
            logging.debug("scikit-image not available - SSIM disabled")
    
    def evaluate(self, svg_content: str, test_name: str) -> Dict[str, Any]:
        """
        Evaluate visual quality of rendered SVG
        
        Args:
            svg_content: SVG code
            test_name: Name for output files
            
        Returns:
            Visual evaluation results
        """
        result = {
            'score': 0,
            'renders': False,
            'render_path': None,
            'dimensions': None,
            'color_count': 0,
            'complexity_score': 0,
            'issues': [],
            'weight': 0.35
        }
        
        # Extract SVG
        svg_content = self._extract_svg(svg_content)
        if not svg_content:
            result['issues'].append("No SVG content to render")
            return result
        
        # Try to render SVG
        if self._has_cairosvg and self._has_pillow:
            try:
                import cairosvg
                from PIL import Image
                import io
                
                # Render to PNG
                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
                
                # Save rendered image
                render_path = os.path.join(self.output_dir, f"{test_name}.png")
                with open(render_path, 'wb') as f:
                    f.write(png_data)
                
                result['renders'] = True
                result['render_path'] = render_path
                result['score'] += 50  # Successful render
                
                # Analyze rendered image
                img = Image.open(io.BytesIO(png_data))
                result['dimensions'] = img.size
                
                # Color analysis
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                colors = img.getcolors(maxcolors=10000)
                if colors:
                    result['color_count'] = len(colors)
                    # More colors = more complex/detailed
                    if result['color_count'] > 100:
                        result['score'] += 20
                    elif result['color_count'] > 20:
                        result['score'] += 15
                    elif result['color_count'] > 5:
                        result['score'] += 10
                    else:
                        result['score'] += 5
                
                # Check for non-empty image
                if img.size[0] > 0 and img.size[1] > 0:
                    # Check if image has actual content (not all transparent/white)
                    extrema = img.getextrema()
                    has_content = any(e[0] != e[1] for e in extrema if isinstance(e, tuple))
                    if has_content:
                        result['score'] += 30
                    else:
                        result['issues'].append("Image appears to be empty or single color")
                        result['score'] += 10
                
            except Exception as e:
                result['issues'].append(f"Render failed: {str(e)}")
                result['score'] = 10  # Partial credit for valid SVG structure
        else:
            # Fallback: estimate quality from SVG code
            result['score'] = self._estimate_quality_from_code(svg_content)
            result['issues'].append("Visual rendering not available (install cairosvg and Pillow)")
        
        return result
    
    def _extract_svg(self, content: str) -> Optional[str]:
        """Extract SVG content from markdown or raw text"""
        validator = SVGValidator()
        return validator._extract_svg(content)
    
    def _estimate_quality_from_code(self, svg_content: str) -> int:
        """Estimate visual quality from SVG code when rendering is unavailable"""
        score = 30  # Base score for valid SVG
        
        # Count visual elements
        elements = ['<path', '<rect', '<circle', '<ellipse', '<line', 
                   '<polygon', '<polyline', '<text', '<g']
        element_count = sum(svg_content.lower().count(el) for el in elements)
        
        if element_count > 20:
            score += 30
        elif element_count > 10:
            score += 20
        elif element_count > 5:
            score += 15
        elif element_count > 0:
            score += 10
        
        # Check for colors
        color_patterns = [r'fill="[^"]*"', r'stroke="[^"]*"', r'#[0-9a-fA-F]{3,6}']
        color_count = sum(len(re.findall(p, svg_content)) for p in color_patterns)
        
        if color_count > 10:
            score += 20
        elif color_count > 5:
            score += 15
        elif color_count > 0:
            score += 10
        
        return min(100, score)


class SVGSemanticEvaluator:
    """
    Semantic alignment evaluation (25% weight)
    Measures how well the SVG matches the prompt description
    Uses CLIP if available, falls back to keyword matching
    """
    
    def __init__(self):
        self._has_clip = False
        self._clip_model = None
        self._clip_processor = None
        
        try:
            import torch
            from transformers import CLIPProcessor, CLIPModel
            self._has_clip = True
            logging.debug("CLIP available for semantic evaluation")
        except ImportError:
            logging.debug("CLIP not available - using keyword matching")
    
    def evaluate(self, svg_content: str, prompt: str, render_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate semantic alignment between SVG and prompt
        
        Args:
            svg_content: SVG code
            prompt: Original prompt/description
            render_path: Path to rendered PNG (optional)
            
        Returns:
            Semantic evaluation results
        """
        result = {
            'score': 0,
            'clip_score': None,
            'keyword_match': 0.0,
            'method': 'keyword',
            'matched_keywords': [],
            'weight': 0.25
        }
        
        # Try CLIP-based evaluation if render is available
        if self._has_clip and render_path and os.path.exists(render_path):
            try:
                clip_score = self._compute_clip_score(render_path, prompt)
                if clip_score is not None:
                    result['clip_score'] = clip_score
                    result['method'] = 'clip'
                    # CLIP scores typically range 0.15-0.35 for good matches
                    # Normalize to 0-100
                    result['score'] = int(min(100, max(0, (clip_score - 0.1) * 400)))
                    return result
            except Exception as e:
                logging.debug(f"CLIP evaluation failed: {e}")
        
        # Fallback to keyword matching
        result['score'], result['keyword_match'], result['matched_keywords'] = \
            self._keyword_match(svg_content, prompt)
        
        return result
    
    def _compute_clip_score(self, image_path: str, text: str) -> Optional[float]:
        """Compute CLIP similarity score between image and text"""
        if not self._has_clip:
            return None
        
        try:
            import torch
            from transformers import CLIPProcessor, CLIPModel
            from PIL import Image
            
            # Lazy load model
            if self._clip_model is None:
                self._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # Load image
            image = Image.open(image_path)
            
            # Process inputs
            inputs = self._clip_processor(
                text=[text],
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # Get similarity
            with torch.no_grad():
                outputs = self._clip_model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                
            return float(probs[0][0])
            
        except Exception as e:
            logging.debug(f"CLIP computation failed: {e}")
            return None
    
    def _keyword_match(self, svg_content: str, prompt: str) -> Tuple[int, float, list]:
        """
        Match keywords from prompt in SVG content
        
        Returns:
            (score, match_ratio, matched_keywords)
        """
        # Extract meaningful keywords from prompt
        stop_words = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 
                     'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'shall',
                     'this', 'that', 'these', 'those', 'it', 'its',
                     'and', 'or', 'but', 'if', 'then', 'else', 'when',
                     'svg', 'generate', 'create', 'make', 'draw', 'show',
                     'image', 'picture', 'graphic', 'illustration'}
        
        # Extract keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        keywords = [w for w in words if w not in stop_words]
        
        if not keywords:
            return 50, 0.5, []  # Default score if no keywords
        
        # Check for keywords in SVG (comments, IDs, class names)
        svg_lower = svg_content.lower()
        matched = []
        
        for kw in keywords:
            # Check in comments, IDs, and content
            if kw in svg_lower:
                matched.append(kw)
            # Check for related terms
            elif any(related in svg_lower for related in self._get_related_terms(kw)):
                matched.append(kw)
        
        match_ratio = len(matched) / len(keywords) if keywords else 0
        
        # Score based on match ratio
        # Also give credit for having complex SVG (likely attempted the task)
        base_score = int(match_ratio * 60)
        
        # Bonus for SVG complexity
        element_count = len(re.findall(r'<(path|rect|circle|ellipse|polygon|g)\b', svg_lower))
        complexity_bonus = min(40, element_count * 4)
        
        score = min(100, base_score + complexity_bonus)
        
        return score, match_ratio, matched
    
    def _get_related_terms(self, keyword: str) -> list:
        """Get related terms for a keyword"""
        # Simple related terms mapping
        related = {
            'bridge': ['arch', 'span', 'tower', 'cable', 'suspension'],
            'sunset': ['sun', 'orange', 'red', 'yellow', 'sky', 'horizon'],
            'golden': ['gold', 'orange', 'yellow', '#ff', '#ffd'],
            'gate': ['entrance', 'arch', 'tower'],
            'water': ['wave', 'ocean', 'sea', 'river', 'blue'],
            'mountain': ['peak', 'hill', 'slope'],
            'tree': ['leaf', 'branch', 'trunk', 'forest'],
            'car': ['wheel', 'vehicle', 'road'],
            'house': ['building', 'roof', 'window', 'door'],
            'person': ['human', 'figure', 'body', 'head'],
            'animal': ['creature', 'beast'],
            'bird': ['wing', 'feather', 'beak'],
            'flower': ['petal', 'stem', 'bloom'],
        }
        return related.get(keyword, [])


class SVGCodeQualityEvaluator:
    """
    SVG code quality evaluation (10% weight)
    Evaluates code structure, optimization, and best practices
    """
    
    def evaluate(self, svg_content: str) -> Dict[str, Any]:
        """
        Evaluate SVG code quality
        
        Args:
            svg_content: SVG code
            
        Returns:
            Code quality evaluation results
        """
        result = {
            'score': 0,
            'has_comments': False,
            'uses_groups': False,
            'uses_defs': False,
            'path_count': 0,
            'element_count': 0,
            'estimated_complexity': 'low',
            'issues': [],
            'weight': 0.10
        }
        
        # Extract SVG
        validator = SVGValidator()
        svg_content = validator._extract_svg(svg_content) or svg_content
        
        svg_lower = svg_content.lower()
        
        # 1. Comments (10 points) - shows organization
        has_comments = '<!--' in svg_content
        if has_comments:
            result['has_comments'] = True
            result['score'] += 10
        
        # 2. Uses groups (15 points) - shows structure
        uses_groups = '<g' in svg_lower
        if uses_groups:
            result['uses_groups'] = True
            result['score'] += 15
        
        # 3. Uses defs/symbols (15 points) - shows optimization
        uses_defs = '<defs' in svg_lower or '<symbol' in svg_lower
        if uses_defs:
            result['uses_defs'] = True
            result['score'] += 15
        
        # 4. Element count and complexity (40 points)
        elements = ['path', 'rect', 'circle', 'ellipse', 'line', 
                   'polygon', 'polyline', 'text', 'image']
        element_count = sum(len(re.findall(f'<{el}\\b', svg_lower)) for el in elements)
        result['element_count'] = element_count
        result['path_count'] = len(re.findall(r'<path\b', svg_lower))
        
        if element_count > 50:
            result['estimated_complexity'] = 'high'
            result['score'] += 40
        elif element_count > 20:
            result['estimated_complexity'] = 'medium'
            result['score'] += 30
        elif element_count > 5:
            result['estimated_complexity'] = 'low'
            result['score'] += 20
        elif element_count > 0:
            result['estimated_complexity'] = 'minimal'
            result['score'] += 10
        else:
            result['issues'].append("No visual elements found")
        
        # 5. Proper attributes (20 points)
        has_xmlns = 'xmlns' in svg_lower
        has_dimensions = ('width=' in svg_lower or 'height=' in svg_lower or 
                         'viewbox' in svg_lower)
        
        if has_xmlns:
            result['score'] += 10
        else:
            result['issues'].append("Missing xmlns attribute")
        
        if has_dimensions:
            result['score'] += 10
        else:
            result['issues'].append("Missing dimensions (width/height or viewBox)")
        
        return result


class SVGEvaluator(BaseEvaluator):
    """
    Complete SVG evaluator combining all metrics
    
    Weights:
    - SVG Validity: 15%
    - Visual Quality: 35%
    - Semantic Alignment: 25%
    - Code Quality: 10%
    - LLM Judge: 15%
    """
    
    def __init__(self, 
                 use_llm_judge: bool = True,
                 judge_model: str = "gpt-4o-mini",
                 output_dir: str = "output/svg"):
        """
        Initialize SVG evaluator
        
        Args:
            use_llm_judge: Enable LLM-as-a-Judge quality scoring
            judge_model: Model to use for judging
            output_dir: Directory for output files
        """
        self.validator = SVGValidator()
        self.visual = SVGVisualEvaluator(output_dir)
        self.semantic = SVGSemanticEvaluator()
        self.code_quality = SVGCodeQualityEvaluator()
        self.use_llm_judge = use_llm_judge
        self.judge_model = judge_model
        self.llm_judge = None
        
        if use_llm_judge:
            try:
                from ..simple_evaluator import LLMJudge
                self.llm_judge = LLMJudge(judge_model)
            except ImportError:
                logging.warning("LLMJudge not available")
    
    def get_language(self) -> str:
        """Return language identifier."""
        return 'svg'
    
    def get_file_extension(self) -> str:
        """Return file extension."""
        return 'svg'
    
    def evaluate(self, 
                 code: str, 
                 test_name: str,
                 prompt: str,
                 expected: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive SVG evaluation
        
        Args:
            code: SVG code to evaluate
            test_name: Name of the test
            prompt: Original prompt/description
            expected: Optional expected result
            
        Returns:
            Complete evaluation results
        """
        results = {}
        
        # 1. SVG Validity (15%)
        results['validity'] = self.validator.validate(code)
        
        # 2. Visual Quality (35%)
        results['visual'] = self.visual.evaluate(code, test_name)
        
        # 3. Semantic Alignment (25%)
        render_path = results['visual'].get('render_path')
        results['semantic'] = self.semantic.evaluate(code, prompt, render_path)
        
        # 4. Code Quality (10%)
        results['code_quality'] = self.code_quality.evaluate(code)
        
        # 5. LLM Judge (15%)
        if self.llm_judge:
            try:
                results['llm_judge'] = self.llm_judge.evaluate(code, prompt)
            except Exception as e:
                logging.warning(f"LLM Judge failed: {e}")
                results['llm_judge'] = None
        else:
            results['llm_judge'] = None
        
        # Calculate overall score
        overall_score = self._calculate_overall(results)
        
        # Generate feedback
        feedback = self._generate_feedback(results)
        
        return {
            'score': overall_score,
            'overall_score': overall_score,
            'passed': overall_score >= 60,
            'validity': results['validity'],
            'visual': results['visual'],
            'semantic': results['semantic'],
            'code_quality': results['code_quality'],
            'llm_judge': results['llm_judge'],
            'feedback': feedback,
            'render_path': results['visual'].get('render_path'),
            'breakdown': self._generate_breakdown(results, overall_score)
        }
    
    def _calculate_overall(self, results: Dict[str, Any]) -> int:
        """Calculate weighted overall score"""
        score = 0.0
        total_weight = 0.0
        
        # Validity (15%)
        if results.get('validity'):
            weight = 0.15
            score += results['validity']['score'] * weight
            total_weight += weight
        
        # Visual (35%)
        if results.get('visual'):
            weight = 0.35
            score += results['visual']['score'] * weight
            total_weight += weight
        
        # Semantic (25%)
        if results.get('semantic'):
            weight = 0.25
            score += results['semantic']['score'] * weight
            total_weight += weight
        
        # Code Quality (10%)
        if results.get('code_quality'):
            weight = 0.10
            score += results['code_quality']['score'] * weight
            total_weight += weight
        
        # LLM Judge (15%)
        if results.get('llm_judge'):
            weight = 0.15
            llm_score = results['llm_judge'].get('quality_score', 
                       results['llm_judge'].get('score', 0))
            score += llm_score * weight
            total_weight += weight
        
        # Normalize if some components are missing
        if total_weight > 0 and total_weight < 1.0:
            score = score / total_weight
        
        return int(score)
    
    def _generate_feedback(self, results: Dict[str, Any]) -> list:
        """Generate feedback from all components"""
        feedback = []
        
        # Validity feedback
        if results.get('validity'):
            v = results['validity']
            if v['issues']:
                feedback.append({
                    'level': 'warning',
                    'component': 'SVG Validity',
                    'message': f"⚠️ {len(v['issues'])} validity issue(s)",
                    'details': v['issues']
                })
            else:
                feedback.append({
                    'level': 'success',
                    'component': 'SVG Validity',
                    'message': '✅ Valid SVG structure'
                })
        
        # Visual feedback
        if results.get('visual'):
            v = results['visual']
            if v['renders']:
                feedback.append({
                    'level': 'success',
                    'component': 'Visual Quality',
                    'message': f"✅ SVG renders successfully ({v['dimensions']})"
                })
            else:
                feedback.append({
                    'level': 'warning',
                    'component': 'Visual Quality',
                    'message': '⚠️ SVG rendering failed or unavailable'
                })
        
        # Semantic feedback
        if results.get('semantic'):
            s = results['semantic']
            if s['score'] >= 70:
                feedback.append({
                    'level': 'success',
                    'component': 'Semantic Alignment',
                    'message': f"✅ Good semantic match ({s['method']})"
                })
            else:
                feedback.append({
                    'level': 'warning',
                    'component': 'Semantic Alignment',
                    'message': f"⚠️ Low semantic alignment ({s['score']}/100)"
                })
        
        # Code quality feedback
        if results.get('code_quality'):
            c = results['code_quality']
            feedback.append({
                'level': 'info',
                'component': 'Code Quality',
                'message': f"📊 Complexity: {c['estimated_complexity']} ({c['element_count']} elements)"
            })
        
        # LLM Judge feedback
        if results.get('llm_judge'):
            l = results['llm_judge']
            llm_score = l.get('quality_score', l.get('score', 0))
            feedback.append({
                'level': 'info',
                'component': 'LLM Judge',
                'message': f"🤖 Quality Score: {llm_score}/100"
            })
        
        return feedback
    
    def _generate_breakdown(self, results: Dict[str, Any], overall: int) -> Dict[str, Any]:
        """Generate detailed score breakdown"""
        has_llm = results.get('llm_judge') is not None
        
        if has_llm:
            weights = {
                'validity': 0.15,
                'visual': 0.35,
                'semantic': 0.25,
                'code_quality': 0.10,
                'llm_judge': 0.15
            }
        else:
            # Normalized weights without LLM
            weights = {
                'validity': 0.176,
                'visual': 0.412,
                'semantic': 0.294,
                'code_quality': 0.118,
                'llm_judge': 0.0
            }
        
        breakdown = {
            'overall_score': overall,
            'components': {}
        }
        
        for component, weight in weights.items():
            if results.get(component):
                comp_result = results[component]
                if component == 'llm_judge':
                    comp_score = comp_result.get('quality_score', comp_result.get('score', 0))
                else:
                    comp_score = comp_result.get('score', 0)
                breakdown['components'][component] = {
                    'score': comp_score,
                    'weight': f"{weight * 100:.1f}%",
                    'contribution': f"{comp_score * weight:.1f}"
                }
            elif component == 'llm_judge' and not has_llm:
                breakdown['components'][component] = {
                    'score': 'N/A',
                    'weight': '0%',
                    'contribution': 'Disabled'
                }
        
        return breakdown
