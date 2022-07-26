# pylnlib : a package to communicate with a model railroad controller using the LocoNet® protocol
#
# (c) 2022 Michel Anders (varkenvarken)
#
# License: GPL 3, see file LICENSE
#
# Version: 20220726161758

from inspect import signature

from typing import Optional, Literal, Dict, Any


class Switch:
    switchstates = {None, "CLOSED", "THROWN"}

    def __init__(
        self, id: int, thrown:Optional[Literal["CLOSED", "THROWN"]] = None, engage: bool = None
    ):
        if thrown not in Switch.switchstates:
            raise ValueError(
                f"unknown switch state {thrown}, not one of {Switch.switchstates}"
            )
        self.id = id
        self.thrown: bool = thrown == "THROWN"
        self.engage = engage

    def toJSON(self) -> Dict[str, Any]:
        return {
            p: getattr(self, p)
            for p in signature(self.__init__).parameters  # type: ignore
            if p != "self"
        }

    def __str__(self) -> str:
        return f"Switch(address={self.id+1}, level={'THROWN' if self.thrown else 'CLOSED'}, engage={self.engage})"

    def __eq__(self, other: object) -> bool:
        return (
            type(other) == Switch
            and self.id == other.id
            and self.thrown == other.thrown
            and self.engage == other.engage
        )
