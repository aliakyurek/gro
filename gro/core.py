import gradio as gr

class Block:
    def __init__(self, **init_kwargs):
        """
        Initializes the Block instance with the provided arguments.

        Args:
            **init_kwargs: Keyword arguments to pass to the Gradio block constructor.
        """
        self.init_args = init_kwargs

    def start(self, **launch_kwargs):
        """
        Starts the Gradio UI by setting up the layout and initializing listeners.
        
        This method initializes all instances of the `Wrapper` class, sets up dynamic reloading
        for gradio objects that'll be persistent with a data source function, and launches the Gradio interface.

        Args:
            **launch_kwargs: Keyword arguments to pass to the Gradio block launch method.
        """
        self.wrapped_instances = []
        for name in dir(self):
            inst = getattr(self, name)
            if isinstance(inst, Wrapper):
                self.wrapped_instances.append(inst)

        self.dyn_reloading_instances = [o for o in self.wrapped_instances if o._source]                
                
        with gr.Blocks(**self.init_args) as block:
            self.layout()
            self._init_listeners()
            if self.dyn_reloading_instances:
                block.load(self._load, outputs=[o.gr_object for o in self.dyn_reloading_instances])

        block.launch(**launch_kwargs)

    def _load(self):
        """
        Loads data from the data source for all gradio objects with a data source function assigned.
        
        This method is called when the Gradio interface is loaded or reloaded.
        """
        print("Reloading")
        outputs = [o._source() for o in self.dyn_reloading_instances]
        return outputs if len(outputs) > 1 else outputs[0]


    def _init_listeners(self):
        """
        Initializes event listeners for all instance attributes of type Wrapper.
        
        This method binds the event listeners defined in each `Wrapper` instance to the corresponding
        events in the Gradio widgets.
        """
        # traverse all instance attributes of type Wrapper
        for inst in self.wrapped_instances:
            for event, listeners in inst.listeners.items():
                event_fn = getattr(inst.gr_object, event)
                for listener in listeners:
                    # if listener has inputs, convert them to gradio objects
                    if "inputs" in listener:
                        listener["inputs"] = [inp.gr_object for inp in listener["inputs"]]
                    # if listener has outputs, convert them to gradio objects
                    if "outputs" in listener:
                        listener["outputs"] = [out.gr_object for out in listener["outputs"]]
                    l = event_fn(**listener)
                    event_fn = l.then

    def layout(self):
        """
        Abstract method to define the layout of the Gradio blocks.
        
        Must be implemented in the subclass to define the specific layout of the Gradio interface.
        
        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("layout_block method must be implemented in the subclass")

class Wrapper:
    """
    Wrapper class for Gradio widgets to manage event listeners.

    Args:
        gr_object_cls (class): The Gradio object class.
        **kwargs: Additional keyword arguments for widget initialization.
    """

    def __init__(self, gr_object_cls, **kwargs):
        self.gr_object_cls = gr_object_cls
        self.init_kwargs = kwargs
        self.listeners = {}
        self._source = None

    def bind_factory(self, name):
        """
        Creates a binding function for an event.

        Args:
            name (str): The name of the event.

        Returns:
            function: A function to bind the event to a handler.
        """
        def bind(**kwargs):
            self.listeners.setdefault(name,[]).append(kwargs)
        return bind

    def __call__(self):
        """
        Initializes the widget with the provided arguments.
        
        This method creates an instance of the Gradio widget using the provided initialization arguments.
        """
        self.gr_object = self.gr_object_cls(**self.init_kwargs)

    def __getattr__(self, name):
        """
        Overrides attribute access to bind events if they exist in the widget class.

        Args:
            name (str): The name of the attribute.

        Returns:
            function: The binding function for the event if it exists.
        """
        if name in self.gr_object_cls.EVENTS:
            return self.bind_factory(name)
        return super().__getattr__(name)
    
    def source(self, fn):
        """
        Sets the data source for the widget.

        Args:
            fn (function): The data source function.
        """
        self._source = fn

