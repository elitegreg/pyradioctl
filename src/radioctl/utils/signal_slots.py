from weakref import *

import inspect


class Signal:
    __slots__ = ['slots', 'funchost']

    """
    class Signal

    A simple implementation of the Signal/Slot pattern. To use, simply
    create a Signal instance. The instance may be a member of a class,
    a global, or a local; it makes no difference what scope it resides
    within. Connect slots to the signal using the "connect()" method.
    The slot may be a member of a class or a simple function. If the
    slot is a member of a class, Signal will automatically detect when
    the method's class instance has been deleted and remove it from
    its list of connected slots.
    """
    def __init__(self):
        self.slots = []

        # for keeping references to _WeakMethod_FuncHost objects.
        # If we didn't, then the weak references would die for
        # non-method slots that we've created.
        self.funchost = []

    def __call__(self, *args, **kwargs):
        for (i, slot) in enumerate(self.slots):
            if slot != None:
                slot(*args, **kwargs)
            else:
                del self.slots[i]


    def call(self, *args, **kwargs):
        self.__call__(*args, **kwargs)

    def connect(self, slot):
        self.disconnect(slot)
        if inspect.ismethod(slot):
            self.slots.append(_WeakMethod(slot))
        else:
            o = _WeakMethod_FuncHost(slot)
            self.slots.append(_WeakMethod(o.func))
            # we stick a copy in here just to keep the instance alive
            self.funchost.append(o)

    def disconnect(self, slot):
        try:
            for i in range(len(self.slots)):
                wm = self.slots[i]
                if inspect.ismethod(slot):
                    if wm.f == slot.im_func and wm.c() == slot.im_self:
                        del self.slots[i]
                        return
                else:
                    if wm.c().hostedFunction == slot:
                        del self.slots[i]
                        return
        except:
            pass

    def disconnectAll(self):
        del self.slots[:]
        del self.funchost[:]


class _WeakMethod_FuncHost:
    __slots__ = ['hostedFunction']

    def __init__(self, func):
        self.hostedFunction = func

    def func(self, *args, **kwargs):
        self.hostedFunction(*args, **kwargs)


class _WeakMethod:
    __slots__ = ['f', 'c']

    def __init__(self, f):
        self.f = f.im_func
        self.c = ref(f.im_self)

    def __call__(self, *args, **kwargs):
        if self.c() == None :
            return
        self.f(self.c(), *args, **kwargs)
