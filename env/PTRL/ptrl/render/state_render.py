import graphviz
from IPython.display import display, Image  


class Graph():
    
    def __init__(self, sim):
        self.sim = sim
        
    def render(self ,action= None ):
        
        dot = graphviz.Digraph(comment='Petri Net')
        # Add places
        for place in self.sim.jobs + self.sim.agvs + self.sim.ready + self.sim.store + self.sim.machines + self.sim.delivery:
            dot.node(place.uid, shape='circle', label=str (len(place.token_container)), style='filled', fillcolor='white', fontsize='10')
        
        # Add controllable transitions
        for transition in self.sim.select + self.sim.allocate:
            if transition.enabled == True:
                dot.node(transition.uid, shape='box', label=transition.label, style='filled', fillcolor='white', fontsize='10', height='0.2')
            else:
                dot.node(transition.uid, shape='box', label=transition.label, style='filled', fillcolor='darkgrey', fontsize='10', height='0.2')
        
        # Add transitions
        for transition in self.sim.buffer + self.sim.deliver+ self.sim.lu:
            dot.node(transition.uid, shape='box', label=transition.label, style='filled', fillcolor='white', fontsize='10', height='0.2')
        
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
