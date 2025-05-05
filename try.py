import networkx as nx
from opennlp import TokenNameFinderModel, TokenizerModel
from opennlp import SimpleTokenizer
import requests

# Load OpenNLP models
tokenizer_model = TokenizerModel(open('en-token.bin', 'rb'))
token_name_model = TokenNameFinderModel(open('en-ner-person.bin', 'rb'))

tokenizer = SimpleTokenizer(tokenizer_model)
token_finder = TokenNameFinderModel(token_name_model)

def create_graph_from_text(text):
    # Tokenize the input text
    tokens = tokenizer.tokenize(text)
    
    # Process text and create graph nodes
    graph = nx.Graph()
    
    # Example: adding persons as nodes in the graph
    for token in tokens:
        if token in token_finder.find(tokens):
            graph.add_node(token)
            graph.add_edge('text', token)  # Example: linking 'text' as a central node
    
    return graph

# Example input
text = "Barack Obama and Elon Musk met in New York."
graph = create_graph_from_text(text)

# Visualize the graph (use matplotlib for visualization)
import matplotlib.pyplot as plt

nx.draw(graph, with_labels=True)
plt.show()
