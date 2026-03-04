from typing import List, Tuple
from difflib import SequenceMatcher

def fuzzy_match(s1: str, s2: str) -> float:
    """Calculate fuzzy similarity between two strings"""
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()

def evaluate_action_items(
    predicted: List[str],
    gold: List[str],
    threshold: float = 0.6
) -> Tuple[float, float, float, List[Tuple[str, str, float]]]:
    """
    Evaluate predicted action items against gold standard.
    Returns (precision, recall, f1, matches)
    """
    if not predicted and not gold:
        return 1.0, 1.0, 1.0, []
    
    if not predicted:
        return 0.0, 0.0, 0.0, []
    
    if not gold:
        return 0.0, 0.0, 0.0, []
    
    matches = []
    matched_gold = set()
    
    for pred in predicted:
        best_match = None
        best_score = 0.0
        best_gold_idx = -1
        
        for idx, g in enumerate(gold):
            if idx in matched_gold:
                continue
            score = fuzzy_match(pred, g)
            if score > best_score:
                best_score = score
                best_match = g
                best_gold_idx = idx
        
        if best_score >= threshold:
            matches.append((pred, best_match, best_score))
            matched_gold.add(best_gold_idx)
    
    true_positives = len(matches)
    precision = true_positives / len(predicted) if predicted else 0.0
    recall = true_positives / len(gold) if gold else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1, matches

def compute_citation_coverage(action_items) -> float:
    """Calculate percentage of action items with source quotes"""
    if not action_items:
        return 0.0
    with_quotes = sum(1 for item in action_items if item.source_quote.strip())
    return with_quotes / len(action_items)

def compute_low_confidence_rate(action_items, threshold: float = 0.55) -> float:
    """Calculate percentage of low confidence action items"""
    if not action_items:
        return 0.0
    low_conf = sum(1 for item in action_items if item.confidence < threshold)
    return low_conf / len(action_items)
