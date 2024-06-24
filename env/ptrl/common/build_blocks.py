class IdGen:
    """
    Class for generating unique IDs.
    """
    uid_counter = 0

    @classmethod
    def generate_uid(cls):     
        uid = cls.uid_counter
        cls.uid_counter += 1
        return str(uid)

class Place:
    """
    Class representing a place in a Petri net.

    Attributes:
        uid (str): Unique identifier for the place.
        label (str): Name or label of the place.
        type (str): Type the place.
        role (str): Role of the place example : machine processing .
        parents (list): List of parent nodes (transitions).
        children (list): List of child nodes (transitions).
        token_container (list): List of tokens currently in the place.
        color: Color attribute for the place.
    """

    def __init__(self, label, type_="",role="" , color=None, timed=False, show=True):
        """
        Initialize a place.

        Parameters:
            label (str): Name or label of the place.
            type (str): type of the place p for process , f for flag .
            role (str): Role of the place example machine processing .
            color: Color attribute for the place.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = type_
        self.role = role 
        self.color = color
        self.timed = timed
        self.enabled = False   
      

        self.parents = []
        self.children = []
        self.token_container = []
        
        
        self.show=show

     

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
        return f"Place name: {self.label}, Type: {self.type}, Role: {self.role}, Tokens: {len(self.token_container)}, color: {self.color}, parents: {[p.uid for p in self.parents]}, children: {[c.uid for c in self.children]}, id: {self.uid}"


class Transition:
    """
    Class representing a transition in a Petri net.

    Attributes:
        uid (str): Unique identifier for the transition.
        label (str): Name or label of the transition.
        type (str): Type  of the transition example : c : controllable / a : automatic 
        role (str): role of the transition example : allocate .
        color: Color attribute for the transition.
        parents (list): List of parent nodes (places).
        children (list): List of child nodes (places).
        enabled (bool): Flag indicating whether the transition is enabled.
    """

    def __init__(self, label, type_="",role =""  ,color=None,timed=False ,show=True):
        """
        Initialize a transition.

        Parameters:
            label (str): Name or label of the transition.
            role (str): Type or role of the transition.
            color: Color attribute for the transition.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = type_
        self.role = role 
        self.color = color
        self.timed = timed
        self.enabled = False   
       
        self.parents = []
        self.children = []
        
        
        self.show=show
        


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
        return f"Transition name: {self.label}, Type: {self.type}, Role: {self.role}, color: {self.color}, parents: {[p.uid for p in self.parents]}, children: {[c.uid for c in self.children]}, id: {self.uid}"


class Token:
    """
    Class representing a token in a Petri net.

    Attributes:
        uid (str): Unique identifier for the token.
        color (tuple): Tuple representing the color of the token (job_color, machine_color).
        features (list) : a list containing the features of the token feature [0] is reserved for processing time
        order (int): Order of  the operation in the job  .
        logging (dict): Dictionary for logging entry time, leave time, and elapsed time for each place.
    """

    def __init__(self, initial_place="",type_="",role="op", color=(None, None), order=0,process_time=0  , trans_time=0 ):
        """
        Initialize a token.

        Parameters:
            initial_place: The initial place where the token is located.
            type (str) : 
            role (str): can be op: operation , lu : load/ unload , f:  flag ....  
            color (tuple): Tuple representing the color of the token (job_color, machine_color).
            order (int): Order of the token.
            process_time (int): Time taken for the token's process.
            transportation_time (int) : the time the operation take to move from  machine to another if not given = 0
            logging (dict) : a logging of every place the token went throught 
        """
        
        self.uid = IdGen.generate_uid()
        self.order = order
        
        self.type=type_
        self.role = role
        self.color = color
        self.trans_time=trans_time
        self.process_time = process_time
        self.logging = {initial_place: [0, 0, 0]}  # entry time, leave time, elapsed time
   

    def __str__(self):

        return f"id: {self.uid}, Order: {self.order}, Type: {self.type}, Color: {self.color}, Process_time: {self.process_time}, Trans_time :{self.trans_time}, Logging: {self.logging}"
