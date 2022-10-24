class OrderWithRespectToMixin(object):
    def move(self, shift):
        parent_name = self._meta.order_with_respect_to.name
        class_name = type(self).__name__
        parent = getattr(self, parent_name)
        get_order = getattr(parent, "get_%s_order" % class_name.lower())
        set_order = getattr(parent, "set_%s_order" % class_name.lower())
        order = list(get_order())
        old = order.index(self.id)
        new = max(0, min(old + int(shift), len(order) - 1))
        order.insert(new, order.pop(old))
        set_order(order)
        parent.save()
