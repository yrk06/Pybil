class Node:
    def __init__(self,type,value,children=[]):
        self.type = type
        self.value = value
        self.children = [x for x in children]
    def add_child(self,child):
        self.children.append(child)
    def add_child_idx(self,child,idx):
        self.children.insert(idx,child)
    def export(self):
        return {
            'type':self.type,
            'value': self.value,
            'children': [x for x in map(lambda a: a.export(),self.children)]
        }