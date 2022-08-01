# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220801133939

from inspect import signature


class Switch:
    """
    Represents a switch state.

    Args:
        id (int): The switch address.
        thrown: The switch state, one of {None, "CLOSED", "THROWN"}.
        engage (bool): Whether the switch motor is engaged.
    Raises:
        ValueError: if the state is an unknown literal and not None.
    """

    switchstates = {None, "CLOSED", "THROWN"}

    def __init__(
        self,
        id,
        thrown=None,
        engage=None,
    ):
        if thrown not in Switch.switchstates:
            raise ValueError(
                f"unknown switch state {thrown}, not one of {Switch.switchstates}"
            )
        self.id = id
        self.thrown: bool = thrown == "THROWN"
        self.engage = engage

    def toJSON(self):
        """
        Returns an object suitable for serialiazing as JSON.

        Returns:
            dict: A dictionary with the object attributes.
        """
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters
            if p != "self"
        }

    def __str__(self):
        """
        Returns a string representation of a Switch object.

        !!! note
            The address shown is 1 larger than the actual address as is customary. (The address is indeed offset 0, but modellers are not accustomed to that)

        Returns:
            str: the string representation of a Switch object with its state and address.
        """
        return f"Switch(address={self.id+1}, level={'THROWN' if self.thrown else 'CLOSED'}, engage={self.engage})"

    def __eq__(self, other: object) -> bool:
        """
        Compares a Switch object to another object.

        Args:
            other (object): any other object

        Returns:
            bool: True if switch address, thrown and engage are the same
        """
        return (
            type(other) == Switch
            and self.id == other.id
            and self.thrown == other.thrown
            and self.engage == other.engage
        )
