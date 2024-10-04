import copy
from collections import defaultdict

class IdGen:
    """
    Class for generating unique IDs.
    """
    uid_counter = 0

    @classmethod
    def generate_uid(cls):
        """
        Generate a unique ID.

        Returns:
            str: Unique ID generated.
        """
        uid = cls.uid_counter
        cls.uid_counter += 1
        return str(uid)
    
    @classmethod
    def reset(cls):
       """
       Reset the unique ID counter to zero.
       """
       cls.uid_counter = 0

class Place:
    """
    Class representing a place in a Petri net.

    Attributes:
        uid (str): Unique identifier for the place.
        label (str): Name or label of the place.
        type (str): Type of the place (e.g., 'p' for process, 'f' for flag).
        role (str): Role of the place (e.g., machine processing).
        parents (list): List of parent nodes (transitions).
        children (list): List of child nodes (transitions).
        token_container (list): List of tokens currently in the place.
        color: Color attribute for the place.
        timed (bool): Whether the place is timed.
        show (bool): Whether the place is visible.
    """

    def __init__(self, label, type_="", role="", color=None, timed=False, show=True):
        """
        Initialize a place.

        Parameters:
            label (str): Name or label of the place.
            type_ (str): Type of the place (e.g., 'p' for process, 'f' for flag).
            role (str): Role of the place (e.g., machine processing).
            color: Color attribute for the place.
            timed (bool): Whether the place is timed.
            show (bool): Whether the place is visible.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = type_
        self.role = role
        self.color = color
        self.timed = timed
        self.enabled = True
        

        self.parents = []
        self.children = []
        self.token_container = []
        self.show = show
        
        self.history = [0]
        
 

    def add_arc(self, node, parent=True):
        """
        Add an arc (connection) between the place and a node.

        Parameters:
            node: The node to connect.
            parent (bool): True if the node is a parent (transition), False if a child.
        """
        if parent:
            self.parents.append(node)
        else:
            self.children.append(node)

    def __str__(self):
        """
        Get a string representation of the place.

        Returns:
            str: A string representing the place.
        """
        return f"Place name: {self.label}, Type: {self.type}, Role: {self.role}, Tokens: {len(self.token_container)}, Color: {self.color}, Parents: {[p.uid for p in self.parents]}, Children: {[c.uid for c in self.children]}, ID: {self.uid}"

    def tick(self):
        """
        Perform a time tick for tokens in the place.
        """
        if self.token_container:
            for token in self.token_container:  
                token.logging[self.uid][2]+= 1 
                

    def error_check(self):
        """
        Check for errors in token color matching.
        """
        if self.token_container and self.color is not None:
            for token in self.token_container:
                if self.color != token.color[1]:
                    print(f"Wrong token detected in place {self.label}")

class Transition:
    """
    Class representing a transition in a Petri net.

    Attributes:
        uid (str): Unique identifier for the transition.
        label (str): Name or label of the transition.
        type (str): Type of the transition (e.g., 'c' for controllable, 'a' for automatic).
        role (str): Role of the transition (e.g., allocate).
        color: Color attribute for the transition.
        parents (list): List of parent nodes (places).
        children (list): List of child nodes (places).
        enabled (bool): Flag indicating whether the transition is enabled.
        timed (bool): Whether the transition is timed.
        show (bool): Whether the transition is visible.
    """

    def __init__(self, label, type_="", role="", color=None, timed=False, show=True):
        """
        Initialize a transition.

        Parameters:
            label (str): Name or label of the transition.
            type_ (str): Type or role of the transition.
            role (str): Role of the transition (e.g., allocate).
            color: Color attribute for the transition.
            timed (bool): Whether the transition is timed.
            show (bool): Whether the transition is visible.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = type_
        self.role = role
        self.color = color
        self.colored=False
        self.timed = timed

        self.parents = []
        self.children = []
        self.show = show

    def add_arc(self, node, parent=True):
        """
        Add an arc (connection) between the transition and a node.

        Parameters:
            node: The node to connect.
            parent (bool): True if the node is a parent (place), False if a child.
        """
        if parent:
            self.parents.append(node)
        else:
            self.children.append(node)

    def __str__(self):
        """
        Get a string representation of the transition.

        Returns:
            str: A string representing the transition.
        """
        return f"Transition name: {self.label}, Type: {self.type}, Role: {self.role}, Color: {self.color}, Parents: {[p.uid for p in self.parents]}, Children: {[c.uid for c in self.children]}, ID: {self.uid}"

    def check_state(self):
        """
        Check the state of the transition to determine if it is enabled.
        """  

        colors_lists = [set(token.color for token in parent.token_container)  for parent in self.parents if parent.type != "f"]
        common_found = bool (set.intersection(*colors_lists))
        
        available_tokens =all(parent.token_container for parent in self.parents)
        
        if len([parent for parent in self.parents if parent.type != "f"])==1:
            self.enabled = available_tokens  
        else : # merging resources
            self.enabled = available_tokens  and common_found
            
        return  self.enabled
        
        pass
    
    
    
    def fire(self, instance, clock=0):
        """
        Fire the transition to move tokens from parent places to child places.
        Parameters:
            clock (int): The current simulation clock.
        """

        non_flag = [parent for parent in self.parents if parent.type != "f"]
        if len(non_flag)>=1:
            token= non_flag[0].token_container[0]

        for child in self.children:
            token.logging[child.uid] = [clock, 0, 0]
            child.token_container.append(token)
            child.history.append(token.color[1])
              
        for parent in self.parents:
            parent.token_container.pop(0)
            
class Token:
    """
    Class representing a token in a Petri net.

    Attributes:
        uid (str): Unique identifier for the token.
        color (tuple): Tuple representing the color of the token (job_color, machine_color).
        order (int): Order of the operation in the job.
        process_time (int): Time taken for the token's process.
        trans_time (int): Transportation time for the token to move between machines.
        logging (dict): Dictionary for logging entry time, leave time, and elapsed time for each place.
    """

    def __init__(self, uid = None ,initial_place="", type_="", role="op",rank=0, color=(0,0,0), time_features=[0,0,0],machine_sequence=(0,0,0)):
        """
        Initialize a token.

        Parameters:
            initial_place (str): The initial place where the token is located.
            type_ (str): Type of the token (e.g., colored, non-colored).
            role (str): Role of the token (e.g., op: operation, lu: load/unload, f: flag).
            color (tuple): Tuple representing the color of the token (job_color, machine_color).
            rank (int): Order of the operation in the job.
            process_time (int): Time taken for the token's process.
            trans_time (int): Transportation time for the token to move between machines.
        """
        
        if uid == None :
            self.uid = IdGen.generate_uid()
        else :
            self.uid=uid
  
    
        self.rank = rank
        self.type_ = type_
        self.role = role
        self.color = color
        
        self.time_features=time_features  # 0 :process_time  1:agv_transport 2: tool_transport 
        self.logging = {initial_place: [0, 0, 0]}  # entry time, leave time, elapsed time
        
        self.machine_sequence=machine_sequence  #(previous machine,current machine,next_machine)
        self.deadheadings=[]
        

    def __str__(self):
        """
        Get a string representation of the token.

        Returns:
            str: A string representing the token.
        """
        return f"ID: {self.uid}, Rank: {self.rank}, Type: {self.type_}, Color: {self.color}, Time features: {self.time_features}, Logging: {self.logging}  ,Sequence:{self.machine_sequence}"
