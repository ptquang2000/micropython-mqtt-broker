class Topic():
    def __init__(self, parent=None, children={}):
        self._name = None
        self._app_msg = None
        self._parent = parent
        self._children = children


    def __getitem__(self, topic_name):
        topic_levels = self.separator(topic_name)
        if not topic_levels[1:] and topic_levels[0] == self._name:
            return self._app_msg
        if topic_levels[0] in self._children:
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]


    def __setitem__(self, topic_name, app_msg):
        topic_levels = self.separator(topic_name)
        if not self._name and self._parent:
            self._name = topic_levels[0]
        
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(parent=self)
            self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = app_msg
        else:
            self._app_msg = app_msg


    @staticmethod
    def separator(topic_name):
        levels = topic_name.split(b'/')
        if topic_name[0] == b'/':
            levels[0] = b'/' + levels[0]
        if topic_name[-1] == b'/':
            levels[-1] = b'/' + levels[-1]
        return levels
            