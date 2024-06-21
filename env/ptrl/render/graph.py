import graphviz
from IPython.display import display, Image  


class Graph():
    
    def __init__(self, sim):
        self.sim = sim
        
    def plot_net(self ,action= None ):
        
        dot = graphviz.Digraph(comment='Petri Net')
        # Add places
        for place in self.sim.places.values():
            dot.node(place.uid, shape='circle', label=str(len(place.token_container)), style='filled', fillcolor='white', fontsize='10')
        
        
        # Add transitions
        for transition in self.sim.transitions.values():
            
           if transition.type=="a":
               dot.node(transition.uid, shape='box', label="", style='filled', fillcolor='grey', fontsize='10', height='0.2')
               
           else :
               
               if transition.enabled :
                   dot.node(transition.uid, shape='box', label="", style='filled', fillcolor='white', fontsize='10', height='0.2')
                    
               else :
                   dot.node(transition.uid, shape='box', label="", style='filled', fillcolor='black', fontsize='10', height='0.2')
                     
  
    
  
        # Add arcs
        for place in self.sim.places.values():
            for child in place.children:
                dot.edge(place.uid, child.uid)
 
        for transition in self.sim.transitions.values():
            for child in transition.children:
                dot.edge(transition.uid, child.uid)
        
        # Render the graph
        dot_data = dot.pipe(format='png')
        display(Image(dot_data))

if __name__ == "__main__":
    # Example usage
    pass
