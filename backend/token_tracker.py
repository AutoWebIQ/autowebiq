# Token Usage Tracker for Emergent-Style Credit System
# Tracks actual token usage from LLM API calls in real-time

from typing import Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class TokenTracker:
    """Tracks token usage across LLM API calls for accurate credit deduction"""
    
    def __init__(self):
        self.session_tokens = {}  # {session_id: {agent: tokens}}
        
        # Token-to-credit conversion (Emergent-style: ~1000 tokens = 1 credit)
        self.tokens_per_credit = 1000
        
        # Model-specific token costs (some models cost more per token)
        self.model_multipliers = {
            "gpt-5": 1.5,
            "gpt-4o": 1.0,
            "claude-sonnet-4-20250514": 1.2,
            "gemini-2.5-pro": 0.8,
            "dall-e-3": 12.0  # Image generation (flat cost per image)
        }
    
    def start_session(self, session_id: str):
        """Initialize token tracking for a new build session"""
        self.session_tokens[session_id] = {
            'total_tokens': 0,
            'agents': {},
            'started_at': datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"Started token tracking session: {session_id}")
    
    def track_tokens(
        self,
        session_id: str,
        agent_type: str,
        input_tokens: int,
        output_tokens: int,
        model: str = "gpt-4o"
    ) -> Dict:
        """
        Track tokens used by an agent
        
        Returns:
            {
                'tokens_used': int,
                'credits_used': float,
                'session_total_tokens': int,
                'session_total_credits': float
            }
        """
        if session_id not in self.session_tokens:
            self.start_session(session_id)
        
        total_tokens = input_tokens + output_tokens
        
        # Apply model multiplier
        multiplier = self.model_multipliers.get(model, 1.0)
        effective_tokens = total_tokens * multiplier
        
        # Calculate credits
        credits_used = effective_tokens / self.tokens_per_credit
        
        # Update session tracking
        if agent_type not in self.session_tokens[session_id]['agents']:
            self.session_tokens[session_id]['agents'][agent_type] = {
                'tokens': 0,
                'credits': 0.0,
                'calls': 0
            }
        
        self.session_tokens[session_id]['agents'][agent_type]['tokens'] += total_tokens
        self.session_tokens[session_id]['agents'][agent_type]['credits'] += credits_used
        self.session_tokens[session_id]['agents'][agent_type]['calls'] += 1
        self.session_tokens[session_id]['total_tokens'] += total_tokens
        
        logger.info(f"[{session_id}] {agent_type}: {total_tokens} tokens ({credits_used:.2f} credits)")
        
        return {
            'tokens_used': total_tokens,
            'credits_used': round(credits_used, 2),
            'session_total_tokens': self.session_tokens[session_id]['total_tokens'],
            'session_total_credits': round(
                sum(a['credits'] for a in self.session_tokens[session_id]['agents'].values()),
                2
            )
        }
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get complete summary of token usage for a session"""
        if session_id not in self.session_tokens:
            return {
                'total_tokens': 0,
                'total_credits': 0.0,
                'agents': {}
            }
        
        session_data = self.session_tokens[session_id]
        total_credits = sum(a['credits'] for a in session_data['agents'].values())
        
        return {
            'total_tokens': session_data['total_tokens'],
            'total_credits': round(total_credits, 2),
            'agents': {
                agent: {
                    'tokens': data['tokens'],
                    'credits': round(data['credits'], 2),
                    'calls': data['calls']
                }
                for agent, data in session_data['agents'].items()
            },
            'started_at': session_data['started_at'],
            'ended_at': datetime.now(timezone.utc).isoformat()
        }
    
    def end_session(self, session_id: str) -> Dict:
        """End tracking session and return final summary"""
        summary = self.get_session_summary(session_id)
        
        # Clean up session data
        if session_id in self.session_tokens:
            del self.session_tokens[session_id]
        
        logger.info(f"Ended token tracking session {session_id}: {summary['total_credits']} credits")
        
        return summary

# Global instance
_token_tracker = None

def get_token_tracker():
    """Get or create token tracker instance"""
    global _token_tracker
    if _token_tracker is None:
        _token_tracker = TokenTracker()
    return _token_tracker
