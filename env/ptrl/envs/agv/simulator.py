from ptrl.envs.agv.petri_build import Petri_build
from ptrl.render.graph import  Graph

class Simulator(Petri_build):
    """
    A class representing the core logic of a Job Shop Scheduling Problem (JSSP) simulation using a Petri net.

    Attributes:
        clock (int): The internal clock of the simulation.
        interaction_counter (int): Counter for interactions in the simulation.
        delivery_history (dict): Dictionary storing the delivery history.
        action_map (dict): Mapping of actions in the simulation from discrete numbers to transition objects.

    Methods:
        __init__(instance_id, dynamic=False, size=(None, None), n_agv=2):
            Initializes the JSSP Simulator with the specified parameters.
        petri_reset():
            Resets the internal state of the Petri net.
        action_mapping():
            Maps actions  integers to transition objects  .
        is_terminal():
            Checks if the simulation has reached a terminal state.
        action_masks():
            Checks which allocations are enabled.
        refresh_state():
            Refreshes the state by sorting tokens and updating transitions.
        sort_tokens():
            Sorts tokens in specific places based on defined criteria.
        fire_timed():
            Fires timed transitions based on completion times.
        fire_controlled(action):
            Fires colored transitions based on the provided action.
        time_tick():
            Increments the internal clock and updates token logging.
        interact(action, screenshot=False):
            Performs Petri net interactions and updates the internal state.
    """

    def __init__(self, instance_id, dynamic=False, size=(None, None), n_agv=2):
        """
        Initializes the JSSP Simulator.

        Parameters:
            instance_id (str): Identifier for the JSSP instance.
            dynamic (bool): If True, appending new operations is possible, and the termination condition is that all queues are empty.
            size (tuple): Size of the simulation environment.
            n_agv (int): Number of AGVs (Automated Guided Vehicles) used in the simulation.
        """
        super().__init__(instance_id, dynamic=dynamic, benchmark='BU', size=size, n_agv=n_agv)

        self.clock = 0
        self.interaction_counter = 0
        self.delivery_history = {}
        self.action_map = self.action_mapping()
        self.graph = Graph(self)

        self.petri_reset()
        # self.graph.plot_net()

    def petri_reset(self):
        """
        Resets the internal state of the Petri net.
        """
        self.clock = 0
        for place in self.places.values():
            place.token_container = []

        self.add_tokens()
        self.refresh_state()

    def action_mapping(self):
        """
        Maps multidiscrete actions to a more versatile discrete format for use with experimental DQN.

        Returns:
            dict: Mapping dictionary from action number to transition object.
        """
        controllable_transitions = [t for t in self.transitions.values() if t.type == "c"]
        mapping_dict = {index: value for index, value in enumerate(controllable_transitions)}
        return mapping_dict

    def is_terminal(self):
        """
        Checks if the simulation has reached a terminal state.
        Returns:
            bool: True if the terminal state is reached, False otherwise.
        """
        process_places = [p for p in self.places.values() if p.type not in ["d", "f"]]
        empty_process = all(len(p.token_container) == 0 for p in process_places)
        return empty_process

    def action_masks(self):
        """
        Checks which allocations are enabled.

        Returns:
            list: List of boolean values indicating the enabled status of each transition.
        """
        self.refresh_state()
        mask = [t.enabled for t in self.transitions.values() if t.type == "c"]
        return mask


    def sort_tokens(self):
        """
        Sorts tokens in specific places based on defined criteria.
        """
        def process_tokens(place, color_criterion_index):
            if not place.token_container:
                return

            for token in place.token_container.copy():
                for transition in place.children:
                    if token.color[color_criterion_index] == transition.color:
                        transition.fire(clock=self.clock)

        for place in (p for p in self.places.values() if p.type == "s"):
            if place.role == "job_sorting":
                process_tokens(place, 0)
            elif place.role == "machine_sorting":
                process_tokens(place, 1)
                
                
    def refresh_state(self):
        """
        Refreshes the state by sorting tokens and updating transitions.
        """
        self.sort_tokens()
        for transition in self.action_map.values():
            transition.check_state()
            

    def fire_timed(self):
        """
        Fires timed transitions based on completion times.
        Returns:
            list: List of fired transition IDs.
        """
        fired_transitions = []

        def process_tokens(place, time_criterion):
            if not place.token_container:
                return

            transition = place.children[0]
            token = place.token_container[0]
            elapsed_time = next(reversed(token.logging.values()))[2]

            if elapsed_time >= getattr(token, time_criterion):
                transition.fire(clock=self.clock)
                fired_transitions.append(transition.uid)

        for place in (p for p in self.places.values() if p.type == "p"):
            if place.role in ["agv_transporting"]:
                process_tokens(place, "trans_time")
            elif place.role in ["machine_processing"]:
                process_tokens(place, "process_time")

        self.refresh_state()

        self.delivery_history[self.clock] = [
            token for place in self.places.values() if place.type == "d" for token in place.token_container
        ]

        return fired_transitions

    def fire_controlled(self, action):
        """
        Fires colored transitions based on the provided action.

        Parameters:
            action: Action to be performed.

        Returns:
            list: List of fired transition IDs.
        """
        fired_transitions = []
        if action in [index for index, value in enumerate(self.action_masks()) if value]:
            self.interaction_counter += 1
            transition = self.action_map[int(action)]
            transition.fire(clock=self.clock)
            self.refresh_state()
            fired_transitions.append(transition.uid)

        return fired_transitions

    def time_tick(self):
        """
        Increments the internal clock and updates token logging.
        """
        self.clock += 1
        for place in [p for p in self.places.values() if p.type == "p"]:
            place.tick()

    def interact(self, action, screenshot=False):
        """
        Performs Petri net interactions and updates the internal state.

        Parameters:
            action: Action to be performed.
            screenshot (bool): If True, takes a screenshot of the net after firing transitions.
        """
        fired_controlled = self.fire_controlled(action)
        self.graph.plot_net(fired_controlled) if screenshot else None

        while not any(self.action_masks()):
            self.time_tick()
            fired_timed = self.fire_timed()
            self.graph.plot_net(fired_timed) if screenshot else None

            if self.is_terminal():
                break


if __name__ == "__main__":
    petri = Simulator("bu10")
    petri.graph.plot_net()
