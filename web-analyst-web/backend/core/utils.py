from core.schemas import ExtractionResult, SourceResult
from typing import List

def generate_report_markdown(extraction: ExtractionResult) -> str:
    """Generate markdown report from extraction results"""
    
    md = "# Web Content Analysis Report\n\n"
    
    # Combined summary
    md += "## Overall Summary\n\n"
    md += f"{extraction.combined.overall_summary}\n\n"
    
    # Cross-source insights
    if extraction.combined.cross_source_agreements:
        md += "### Agreements Across Sources\n\n"
        for agreement in extraction.combined.cross_source_agreements:
            md += f"- {agreement}\n"
        md += "\n"
    
    if extraction.combined.cross_source_conflicts:
        md += "### Conflicts or Differences\n\n"
        for conflict in extraction.combined.cross_source_conflicts:
            md += f"- {conflict}\n"
        md += "\n"
    
    # Final action plan
    if extraction.combined.final_action_plan:
        md += "## Final Action Plan\n\n"
        for i, action in enumerate(extraction.combined.final_action_plan, 1):
            md += f"{i}. {action}\n"
        md += "\n"
    
    # Per-source details
    md += "## Source Details\n\n"
    
    for source in extraction.sources:
        md += f"### {source.title}\n\n"
        md += f"**URL:** {source.url}\n\n"
        md += f"**Type:** {source.type}\n\n"
        md += f"**Summary:** {source.summary}\n\n"
        
        if source.key_points:
            md += "**Key Points:**\n\n"
            for point in source.key_points:
                md += f"- {point}\n"
            md += "\n"
        
        if source.recommendations_or_decisions:
            md += "**Recommendations/Decisions:**\n\n"
            for rec in source.recommendations_or_decisions:
                md += f"- {rec}\n"
            md += "\n"
        
        if source.open_questions:
            md += "**Open Questions:**\n\n"
            for q in source.open_questions:
                md += f"- {q}\n"
            md += "\n"
        
        if source.risks_or_ambiguities:
            md += "**Risks/Ambiguities:**\n\n"
            for risk in source.risks_or_ambiguities:
                md += f"- {risk}\n"
            md += "\n"
        
        md += "---\n\n"
    
    # Confidence notes
    if extraction.combined.confidence_notes:
        md += "## Confidence Notes\n\n"
        for note in extraction.combined.confidence_notes:
            md += f"- {note}\n"
        md += "\n"
    
    return md

def export_report(extraction: ExtractionResult, filename: str = "report.md"):
    """Export report to markdown file"""
    md = generate_report_markdown(extraction)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)
    return filename
