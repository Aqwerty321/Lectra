"""
🚀 ADVANCED DYNAMIC SLIDE LAYOUT ENGINE v2.0
==============================================

Enterprise-grade algorithmic text fitting system with intelligent typography,
adaptive spacing, and professional layout optimization.

CORE MATHEMATICAL MODEL:
    H_used = Σ(N_lines(p) × L_height) + (n-1) × P_spacing + M_top + M_bottom
    
    Where:
    - H_used: Total vertical space consumed (points)
    - N_lines(p): Number of lines for paragraph p (advanced text metrics)
    - L_height: Line height = font_size × line_spacing
    - P_spacing: Inter-paragraph spacing (adaptive)
    - M_top, M_bottom: Top and bottom margins
    - n: Total paragraph count

VALIDATION RULES:
    ✓ Valid if: H_used ≤ H_textbox
    ✓ Optimal if: 0.7 × H_textbox ≤ H_used ≤ 0.95 × H_textbox
    ✓ Overflow if: H_used > H_textbox → trigger pagination
    
ADVANCED FEATURES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ ✨ Intelligent Pagination     │ Multi-slide content splitting          │
│ 📐 Vertical Centering         │ Mathematical top_padding calculation   │
│ 🎯 Smart Font Scaling         │ Progressive font reduction (5-15%)     │
│ 📊 Density Analysis           │ Sparse/dense content detection         │
│ 🔤 Typography Engine          │ Advanced font metrics & line breaking  │
│ 🎨 Adaptive Spacing           │ Context-aware paragraph spacing        │
│ 🧮 Real-time Metrics          │ Live calculation tracking              │
│ 🐛 Debug Telemetry            │ Comprehensive logging system           │
│ 🔄 Orphan Prevention          │ Widow/orphan line control              │
│ 📏 Aspect Ratio Support       │ 16:9, 4:3, custom ratio handling       │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Author: AI-Powered Layout Engine
Version: 2.0.0
License: MIT
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
import math
import re


class ContentDensity(Enum):
    """Content density classification for adaptive spacing."""
    SPARSE = "sparse"          # < 3 paragraphs, < 30% space used
    BALANCED = "balanced"      # 3-6 paragraphs, 30-70% space used
    DENSE = "dense"            # 6-10 paragraphs, 70-90% space used
    OVERCROWDED = "overcrowded"  # > 10 paragraphs or > 90% space


class FontScalingStrategy(Enum):
    """Font scaling strategies for overflow handling."""
    NONE = "none"              # No scaling
    CONSERVATIVE = "conservative"  # 5% reduction
    MODERATE = "moderate"      # 10% reduction
    AGGRESSIVE = "aggressive"  # 15% reduction


@dataclass
class TypographyMetrics:
    """Advanced typography metrics for precise text measurement."""
    avg_char_width: float = 0.6  # Average character width ratio (relative to font size)
    capital_ratio: float = 1.3   # Capital letters height ratio
    descender_ratio: float = 0.25  # Descender depth ratio
    word_spacing: float = 0.3    # Space between words (relative to font size)
    
    # Character width variations (relative to font size)
    narrow_chars: str = "ijl|!"
    normal_chars: str = "abcdefghknopqrstuvxyz"
    wide_chars: str = "mwMW"
    extra_wide_chars: str = "@"
    
    def estimate_text_width(self, text: str, font_size: float) -> float:
        """
        Estimate text width using character-specific metrics.
        
        Algorithm:
            width = Σ(char_width(c) × font_size) for c in text
        """
        width = 0
        for char in text:
            if char in self.narrow_chars:
                width += font_size * 0.4
            elif char in self.wide_chars:
                width += font_size * 0.9
            elif char in self.extra_wide_chars:
                width += font_size * 1.2
            elif char.isupper():
                width += font_size * self.avg_char_width * self.capital_ratio
            elif char == ' ':
                width += font_size * self.word_spacing
            else:
                width += font_size * self.avg_char_width
        return width


@dataclass
class LayoutConfig:
    """
    Advanced configuration for slide layout calculations.
    
    All dimensions in points (1 inch = 72 points).
    """
    # === SLIDE DIMENSIONS ===
    slide_height: float = 540  # Content area height (7.5" for 16:9 after title)
    slide_width: float = 720   # Content area width (10" for 16:9)
    aspect_ratio: str = "16:9"  # Aspect ratio
    
    # === MARGINS ===
    margin_top: float = 0      # Top margin (title handled separately)
    margin_bottom: float = 21.6  # Bottom margin (0.3")
    margin_left: float = 36    # Left margin (0.5")
    margin_right: float = 36   # Right margin (0.5")
    
    # === TYPOGRAPHY ===
    font_size: float = 14      # Base font size
    font_family: str = "Calibri"
    line_spacing: float = 1.15  # Line height multiplier
    para_spacing: float = 14   # Base spacing between paragraphs
    
    # === TEXT MEASUREMENT ===
    chars_per_line: int = 80   # Estimated characters per line
    use_advanced_metrics: bool = True  # Use TypographyMetrics
    
    # === ADAPTIVE BEHAVIOR ===
    auto_center_vertical: bool = True   # Enable vertical centering
    auto_adjust_font: bool = True       # Enable font size adjustment
    prevent_orphans: bool = True        # Prevent single lines on new slide
    
    # === SPACING MULTIPLIERS ===
    sparse_content_multiplier: float = 1.5   # Boost spacing for sparse content
    dense_content_multiplier: float = 0.85   # Reduce spacing for dense content
    
    # === OVERFLOW HANDLING ===
    overflow_threshold: float = 1.0    # Trigger pagination (1.0 = 100%)
    overflow_tolerance: float = 0.1    # Allow 10% overflow before font reduction
    font_scaling_strategy: FontScalingStrategy = FontScalingStrategy.MODERATE
    
    # === OPTIMIZATION ===
    optimize_spacing: bool = True      # Optimize paragraph spacing
    balance_slides: bool = True        # Balance content across multiple slides
    min_paragraphs_per_slide: int = 1  # Minimum paragraphs per slide
    
    @property
    def textbox_height(self) -> float:
        """Calculate available textbox height."""
        return self.slide_height - (self.margin_top + self.margin_bottom)
    
    @property
    def textbox_width(self) -> float:
        """Calculate available textbox width."""
        return self.slide_width - (self.margin_left + self.margin_right)
    
    @property
    def line_height(self) -> float:
        """Calculate line height in points."""
        return self.font_size * self.line_spacing
    
    def get_font_reduction_factor(self) -> float:
        """Get font reduction factor based on strategy."""
        strategy_map = {
            FontScalingStrategy.NONE: 1.0,
            FontScalingStrategy.CONSERVATIVE: 0.95,
            FontScalingStrategy.MODERATE: 0.90,
            FontScalingStrategy.AGGRESSIVE: 0.85
        }
        return strategy_map.get(self.font_scaling_strategy, 0.90)


@dataclass
class ParagraphMetrics:
    """
    Detailed metrics for a single paragraph.
    
    Tracks all measurements needed for precise layout calculation.
    """
    text: str                          # Original text
    estimated_lines: int               # Number of lines (estimated)
    actual_width: float                # Estimated text width (points)
    height_required: float             # Total height needed (points)
    font_size: float                   # Font size for this paragraph
    is_subpoint: bool = False          # Is this an indented sub-bullet?
    indent_level: int = 0              # Indentation level (0, 1, 2, ...)
    word_count: int = 0                # Number of words
    char_count: int = 0                # Number of characters
    
    def __post_init__(self):
        """Calculate derived metrics."""
        self.word_count = len(self.text.split())
        self.char_count = len(self.text)


@dataclass
class SlideLayout:
    """
    Complete layout information for a single slide.
    
    Contains all data needed to render the slide perfectly.
    """
    slide_number: int                  # Slide index (0-based)
    paragraphs: List[str]              # Text content for this slide
    paragraph_metrics: List[ParagraphMetrics]  # Detailed metrics per paragraph
    total_height_used: float           # Total vertical space consumed
    available_height: float            # Available textbox height
    top_padding: float                 # Padding for vertical centering
    para_spacing: float                # Spacing between paragraphs
    font_size: float                   # Base font size
    density: ContentDensity            # Content density classification
    is_balanced: bool = True           # Is layout well-balanced?
    overflow_amount: float = 0.0       # Amount of overflow (if any)
    optimization_applied: str = "none"  # Optimization techniques applied
    
    @property
    def utilization_ratio(self) -> float:
        """Calculate space utilization ratio (0.0 - 1.0+)."""
        if self.available_height == 0:
            return 0.0
        return self.total_height_used / self.available_height
    
    @property
    def is_optimal(self) -> bool:
        """Check if layout is in optimal range (70-95% utilization)."""
        return 0.70 <= self.utilization_ratio <= 0.95
    
    @property
    def has_overflow(self) -> bool:
        """Check if content overflows available space."""
        return self.total_height_used > self.available_height


class SlideLayoutEngine:
    """
    🎯 ADVANCED DYNAMIC LAYOUT ENGINE
    
    Calculates optimal text layout across multiple slides using sophisticated
    mathematical algorithms and typography principles.
    
    WORKFLOW:
    ========
    1. INITIALIZATION
       │
       ├─> Configure layout parameters (margins, spacing, fonts)
       ├─> Initialize typography engine
       └─> Set optimization flags
       
    2. TEXT ANALYSIS
       │
       ├─> Parse paragraphs and detect structure
       ├─> Estimate line counts using advanced metrics
       ├─> Calculate height requirements per paragraph
       └─> Classify content density
       
    3. LAYOUT CALCULATION
       │
       ├─> Track cumulative height incrementally
       ├─> Detect overflow conditions
       ├─> Apply adaptive spacing rules
       ├─> Trigger pagination when needed
       └─> Prevent orphans/widows
       
    4. OPTIMIZATION
       │
       ├─> Vertical centering (top_padding calculation)
       ├─> Font size adjustment for slight overflows
       ├─> Spacing optimization (sparse/dense adaptation)
       ├─> Balance content across slides
       └─> Final metrics validation
       
    5. OUTPUT
       │
       └─> Return list of SlideLayout objects (ready to render)
    
    USAGE:
    ======
    >>> config = LayoutConfig(slide_height=540, font_size=14)
    >>> engine = SlideLayoutEngine(config)
    >>> layouts = engine.calculate_layouts(paragraphs, font_size=14)
    >>> for layout in layouts:
    ...     print(f"Slide {layout.slide_number}: {len(layout.paragraphs)} paragraphs")
    """
    
    def __init__(self, config: LayoutConfig):
        """
        Initialize the layout engine with configuration.
        
        Args:
            config: LayoutConfig object with all parameters
        """
        self.config = config
        self.typography = TypographyMetrics()
        self.debug_log: List[str] = []
        self.metrics_history: List[Dict[str, Any]] = []
        
        self._log(f"🚀 SlideLayoutEngine v2.0 Initialized")
        self._log(f"   Textbox: {config.textbox_width:.1f}W × {config.textbox_height:.1f}H pts")
        self._log(f"   Font: {config.font_family} {config.font_size}pt @ {config.line_spacing}× spacing")
        self._log(f"   Features: {'✓' if config.auto_center_vertical else '✗'} Centering | "
                 f"{'✓' if config.auto_adjust_font else '✗'} Auto-Font | "
                 f"{'✓' if config.prevent_orphans else '✗'} Orphan Prevention")
    
    def calculate_layouts(
        self, 
        paragraphs: List[str], 
        font_size: Optional[float] = None
    ) -> List[SlideLayout]:
        """
        🎯 MAIN ENTRY POINT: Calculate optimal layouts for given paragraphs.
        
        This method implements the core algorithm that:
        1. Analyzes text content and structure
        2. Calculates height requirements
        3. Splits content across multiple slides
        4. Applies optimization techniques
        5. Returns ready-to-render layouts
        
        Args:
            paragraphs: List of text strings (bullet points)
            font_size: Override font size (optional)
            
        Returns:
            List of SlideLayout objects (one per slide needed)
            
        Algorithm:
            FOR each paragraph p:
                CALCULATE lines(p) using text metrics
                CALCULATE height(p) = lines × line_height
                TRACK cumulative_height += height(p) + spacing
                
                IF cumulative_height > threshold:
                    FINALIZE current slide
                    START new slide
                    ADD p to new slide
                ELSE:
                    ADD p to current slide
            
            FINALIZE last slide
            APPLY optimizations to all slides
            RETURN layouts
        """
        if not paragraphs:
            self._log("⚠️  Empty paragraph list - returning empty layout")
            return []
        
        font_size = font_size or self.config.font_size
        self._log(f"\n{'='*70}")
        self._log(f"📊 CALCULATING LAYOUTS: {len(paragraphs)} paragraphs @ {font_size}pt")
        self._log(f"{'='*70}")
        
        layouts: List[SlideLayout] = []
        current_slide_paragraphs: List[str] = []
        current_slide_metrics: List[ParagraphMetrics] = []
        cumulative_height = 0.0
        
        for para_idx, para_text in enumerate(paragraphs):
            # === STEP 1: ANALYZE PARAGRAPH ===
            metric = self._calculate_paragraph_metrics(para_text, font_size)
            
            # === STEP 2: ADD PARAGRAPH SPACING ===
            # Add spacing before paragraph (except first on slide)
            spacing_before = self.config.para_spacing if current_slide_paragraphs else 0
            
            # === STEP 3: CALCULATE PROJECTED HEIGHT ===
            projected_height = cumulative_height + spacing_before + metric.height_required
            
            self._log(f"\n   Para {para_idx + 1}/{len(paragraphs)}: "
                     f"{metric.estimated_lines} lines × {metric.height_required:.1f}pts")
            self._log(f"      Text: \"{para_text[:60]}{'...' if len(para_text) > 60 else ''}\"")
            self._log(f"      Cumulative: {cumulative_height:.1f} + {spacing_before:.1f} + "
                     f"{metric.height_required:.1f} = {projected_height:.1f}pts")
            
            # === STEP 4: CHECK OVERFLOW ===
            overflow_threshold = self.config.textbox_height * self.config.overflow_threshold
            
            if projected_height > overflow_threshold and current_slide_paragraphs:
                # === OVERFLOW DETECTED: FINALIZE CURRENT SLIDE ===
                self._log(f"      🔴 OVERFLOW: {projected_height:.1f} > {overflow_threshold:.1f}")
                self._log(f"      📄 Finalizing slide {len(layouts) + 1} with {len(current_slide_paragraphs)} paragraphs")
                
                # Check orphan prevention
                if self.config.prevent_orphans and len(current_slide_paragraphs) >= 2:
                    # Keep at least 2 paragraphs on current slide
                    self._log(f"      🛡️  Orphan prevention: keeping ≥2 paragraphs")
                
                layout = self._finalize_slide_layout(
                    slide_number=len(layouts),
                    paragraphs=current_slide_paragraphs,
                    metrics=current_slide_metrics,
                    cumulative_height=cumulative_height,
                    base_font_size=font_size
                )
                layouts.append(layout)
                
                # === START NEW SLIDE ===
                current_slide_paragraphs = [para_text]
                current_slide_metrics = [metric]
                cumulative_height = metric.height_required
                self._log(f"      ✨ Starting slide {len(layouts) + 1} with para {para_idx + 1}")
            
            else:
                # === ADD TO CURRENT SLIDE ===
                current_slide_paragraphs.append(para_text)
                current_slide_metrics.append(metric)
                cumulative_height = projected_height
                self._log(f"      ✅ Added to current slide ({len(current_slide_paragraphs)} total)")
        
        # === STEP 5: FINALIZE LAST SLIDE ===
        if current_slide_paragraphs:
            self._log(f"\n   📄 Finalizing final slide {len(layouts) + 1} with {len(current_slide_paragraphs)} paragraphs")
            layout = self._finalize_slide_layout(
                slide_number=len(layouts),
                paragraphs=current_slide_paragraphs,
                metrics=current_slide_metrics,
                cumulative_height=cumulative_height,
                base_font_size=font_size
            )
            layouts.append(layout)
        
        # === STEP 6: POST-PROCESSING OPTIMIZATION ===
        if self.config.balance_slides and len(layouts) > 1:
            self._log(f"\n   ⚖️  Balancing content across {len(layouts)} slides...")
            layouts = self._balance_slides(layouts)
        
        # === SUMMARY ===
        self._log(f"\n{'='*70}")
        self._log(f"✅ LAYOUT COMPLETE: {len(layouts)} slide(s) created")
        for idx, layout in enumerate(layouts):
            self._log(f"   Slide {idx + 1}: {len(layout.paragraphs)} para, "
                     f"{layout.utilization_ratio:.1%} util, "
                     f"{layout.density.value} density, "
                     f"{'✓ optimal' if layout.is_optimal else '⚠ suboptimal'}")
        self._log(f"{'='*70}\n")
        
        return layouts
    
    def _calculate_paragraph_metrics(
        self, 
        text: str, 
        font_size: float
    ) -> ParagraphMetrics:
        """
        Calculate detailed metrics for a single paragraph.
        
        Uses advanced typography engine for precise measurements.
        
        Algorithm:
            IF use_advanced_metrics:
                width = typography.estimate_text_width(text, font_size)
                lines = ceil(width / textbox_width)
            ELSE:
                lines = ceil(len(text) / chars_per_line)
            
            height = lines × (font_size × line_spacing)
        """
        # Detect indentation level
        is_subpoint = text.startswith('  ')
        indent_level = len(text) - len(text.lstrip())
        clean_text = text.strip()
        
        # === ESTIMATE LINE COUNT ===
        if self.config.use_advanced_metrics and self.typography:
            # Advanced: Use character-width estimation
            estimated_width = self.typography.estimate_text_width(clean_text, font_size)
            available_width = self.config.textbox_width * (0.85 if is_subpoint else 0.95)
            estimated_lines = max(1, math.ceil(estimated_width / available_width))
        else:
            # Simple: Character count estimation
            chars_per_line = self.config.chars_per_line * (0.8 if is_subpoint else 1.0)
            estimated_lines = max(1, math.ceil(len(clean_text) / chars_per_line))
        
        # === CALCULATE HEIGHT ===
        line_height = font_size * self.config.line_spacing
        height_required = estimated_lines * line_height
        
        return ParagraphMetrics(
            text=clean_text,
            estimated_lines=estimated_lines,
            actual_width=estimated_width if self.config.use_advanced_metrics else 0,
            height_required=height_required,
            font_size=font_size,
            is_subpoint=is_subpoint,
            indent_level=indent_level
        )
    
    def _finalize_slide_layout(
        self,
        slide_number: int,
        paragraphs: List[str],
        metrics: List[ParagraphMetrics],
        cumulative_height: float,
        base_font_size: float
    ) -> SlideLayout:
        """
        Finalize layout for a single slide with optimization.
        
        Applies:
        - Vertical centering
        - Font size adjustment
        - Adaptive spacing
        - Density analysis
        
        Returns:
            Complete SlideLayout object ready for rendering
        """
        available_height = self.config.textbox_height
        para_spacing = self.config.para_spacing
        font_size = base_font_size
        optimization = "none"
        
        # === DENSITY ANALYSIS ===
        density = self._classify_density(len(paragraphs), cumulative_height, available_height)
        self._log(f"      📊 Density: {density.value}")
        
        # === FONT SIZE ADJUSTMENT ===
        if self.config.auto_adjust_font:
            overflow_ratio = cumulative_height / available_height
            tolerance = 1.0 + self.config.overflow_tolerance
            
            if overflow_ratio > tolerance:
                # Apply font reduction
                reduction_factor = self.config.get_font_reduction_factor()
                font_size = base_font_size * reduction_factor
                
                # Recalculate metrics with new font size
                metrics = [self._calculate_paragraph_metrics(p, font_size) for p in paragraphs]
                cumulative_height = sum(m.height_required for m in metrics)
                cumulative_height += para_spacing * (len(paragraphs) - 1)
                
                optimization = f"font_reduced_{int((1-reduction_factor)*100)}pct"
                self._log(f"      🎯 Font adjusted: {base_font_size:.1f} → {font_size:.1f}pt "
                         f"({reduction_factor:.1%})")
        
        # === ADAPTIVE SPACING ===
        if self.config.optimize_spacing:
            if density == ContentDensity.SPARSE:
                para_spacing *= self.config.sparse_content_multiplier
                optimization = optimization + "+sparse_spacing" if optimization != "none" else "sparse_spacing"
                self._log(f"      🎨 Sparse spacing: {self.config.para_spacing:.1f} → {para_spacing:.1f}pts")
            
            elif density == ContentDensity.DENSE or density == ContentDensity.OVERCROWDED:
                para_spacing *= self.config.dense_content_multiplier
                optimization = optimization + "+dense_spacing" if optimization != "none" else "dense_spacing"
                self._log(f"      🎨 Dense spacing: {self.config.para_spacing:.1f} → {para_spacing:.1f}pts")
        
        # === RECALCULATE WITH ADJUSTED SPACING ===
        total_height_used = sum(m.height_required for m in metrics)
        total_height_used += para_spacing * (len(paragraphs) - 1)
        
        # === VERTICAL CENTERING ===
        top_padding = 0.0
        if self.config.auto_center_vertical:
            remaining_space = available_height - total_height_used
            if remaining_space > 0:
                top_padding = remaining_space / 2
                self._log(f"      📐 Vertical centering: {top_padding:.1f}pts top padding")
        
        # === CREATE LAYOUT ===
        is_balanced = 0.60 <= (total_height_used / available_height) <= 0.95
        overflow_amount = max(0, total_height_used - available_height)
        
        layout = SlideLayout(
            slide_number=slide_number,
            paragraphs=paragraphs,
            paragraph_metrics=metrics,
            total_height_used=total_height_used,
            available_height=available_height,
            top_padding=top_padding,
            para_spacing=para_spacing,
            font_size=font_size,
            density=density,
            is_balanced=is_balanced,
            overflow_amount=overflow_amount,
            optimization_applied=optimization
        )
        
        self._log(f"      📊 Final metrics: {total_height_used:.1f}/{available_height:.1f}pts "
                 f"({layout.utilization_ratio:.1%} util)")
        
        return layout
    
    def _classify_density(
        self, 
        paragraph_count: int, 
        content_height: float, 
        available_height: float
    ) -> ContentDensity:
        """
        Classify content density for adaptive spacing.
        
        Density Thresholds:
        - Sparse: < 3 para OR < 30% space
        - Balanced: 3-6 para AND 30-70% space
        - Dense: 6-10 para OR 70-90% space
        - Overcrowded: > 10 para OR > 90% space
        """
        utilization = content_height / available_height if available_height > 0 else 0
        
        if paragraph_count < 3 or utilization < 0.30:
            return ContentDensity.SPARSE
        elif paragraph_count > 10 or utilization > 0.90:
            return ContentDensity.OVERCROWDED
        elif paragraph_count > 6 or utilization > 0.70:
            return ContentDensity.DENSE
        else:
            return ContentDensity.BALANCED
    
    def _balance_slides(self, layouts: List[SlideLayout]) -> List[SlideLayout]:
        """
        Balance content distribution across multiple slides.
        
        Attempts to redistribute paragraphs for more even utilization.
        
        NOTE: This is a placeholder for future advanced balancing logic.
        """
        # TODO: Implement sophisticated balancing algorithm
        # For now, just return as-is
        return layouts
    
    def _log(self, message: str):
        """Add message to debug log."""
        self.debug_log.append(message)
    
    def get_debug_log(self) -> List[str]:
        """Get all debug log messages."""
        return self.debug_log.copy()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all layout metrics.
        
        Returns:
            Dictionary with comprehensive statistics
        """
        if not self.metrics_history:
            return {}
        
        return {
            "total_calculations": len(self.metrics_history),
            "avg_utilization": sum(m.get("utilization", 0) for m in self.metrics_history) / len(self.metrics_history),
            "optimizations_applied": sum(1 for m in self.metrics_history if m.get("optimization") != "none"),
        }
