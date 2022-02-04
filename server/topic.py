class Topic():
    def __init__(self, parent=None, children={}):
        self._name = None
        self._app_msg = None
        self._qos_level = '00'
        self._subscription = []
        self._parent = parent
        self._children = children


    @property
    def qos_level(self):
        return self._qos_level


    @property
    def application_message(self):
        return self._app_msg


    @property
    def subscription(self):
        return self._subscription
        
    
    @subscription.setter
    def subscription(self, id):
        return self._subscription.append(id)
        

    def __getitem__(self, topic_filter):
        topic_levels = self.separator(topic_filter)
        if not topic_levels[1:] and topic_levels[0] == self._name:
            return self
        if topic_levels[0] in self._children:
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]


    def __setitem__(self, topic_name, packet):
        topic_levels = self.separator(topic_name)
        if not self._name and self._parent:
            self._name = topic_levels[0]
        
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(parent=self)
            self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = packet
        else:
            self._app_msg = packet.application_message
            self._qos_level = packet.qos_level


    @staticmethod
    def separator(topic):
        levels = topic.split(b'/')
        if topic[0] == b'/':
            levels[0] = b'/' + levels[0]
        if topic[-1] == b'/':
            levels[-1] = b'/' + levels[-1]
        return levels