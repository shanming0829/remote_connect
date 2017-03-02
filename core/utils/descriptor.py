import re
import weakref


class Descriptor(object):
    def __init__(self, default=None):
        self.name = None
        self.default = default
        self.data = weakref.WeakKeyDictionary()
        self.callbacks = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        for callback in self.callbacks.get(instance, []):
            callback(instance, self.name, value)
        self.data[instance] = value

    def add_callback(self, instance, callback):
        if instance not in self.callbacks:
            self.callbacks[instance] = []
        self.callbacks[instance].append(callback)


class DescriptorType(type):
    @staticmethod
    def __new__(cls, name, bases, attrs):
        for n, v in attrs.items():
            if isinstance(v, Descriptor):
                v.name = n
        return super(DescriptorType, cls).__new__(cls, name, bases, attrs)


class NumberDescriptor(Descriptor):
    def __set__(self, instance, value):
        type_check(value, (int, float))
        super(NumberDescriptor, self).__set__(instance, value)


class StringDescriptor(Descriptor):
    def __set__(self, instance, value):
        type_check(value, basestring)
        super(StringDescriptor, self).__set__(instance, value)


class CompileDescriptor(Descriptor):
    def __set__(self, instance, value):
        if isinstance(value, basestring):
            rel_value = re.compile(value)
        elif isinstance(value, re._pattern_type):
            rel_value = value
        else:
            raise TypeError("Not support the compile type -> {}.".format(value))

        super(CompileDescriptor, self).__set__(instance, rel_value)


class ListDescriptor(Descriptor):
    def __set__(self, instance, value):
        type_check(value, (list, tuple))
        super(ListDescriptor, self).__set__(instance, value)


class BooleanDescriptor(Descriptor):
    def __set__(self, instance, value):
        super(BooleanDescriptor, self).__set__(instance, bool(value))


def type_check(inst, check_type):
    if not isinstance(inst, check_type):
        raise TypeError("Value must be {} type".format(str(check_type)))
