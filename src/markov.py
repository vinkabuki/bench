import random
import numpy as np
from typing import Dict, List, Tuple, Any

class MarkovChain:
    def __init__(self):
        self.transitions = {}
        self.states = set()
    
    def add_transition(self, from_state: Any, to_state: Any, probability: float = None):
        """
        Add a transition to the Markov chain.
        
        Args:
            from_state: The starting state
            to_state: The destination state
            probability: Transition probability (will be normalized later)
        """
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        
        if probability is None:
            probability = 1.0
            
        self.transitions[from_state][to_state] = probability
        self.states.add(from_state)
        self.states.add(to_state)
    
    def normalize_probabilities(self):
        """Normalize the transition probabilities so they sum to 1 for each state."""
        for state, transitions in self.transitions.items():
            total = sum(transitions.values())
            if total > 0:
                for to_state in transitions:
                    self.transitions[state][to_state] /= total
    
    def next_state(self, current_state: Any) -> Any:
        """
        Generate the next state based on transition probabilities.
        
        Args:
            current_state: The current state
            
        Returns:
            The next state
        """
        if current_state not in self.transitions:
            return None
        
        transitions = self.transitions[current_state]
        states = list(transitions.keys())
        probabilities = list(transitions.values())
        
        return random.choices(states, weights=probabilities, k=1)[0]
    
    def generate_sequence(self, start_state: Any, length: int) -> List[Any]:
        """
        Generate a sequence of states using the Markov chain.
        
        Args:
            start_state: The initial state
            length: The length of the sequence to generate
            
        Returns:
            A list of generated states
        """
        if start_state not in self.states:
            raise ValueError(f"Start state '{start_state}' not in Markov chain")
        
        sequence = [start_state]
        current = start_state
        
        for _ in range(length - 1):
            next_state = self.next_state(current)
            if next_state is None:
                break
            sequence.append(next_state)
            current = next_state
            
        return sequence

def create_text_markov_chain(text: str, order: int = 1) -> MarkovChain:
    """
    Create a Markov chain from text.
    
    Args:
        text: The input text
        order: The order of the Markov chain (how many previous words to consider)
        
    Returns:
        A MarkovChain object
    """
    words = text.split()
    markov = MarkovChain()
    
    for i in range(len(words) - order):
        from_state = tuple(words[i:i+order])
        to_state = words[i+order]
        markov.add_transition(from_state, to_state)
    
    markov.normalize_probabilities()
    return markov
