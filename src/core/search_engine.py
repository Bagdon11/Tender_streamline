"""
Search Engine - Implement document search functionality
"""

import re
from typing import Dict, List, Any
from collections import defaultdict
import math

class SearchEngine:
    """Simple search engine for document content with TF-IDF scoring."""
    
    def __init__(self):
        self.documents: Dict[str, str] = {}
        self.word_frequencies: Dict[str, Dict[str, int]] = {}
        self.document_frequencies: Dict[str, int] = defaultdict(int)
        self.total_documents = 0
    
    def add_document(self, doc_id: str, content: str):
        """Add a document to the search index."""
        self.documents[doc_id] = content
        
        # Tokenize and count words
        words = self._tokenize(content)
        word_freq = defaultdict(int)
        
        for word in words:
            word_freq[word] += 1
            
        self.word_frequencies[doc_id] = dict(word_freq)
        
        # Update document frequencies
        unique_words = set(words)
        for word in unique_words:
            self.document_frequencies[word] += 1
            
        self.total_documents = len(self.documents)
    
    def remove_document(self, doc_id: str):
        """Remove a document from the search index."""
        if doc_id not in self.documents:
            return
            
        # Update document frequencies
        words = set(self._tokenize(self.documents[doc_id]))
        for word in words:
            self.document_frequencies[word] -= 1
            if self.document_frequencies[word] <= 0:
                del self.document_frequencies[word]
        
        # Remove document
        del self.documents[doc_id]
        del self.word_frequencies[doc_id]
        
        self.total_documents = len(self.documents)
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with scores and snippets
        """
        if not self.documents:
            return []
            
        query_words = self._tokenize(query.lower())
        if not query_words:
            return []
        
        # Calculate TF-IDF scores for each document
        scores = {}
        
        for doc_id in self.documents:
            score = self._calculate_tfidf_score(doc_id, query_words)
            if score > 0:
                scores[doc_id] = score
        
        # Sort by score (descending)
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare results with snippets
        results = []
        for doc_id, score in sorted_results[:max_results]:
            snippet = self._generate_snippet(self.documents[doc_id], query_words)
            results.append({
                'document': doc_id,
                'score': score,
                'snippet': snippet
            })
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out very short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                      'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        
        filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return filtered_words
    
    def _calculate_tfidf_score(self, doc_id: str, query_words: List[str]) -> float:
        """Calculate TF-IDF score for a document given query words."""
        if doc_id not in self.word_frequencies:
            return 0.0
            
        score = 0.0
        doc_word_count = sum(self.word_frequencies[doc_id].values())
        
        for word in query_words:
            if word in self.word_frequencies[doc_id]:
                # Term frequency
                tf = self.word_frequencies[doc_id][word] / doc_word_count
                
                # Inverse document frequency
                if word in self.document_frequencies:
                    idf = math.log(self.total_documents / self.document_frequencies[word])
                else:
                    idf = 0
                
                # TF-IDF score
                score += tf * idf
        
        return score
    
    def _generate_snippet(self, content: str, query_words: List[str], max_length: int = 200) -> str:
        """Generate a snippet showing query words in context."""
        # Find sentences containing query words
        sentences = re.split(r'[.!?]+', content)
        
        best_sentence = ""
        max_word_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
                
            sentence_lower = sentence.lower()
            word_count = sum(1 for word in query_words if word in sentence_lower)
            
            if word_count > max_word_count:
                max_word_count = word_count
                best_sentence = sentence
        
        # If no good sentence found, use beginning of document
        if not best_sentence:
            best_sentence = content[:max_length]
        
        # Truncate if too long
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."
            
        return best_sentence