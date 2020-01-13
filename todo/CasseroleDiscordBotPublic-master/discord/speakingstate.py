# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2019 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

class SpeakingState:
    """Wraps up the Discord speaking state value.

    This object is similar to a :class:`Permissions` object with reduced
    functionality. You can set and retrieve individual bits using the
    properties as if they were regular bools. Only a subset of the operators
    :class:`Permissions` implements are available.

    .. container:: operations

        .. describe:: x == y

            Checks if two speaking states are equal.
        .. describe:: x != y

            Checks if two speaking states are not equal.
        .. describe:: hash(x)

            Returns the speaking state's hash.
        .. describe:: int(x)

            Returns the raw integer value of the speaking state.

    Attributes
    -----------
    value
        The raw value. This value is a bit array field of a 3 bit integer
        representing the current speaking state. You should query the state
        via the properties rather than using this raw value.
    """

    __slots__ = ('value',)
    def __init__(self, state):
        if not isinstance(state, int):
            raise TypeError('Expected int parameter, received %s instead.' % state.__class__.__name__)

        self.value = state

    def __eq__(self, other):
        return isinstance(other, SpeakingState) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __int__(self):
        return self.value

    def __repr__(self):
        return '<SpeakingState value=%s>' % self.value

    @classmethod
    def inactive(cls):
        """A factory method that creates a :class:`SpeakingState` that
        indicates the user is not speaking."""
        return cls(0b000)

    @classmethod
    def active(cls, *, priority=False):
        """A factory method that creates a :class:`SpeakingState` that
        indicates the user is speaking.

        Parameters
        -----------
            priority: blah
        """
        return cls(0b101 if priority else 0b001)

    def _bit(self, index):
        return bool((self.value >> index) & 1)

    def _set(self, index, value):
        if value is True:
            self.value |= (1 << index)
        elif value is False:
            self.value &= ~(1 << index)
        else:
            raise TypeError('Value to set for SpeakingState must be a bool.')

    @property
    def speaking(self):
        """Returns True if the user is speaking."""
        return self._bit(0)

    @speaking.setter
    def speaking(self, value):
        self._set(0, value)

    @property
    def soundshare(self):
        """Returns True is the user is using shoundshare.""" # TODO: nitpick wording
        return self._bit(1)

    @soundshare.setter
    def soundshare(self, value):
        self._set(1, value)

    @property
    def priority(self):
        """Returns True if the user has priority voice mode enabled."""
        return self._bit(2)

    @priority.setter
    def priority(self):
        self._set(2, value)
